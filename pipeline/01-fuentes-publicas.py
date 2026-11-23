"""Limpia las fuentes públicas del corte y las deja en datos-reportes/modelo.

No une lluvia con fallas, ni suscriptores con clientes, ni tarifa con municipio.
"""

import json

import pandas as pd

from comunes import codigo, decimal_coma, guardar, numero_o_vacio, precio_cop, sin_tilde
from rutas import ANIO, CODIGO, MODELO, MUESTRAS

MESES = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12,
}


def geografia():
    tabla = pd.read_csv(MUESTRAS / "divipola-codigos-municipios-20261007.csv", dtype=str)
    tabla = tabla.rename(columns={
        "Código Departamento": "cod_departamento",
        "Nombre Departamento": "departamento",
        "Código Municipio": "cod_divipola",
        "Nombre Municipio": "nombre",
        "Tipo: Municipio / Isla / Área no municipalizada": "tipo_municipio",
        "longitud": "longitud",
        "Latitud": "latitud",
    })
    tabla["cod_divipola"] = codigo(tabla["cod_divipola"])
    tabla["cod_departamento"] = codigo(tabla["cod_departamento"])
    tabla["longitud"] = decimal_coma(tabla["longitud"])
    tabla["latitud"] = decimal_coma(tabla["latitud"])
    antioquia = tabla[tabla["cod_departamento"] == "00005"].copy()
    # zfill de un departamento de 2 dígitos lo deja en 5. Se conserva el código real de 2.
    antioquia["cod_departamento"] = "05"
    if antioquia["cod_divipola"].duplicated().any() or antioquia[["latitud", "longitud"]].isna().any().any():
        raise SystemExit("La geografía de Antioquia quedó con códigos repetidos o coordenadas vacías")
    if not (antioquia["cod_divipola"] == CODIGO).any():
        raise SystemExit("Medellín no quedó en la geografía")
    guardar(antioquia, MODELO / "geografia.csv")
    return antioquia


def clima():
    crudo = json.loads((MUESTRAS / "open-meteo-medellin-2021.json").read_text(encoding="utf-8"))
    tabla = pd.DataFrame(crudo["hourly"])
    tabla["fecha_hora"] = pd.to_datetime(tabla["time"])
    tabla["cod_divipola"] = CODIGO
    tabla = tabla.rename(columns={
        "temperature_2m": "temperatura_2m",
        "precipitation": "precipitacion_mm",
        "relative_humidity_2m": "humedad_relativa",
        "wind_speed_10m": "viento_kmh",
        "surface_pressure": "presion_hpa",
    })
    columnas = [
        "cod_divipola", "fecha_hora", "precipitacion_mm", "temperatura_2m",
        "humedad_relativa", "viento_kmh", "presion_hpa",
    ]
    tabla = tabla[columnas].sort_values("fecha_hora")
    if len(tabla) != 8760 or tabla["fecha_hora"].duplicated().any() or tabla.isna().any().any():
        raise SystemExit("El clima de 2021 no está completo")
    tabla["fecha_hora"] = tabla["fecha_hora"].dt.strftime("%Y-%m-%d %H:%M")
    guardar(tabla, MODELO / "clima.csv")
    return tabla


def poblacion(geo):
    tabla = pd.read_excel(
        MUESTRAS / "dane-poblacion-municipal-2018-2042.xlsx",
        sheet_name="PobMunicipalxÁrea",
        header=7,
        dtype={"MPIO": str, "DP": str},
    )
    tabla = tabla.dropna(subset=["MPIO"]).copy()
    tabla["cod_divipola"] = codigo(tabla["MPIO"])
    tabla["anio"] = pd.to_numeric(tabla["AÑO"], errors="coerce").astype("Int64")
    tabla["area"] = tabla["ÁREA GEOGRÁFICA"].str.strip()
    tabla["habitantes"] = pd.to_numeric(tabla["TOTAL"], errors="coerce").astype("Int64")
    corte = tabla[(tabla["cod_divipola"] == CODIGO) & (tabla["anio"] == ANIO)].copy()
    corte = corte[["cod_divipola", "anio", "area", "habitantes"]]
    corte["incluido_en_total"] = corte["area"] != "Total"
    if len(corte) != 3:
        raise SystemExit("Medellín 2021 no tiene las tres áreas de población")
    total = int(corte.loc[corte["area"] == "Total", "habitantes"].iloc[0])
    partes = int(corte.loc[corte["incluido_en_total"], "habitantes"].sum())
    if total != partes:
        raise SystemExit("La población Total de Medellín no cuadra con cabecera más resto")
    if CODIGO not in set(geo["cod_divipola"]):
        raise SystemExit("La población no encuentra a Medellín en la geografía")
    guardar(corte, MODELO / "poblacion.csv")
    return corte


