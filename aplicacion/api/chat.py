"""Consulta de negocio. Lee la base en solo lectura y no sale del proyecto."""

import json
import os
import re
import urllib.error
import urllib.request
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

AQUI = Path(__file__).resolve().parent
ENV = AQUI / ".env"
URL_BASE = "postgresql://makaia:makaia@127.0.0.1:5432/makaia"

router = APIRouter()

RECHAZO = "Solo puedo responder sobre el servicio eléctrico de Medellín en 2021 que muestra este tablero."

TABLAS = {
    "geografia",
    "tiempo",
    "cliente",
    "activo",
    "clima",
    "consumo",
    "factura",
    "falla",
    "mantenimiento",
    "poblacion",
    "sui",
    "tarifa",
}

PROHIBIDO = re.compile(
    r"\b(insert|update|delete|drop|alter|create|grant|revoke|copy|truncate|vacuum|"
    r"execute|call|do|set|reset|listen|notify|load|lock|reindex|cluster|discard|"
    r"prepare|deallocate|refresh|merge|into|pg_sleep|pg_read_file|pg_ls_dir|"
    r"lo_import|lo_export|dblink|pg_catalog|information_schema)\b",
    re.I,
)

ESQUEMA = """
Base PostgreSQL, esquema makaia. El año operativo es 2021 y el grano fino es Medellín, cod_divipola '05001'.
Hay 125 municipios en geografia, pero clientes, activos, clima y población de este corte son de Medellín.

geografia(cod_divipola, nombre, departamento, tipo_municipio, latitud, longitud)
tiempo(fecha_hora, fecha, hora, mes, anio, periodo)  -- una fila por hora; periodo es '2021-01'
cliente(cliente_id, cod_divipola, tipo_cliente, estrato, estado)  -- estrato vacío si no es residencial. Muestra de 1.000, no los suscriptores del SUI.
activo(infraestructura_id, cod_divipola, tipo, latitud, longitud, fecha_instalacion, estado)
clima(cod_divipola, fecha_hora, precipitacion_mm, temperatura_2m, humedad_relativa, viento_kmh, presion_hpa)
consumo(cliente_id, fecha_hora, consumo_kwh)  -- millones de filas horarias. Siempre agrupa. No la listes.
factura(cliente_id, periodo, consumo_kwh_mes, valor_facturado, tarifa, estado_pago)  -- una cuenta por cliente y mes. estado_pago: pagada, pendiente, en mora. consumo_kwh_mes ya es la suma de las horas: no lo sumes con consumo.
falla(incidente_id, infraestructura_id, fecha_hora, clientes_afectados, duracion_minutos)  -- no tiene lluvia ni gravedad.
mantenimiento(mantenimiento_id, infraestructura_id, fecha, tipo, costo)  -- fecha es un día, no una hora.
poblacion(cod_divipola, anio, area, habitantes)  -- áreas: 'Total', 'Cabecera Municipal', 'Centros Poblados y Rural Disperso'. Total ya incluye las otras dos.
sui(cod_divipola, anio, periodo, ubicacion, empresa, estrato_1..estrato_6, total_residencial, industrial, comercial, oficial, otros, total_no_residencial)  -- Medellín anual: cod_divipola '05001', periodo 25, ubicacion 'Total'. No sumes los otros municipios salvo que pregunten por Antioquia.
tarifa(anio, mes, tipo_informacion, tipo_tarifa, tipo_dato, rango_consumo, nivel, precio_propiedad_epm, precio_compartido, precio_propiedad_cliente, precio_punta, precio_fuera_punta)  -- no tiene municipio. El precio de estrato 1 es precio_propiedad_epm.

Uniones válidas: cliente con consumo y factura por cliente_id; activo con falla y mantenimiento por infraestructura_id; tiempo con consumo, clima y falla por fecha_hora. No unas mantenimiento con tiempo. No unas clima con falla fila a fila: si comparas lluvia y fallas, agrupa cada una por periodo.
""".strip()

PLAN = """Eres el analista de EnergIA. Decides cómo leer la base para una pregunta de directivos.
Devuelve solo un JSON, sin markdown y sin texto alrededor.
{"accion":"rechazar"} si la pregunta no es del servicio eléctrico de Medellín en 2021 de este proyecto.
{"accion":"reglas"} si pregunta cómo se leen las cifras y no pide un número nuevo.
{"accion":"consultar","sql":"SELECT ..."} si hace falta un dato de la base.

El SQL es un solo SELECT o WITH, sin punto y coma, solo con las tablas del esquema.
Si piden las peores fallas, los peores cortes o algo parecido, no existe gravedad: ordena por clientes_afectados y duracion_minutos.
Si la frase es coloquial, tradúcela al dato que sí existe. No inventes columnas.
"""

