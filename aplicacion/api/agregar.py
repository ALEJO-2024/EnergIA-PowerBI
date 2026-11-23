"""Arma el resumen del tablero a partir de los CSV de datos finales."""

import csv
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "datos finales"
DESTINO = Path(__file__).resolve().parent / "resumen.json"
CODIGO = "05001"


def entero(texto):
    limpio = (texto or "").strip()
    if limpio in ("", "ND"):
        return 0
    return int(float(limpio))


def decimal(texto):
    limpio = (texto or "").strip()
    if limpio == "":
        return 0.0
    return float(limpio)


def clientes():
    tabla = {}
    with (DATOS / "cliente.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["cod_divipola"] != CODIGO:
                continue
            estrato = fila["estrato"].strip()
            tabla[fila["cliente_id"]] = {
                "tipo": fila["tipo_cliente"],
                "estrato": int(estrato) if estrato else None,
            }
    return tabla


def consumo(tabla):
    por_tipo = defaultdict(float)
    por_estrato = defaultdict(float)
    perfil = defaultdict(lambda: [0.0, 0])
    total = 0.0
    with (DATOS / "consumo.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            persona = tabla.get(fila["cliente_id"])
            if persona is None:
                continue
            kwh = float(fila["consumo_kwh"])
            marca = fila["fecha_hora"]
            periodo = marca[:7]
            hora = int(marca[11:13])
            total += kwh
            por_tipo[(periodo, persona["tipo"])] += kwh
            if persona["estrato"] is not None:
                por_estrato[(periodo, persona["estrato"])] += kwh
            celda = perfil[(periodo, persona["tipo"], hora)]
            celda[0] += kwh
            celda[1] += 1
    return total, por_tipo, por_estrato, perfil


def facturas(tabla):
    por_mes = {}
    por_tipo = defaultdict(lambda: {"valor": 0.0, "kwh": 0.0})
    with (DATOS / "factura.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["cliente_id"] not in tabla:
                continue
            periodo = fila["periodo"]
            valor = float(fila["valor_facturado"])
            kwh = float(fila["consumo_kwh_mes"])
            tarifa = float(fila["tarifa"])
            estado = fila["estado_pago"]
            cubo = por_mes.setdefault(periodo, {
                "valor": 0.0, "kwh": 0.0, "tarifa_kwh": 0.0,
                "pagada": 0, "pendiente": 0, "en mora": 0, "facturas": 0,
            })
            cubo["valor"] += valor
            cubo["kwh"] += kwh
            cubo["tarifa_kwh"] += tarifa * kwh
            cubo[estado] += 1
            cubo["facturas"] += 1
            tipo = tabla[fila["cliente_id"]]["tipo"]
            por_tipo[(periodo, tipo)]["valor"] += valor
            por_tipo[(periodo, tipo)]["kwh"] += kwh
    return por_mes, por_tipo


def activos():
    tabla = {}
    with (DATOS / "activo.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["cod_divipola"] != CODIGO:
                continue
            tabla[fila["infraestructura_id"]] = {
                "tipo": fila["tipo"],
                "lat": float(fila["latitud"]),
                "lon": float(fila["longitud"]),
                "instalacion": fila["fecha_instalacion"],
                "edad": 2021 - int(fila["fecha_instalacion"][:4]),
                "estado": fila["estado"],
            }
    return tabla


def fallas(equipos):
    filas = []
    with (DATOS / "falla.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            equipo = equipos.get(fila["infraestructura_id"])
            if equipo is None:
                continue
            filas.append({
                "id": fila["incidente_id"],
                "activo": fila["infraestructura_id"],
                "tipo": equipo["tipo"],
                "lat": equipo["lat"],
                "lon": equipo["lon"],
                "cuando": fila["fecha_hora"],
                "periodo": fila["fecha_hora"][:7],
                "afectados": entero(fila["clientes_afectados"]),
                "minutos": entero(fila["duracion_minutos"]),
                "edad": equipo["edad"],
                "estado": equipo["estado"],
            })
    return filas


def mantenimientos(equipos):
    filas = []
    with (DATOS / "mantenimiento.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["infraestructura_id"] not in equipos:
                continue
            filas.append({
                "activo": fila["infraestructura_id"],
                "fecha": fila["fecha"],
                "periodo": fila["fecha"][:7],
                "tipo": fila["tipo"],
                "costo": entero(fila["costo"]),
            })
    return filas


def lluvia_por_mes():
    por_mes = defaultdict(float)
    with (DATOS / "clima.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["cod_divipola"] != CODIGO:
                continue
            por_mes[fila["fecha_hora"][:7]] += decimal(fila["precipitacion_mm"])
    return por_mes


def poblacion():
    areas = {}
    with (DATOS / "poblacion.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["cod_divipola"] == CODIGO and fila["anio"] == "2021":
                areas[fila["area"]] = entero(fila["habitantes"])
    return {
        "total": areas["Total"],
        "cabecera": areas["Cabecera Municipal"],
        "resto": areas["Centros Poblados y Rural Disperso"],
    }


def sui():
    with (DATOS / "sui.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["cod_divipola"] == CODIGO and fila["ubicacion"] == "Total" and fila["periodo"] == "25":
                estratos = [{"estrato": i, "usuarios": entero(fila[f"estrato_{i}"])} for i in range(1, 7)]
                otros = [
                    {"tipo": "Industrial", "usuarios": entero(fila["industrial"])},
                    {"tipo": "Comercial", "usuarios": entero(fila["comercial"])},
                    {"tipo": "Oficial", "usuarios": entero(fila["oficial"])},
                    {"tipo": "Otros", "usuarios": entero(fila["otros"])},
                ]
                return {
                    "suscriptores": entero(fila["total_residencial"]) + entero(fila["total_no_residencial"]),
                    "estratos": estratos,
                    "otros": otros,
                }
    raise SystemExit("No está Medellín en sui.csv")


def tarifa():
    serie = {}
    with (DATOS / "tarifa.csv").open(encoding="utf-8-sig", newline="") as archivo:
        for fila in csv.DictReader(archivo):
            if fila["anio"] != "2021":
                continue
            serie[int(fila["mes"])] = round(decimal(fila["precio_propiedad_epm"]), 2)
    if len(serie) != 12:
        raise SystemExit("Faltan meses de la tarifa en tarifa.csv")
    return [{"mes": mes, "precio": serie[mes]} for mes in range(1, 13)]


def redondear(valor, decimales):
    return round(valor, decimales)


def construir():
    import json

    print("Leyendo clientes y consumo de datos finales...")
    tabla = clientes()
    total_kwh, por_tipo, por_estrato, perfil = consumo(tabla)
    print("Leyendo facturas, fallas y contexto...")
    por_mes_factura, factura_tipo = facturas(tabla)
    equipos = activos()
    eventos = fallas(equipos)
    trabajos = mantenimientos(equipos)
    lluvia = lluvia_por_mes()
    habitantes = poblacion()
    sector = sui()
    precios = tarifa()

    periodos = [f"2021-{mes:02d}" for mes in range(1, 13)]
    tipos = ["Residencial", "Industrial", "Comercial", "Oficial", "Otros"]

    resumen = {
        "corte": {
            "municipio": "Medellín",
            "codigo": "05001",
            "anio": 2021,
            "clientes": len(tabla),
            "activos": len(equipos),
            "suscriptores_publicados": sector["suscriptores"],
        },
        "periodos": periodos,
        "consumo": {
            "total_kwh": redondear(total_kwh, 1),
            "por_tipo": [
                {"periodo": periodo, "tipo": tipo, "kwh": redondear(por_tipo[(periodo, tipo)], 1)}
                for periodo in periodos for tipo in tipos
            ],
            "por_estrato": [
                {"periodo": periodo, "estrato": estrato, "kwh": redondear(kwh, 1)}
                for (periodo, estrato), kwh in sorted(por_estrato.items())
            ],
            "por_hora": [
                {
                    "periodo": periodo,
                    "tipo": tipo,
                    "hora": hora,
                    "kwh": redondear(perfil[(periodo, tipo, hora)][0], 1),
                    "n": perfil[(periodo, tipo, hora)][1],
                }
                for periodo in periodos for tipo in tipos for hora in range(24)
            ],
        },
        "factura": {
            "por_mes": [
                {
                    "periodo": periodo,
                    "valor": redondear(por_mes_factura[periodo]["valor"], 2),
                    "kwh": redondear(por_mes_factura[periodo]["kwh"], 1),
                    "tarifa": redondear(
                        por_mes_factura[periodo]["tarifa_kwh"] / por_mes_factura[periodo]["kwh"], 2
                    ),
                    "pagada": por_mes_factura[periodo]["pagada"],
                    "pendiente": por_mes_factura[periodo]["pendiente"],
                    "mora": por_mes_factura[periodo]["en mora"],
                }
                for periodo in periodos
            ],
            "por_tipo": [
                {
                    "periodo": periodo,
                    "tipo": tipo,
                    "valor": redondear(factura_tipo[(periodo, tipo)]["valor"], 2),
                    "kwh": redondear(factura_tipo[(periodo, tipo)]["kwh"], 1),
                }
                for periodo in periodos for tipo in tipos
            ],
        },
        "fallas": eventos,
        "lluvia": [{"periodo": periodo, "mm": redondear(lluvia[periodo], 1)} for periodo in periodos],
        "equipos": [
            {
                "id": codigo,
                "tipo": equipo["tipo"],
                "lat": equipo["lat"],
                "lon": equipo["lon"],
                "edad": equipo["edad"],
                "estado": equipo["estado"],
            }
            for codigo, equipo in equipos.items()
        ],
        "mantenimiento": trabajos,
        "contexto": {
            "habitantes": habitantes,
            "sui": sector,
            "tarifa": precios,
        },
    }
    DESTINO.write_text(json.dumps(resumen, ensure_ascii=False), encoding="utf-8")
    print(f"Listo: {DESTINO}")
    print(f"kWh {resumen['consumo']['total_kwh']} fallas {len(eventos)} suscriptores {sector['suscriptores']}")


if __name__ == "__main__":
    construir()