def sui(geo):
    tabla = pd.read_csv(MUESTRAS / "sui-epm-antioquia-2021-suscriptores.csv", encoding="cp1252", dtype=str)
    tabla = tabla[tabla["Departamento"] == "ANTIOQUIA"].copy()
    puente = geo[["cod_divipola", "nombre"]].copy()
    puente["nombre_clave"] = puente["nombre"].map(sin_tilde)
    tabla["nombre_clave"] = tabla["Municipio"].map(sin_tilde)
    tabla = tabla.merge(puente, on="nombre_clave", how="left")
    numeros = [
        "Estrato 1", "Estrato 2", "Estrato 3", "Estrato 4", "Estrato 5", "Estrato 6",
        "Total Residencial", "Industrial", "Comercial", "Oficial", "Otros", "Total No Residencial",
    ]
    for columna in numeros:
        tabla[columna] = numero_o_vacio(tabla[columna])
    limpio = pd.DataFrame({
        "cod_divipola": tabla["cod_divipola"],
        "nombre_publicado": tabla["Municipio"],
        "anio": ANIO,
        "periodo": 25,
        "ubicacion": "Total",
        "empresa": tabla["Empresa"],
        "estrato_1": tabla["Estrato 1"],
        "estrato_2": tabla["Estrato 2"],
        "estrato_3": tabla["Estrato 3"],
        "estrato_4": tabla["Estrato 4"],
        "estrato_5": tabla["Estrato 5"],
        "estrato_6": tabla["Estrato 6"],
        "total_residencial": tabla["Total Residencial"],
        "industrial": tabla["Industrial"],
        "comercial": tabla["Comercial"],
        "oficial": tabla["Oficial"],
        "otros": tabla["Otros"],
        "total_no_residencial": tabla["Total No Residencial"],
    })
    sin_codigo = limpio[limpio["cod_divipola"].isna()].copy()
    con_codigo = limpio[limpio["cod_divipola"].notna()].copy()
    if sin_codigo.shape[0]:
        guardar(sin_codigo, MODELO / "sui-sin-codigo.csv")
    medellin = con_codigo[con_codigo["cod_divipola"] == CODIGO]
    if len(medellin) != 1:
        raise SystemExit("El SUI anual no dejó una sola fila de Medellín con código")
    guardar(con_codigo, MODELO / "sui.csv")
    return con_codigo


def tarifa():
    tabla = pd.read_csv(MUESTRAS / "epm-tarifas-2016-2021-20261007.csv", dtype=str)
    tabla = tabla[tabla["Año"].notna()].copy()
    tabla["anio"] = pd.to_numeric(tabla["Año"], errors="coerce").astype("Int64")
    tabla["mes"] = tabla["Mes"].map(MESES).astype("Int64")
    tabla["precio_propiedad_epm"] = precio_cop(tabla["Propiedad Epm"])
    corte = tabla[
        (tabla["anio"] == ANIO)
        & (tabla["Tipo de Información"] == "Monomia")
        & (tabla["Nivel"] == "I")
        & (tabla["Tipo de Tarifa"] == "Residencial")
        & (tabla["Tipo de Dato"] == "Estrato 1")
        & (tabla["Rango de Consumo"] == "Rango > CS")
    ].copy()
    corte = corte[["anio", "mes", "precio_propiedad_epm"]].sort_values("mes")
    corte["tipo_informacion"] = "Monomia"
    corte["tipo_tarifa"] = "Residencial"
    corte["tipo_dato"] = "Estrato 1"
    corte["rango_consumo"] = "Rango > CS"
    corte["nivel"] = "I"
    if len(corte) != 12 or corte["precio_propiedad_epm"].isna().any():
        raise SystemExit("Faltan meses de la tarifa de estrato 1 en 2021")
    guardar(corte, MODELO / "tarifa.csv")
    return corte


def limpiar():
    print("Fuentes públicas")
    geo = geografia()
    clima()
    poblacion(geo)
    sui(geo)
    tarifa()


if __name__ == "__main__":
    limpiar()