RESPUESTA = """Eres el analista de EnergIA para directivos. Respondes en español de Colombia, con frases cortas.
Usa solo el resultado de la base y las reglas. No inventes cifras. Si el resultado no trae el dato, dilo.
No menciones SQL ni nombres de tablas.
Si el resultado ordena fallas por clientes alcanzados o por minutos, explica que no hay una gravedad guardada y que "peor" aquí significa más clientes o más minutos.
Reglas:
- El kWh de la factura ya es la suma de las horas. No se vuelve a sumar al medidor.
- La muestra tiene 1.000 clientes. No son los suscriptores del SUI.
- La población Total ya incluye cabecera y resto.
- La lluvia no va copiada en cada falla.
- El SUI, el DANE y la tarifa publicada no identifican a un cliente ni a un equipo de la muestra.
- El periodo 25 del SUI es el año completo.
"""


class Mensaje(BaseModel):
    rol: str
    texto: str = Field(max_length=1500)


class Consulta(BaseModel):
    mensajes: list[Mensaje] = Field(min_length=1, max_length=8)


class ConsultaSql(Exception):
    pass


def configuracion() -> tuple[str, str]:
    valores = {
        "RESCUEAI_BASE_URL": os.environ.get("RESCUEAI_BASE_URL", "https://llm.tirescue.com/v1"),
        "RESCUEAI_API_KEY": os.environ.get("RESCUEAI_API_KEY", ""),
    }
    if ENV.exists():
        for linea in ENV.read_text(encoding="utf-8").splitlines():
            limpia = linea.strip()
            if not limpia or limpia.startswith("#") or "=" not in limpia:
                continue
            clave, valor = limpia.split("=", 1)
            clave = clave.strip()
            if clave in valores:
                valores[clave] = valor.strip().strip('"').strip("'")
    return valores["RESCUEAI_BASE_URL"].rstrip("/"), valores["RESCUEAI_API_KEY"].strip()


def completar(historial: list[dict], modelo: str = "rescue-main", temperatura: float = 0.2, tope: int = 700) -> str:
    base, clave = configuracion()
    if not clave or clave.endswith("..."):
        raise HTTPException(status_code=503, detail="Falta la llave virtual de RescueAI en aplicacion/api/.env.")
    cuerpo = json.dumps(
        {"model": modelo, "temperature": temperatura, "max_tokens": tope, "messages": historial}
    ).encode("utf-8")
    pedido = urllib.request.Request(
        base + "/chat/completions",
        data=cuerpo,
        headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(pedido, timeout=120) as respuesta:
            data = json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise HTTPException(status_code=429, detail="RescueAI está en el límite de uso. Intenta de nuevo en un momento.") from exc
        raise HTTPException(status_code=502, detail="RescueAI no pudo responder esta consulta.") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise HTTPException(status_code=502, detail="No hubo respuesta de RescueAI.") from exc
    try:
        texto = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="RescueAI devolvió una respuesta vacía.") from exc
    if not isinstance(texto, str) or not texto.strip():
        raise HTTPException(status_code=502, detail="RescueAI devolvió una respuesta vacía.")
    return texto.strip()


def extraer_json(texto: str) -> dict:
    limpio = texto.strip()
    if limpio.startswith("```"):
        limpio = re.sub(r"^```(?:json)?", "", limpio).strip()
        limpio = re.sub(r"```$", "", limpio).strip()
    inicio = limpio.find("{")
    fin = limpio.rfind("}")
    if inicio < 0 or fin <= inicio:
        raise ConsultaSql("La consulta no vino en JSON.")
    try:
        dato = json.loads(limpio[inicio : fin + 1])
    except json.JSONDecodeError as exc:
        raise ConsultaSql("La consulta no vino en JSON.") from exc
    if not isinstance(dato, dict):
        raise ConsultaSql("La consulta no vino en JSON.")
    return dato


def validar_sql(sql: str) -> str:
    limpio = sql.strip().rstrip(";").strip()
    if not limpio or ";" in limpio or "--" in limpio or "/*" in limpio:
        raise ConsultaSql("La consulta tiene que ser un solo SELECT.")
    if not re.match(r"(?is)^(select|with)\b", limpio):
        raise ConsultaSql("La consulta tiene que ser un solo SELECT.")
    if PROHIBIDO.search(limpio):
        raise ConsultaSql("Esa consulta no está permitida.")
    ctes = {nombre.lower() for nombre in re.findall(r"(?i)\b([a-zA-Z_][\w]*)\s+as\s*\(", limpio)}
    for origen in re.findall(r"(?i)\b(?:from|join)\s+([a-zA-Z_][\w\.]*)", limpio):
        partes = origen.split(".")
        if len(partes) == 2 and partes[0].lower() != "makaia":
            raise ConsultaSql("Solo se puede leer el esquema makaia.")
        tabla = partes[-1].lower()
        if tabla not in TABLAS and tabla not in ctes:
            raise ConsultaSql("Esa tabla no hace parte del proyecto.")
    return limpio


def texto_celda(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%d %H:%M")
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return format(valor, "f")
    return str(valor)


def ejecutar(sql: str) -> str:
    try:
        import psycopg
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Falta el controlador de PostgreSQL.") from exc
    consulta = validar_sql(sql)
    try:
        with psycopg.connect(URL_BASE, connect_timeout=5) as conexion:
            conexion.execute("SET default_transaction_read_only = on")
            conexion.execute("SET statement_timeout = '12s'")
            conexion.execute("SET search_path TO makaia")
            cursor = conexion.execute(consulta)
            columnas = [columna.name for columna in cursor.description] if cursor.description else []
            filas = cursor.fetchmany(40)
    except ConsultaSql:
        raise
    except Exception as exc:
        mensaje = str(exc).splitlines()[0]
        bajada = mensaje.lower()
        if "could not connect" in bajada or "connection refused" in bajada or "failed to connect" in bajada or "connection timeout" in bajada:
            raise HTTPException(
                status_code=503,
                detail="La base de datos no está encendida. Abre Docker y el contenedor makaia-postgres.",
            ) from exc
        raise ConsultaSql(mensaje[:240]) from exc
    if not columnas:
        return "La consulta no devolvió filas."
    linea = " | ".join(columnas)
    cuerpo = [" | ".join(texto_celda(valor) for valor in fila) for fila in filas]
    aviso = ""
    if len(filas) == 40:
        aviso = "\nSe muestran las primeras 40 filas."
    if not cuerpo:
        return "La consulta no devolvió filas."
    return linea + "\n" + "\n".join(cuerpo) + aviso


def base_disponible() -> None:
    try:
        import psycopg
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Falta el controlador de PostgreSQL.") from exc
    try:
        with psycopg.connect(URL_BASE, connect_timeout=5) as conexion:
            conexion.execute("SELECT 1")
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="La base de datos no está encendida. Abre Docker y el contenedor makaia-postgres.",
        ) from exc


def conversacion(mensajes: list[Mensaje]) -> list[dict]:
    return [
        {"role": "user" if mensaje.rol == "usuario" else "assistant", "content": mensaje.texto.strip()}
        for mensaje in mensajes
    ]


def planear(mensajes: list[Mensaje], error: str = "") -> dict:
    aviso = f"\nLa consulta anterior falló: {error}. Corrígela." if error else ""
    mensajes_plan = [
        {"role": "system", "content": PLAN + "\n" + ESQUEMA + aviso},
        *conversacion(mensajes),
    ]
    try:
        texto = completar(mensajes_plan, modelo="rescue-reason", temperatura=0.1, tope=500)
    except HTTPException as exc:
        if exc.status_code != 502:
            raise
        texto = completar(mensajes_plan, modelo="rescue-main", temperatura=0.1, tope=500)
    return extraer_json(texto)


def redactar(mensajes: list[Mensaje], resultado: str) -> str:
    return completar(
        [
            {"role": "system", "content": RESPUESTA},
            *conversacion(mensajes),
            {"role": "user", "content": "Resultado de la base, úsalo como única fuente de cifras:\n" + resultado},
        ]
    )


@router.post("/api/chat")
def consultar(consulta: Consulta):
    utiles = [mensaje for mensaje in consulta.mensajes if mensaje.rol in ("usuario", "asistente") and mensaje.texto.strip()]
    if not utiles or utiles[-1].rol != "usuario":
        raise HTTPException(status_code=400, detail="La consulta tiene que terminar en una pregunta.")
    base_disponible()
    try:
        plan = planear(utiles)
    except ConsultaSql:
        try:
            plan = planear(utiles, "Devuelve solo el JSON pedido.")
        except ConsultaSql:
            return {"respuesta": "No pude leer ese dato en la base."}
    accion = plan.get("accion")
    if accion == "rechazar":
        return {"respuesta": RECHAZO}
    if accion == "reglas":
        return {"respuesta": redactar(utiles, "No hace falta una cifra nueva. Explica solo la regla de lectura.")}
    if accion != "consultar" or not isinstance(plan.get("sql"), str):
        return {"respuesta": RECHAZO}
    try:
        resultado = ejecutar(plan["sql"])
    except ConsultaSql as exc:
        try:
            corregido = planear(utiles, str(exc))
            if corregido.get("accion") != "consultar" or not isinstance(corregido.get("sql"), str):
                return {"respuesta": "No pude leer ese dato en la base."}
            resultado = ejecutar(corregido["sql"])
        except ConsultaSql:
            return {"respuesta": "No pude leer ese dato en la base."}
    return {"respuesta": redactar(utiles, resultado)}
