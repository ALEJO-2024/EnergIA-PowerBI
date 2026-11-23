# -*- coding: utf-8 -*-
"""Ajusta los visuales ya generados: tipo válido, mapa de Medellín, textos y fondo oscuro."""

import json
from pathlib import Path

PAGINAS = Path(r"C:\Users\ruizd\Pictures\BI\dashboard - power bi.Report\definition\pages")

GRAFICOS = {
    "lineChart", "columnChart", "clusteredColumnChart", "clusteredBarChart",
    "scatterChart", "barChart",
}


def lit(valor):
    return {"expr": {"Literal": {"Value": valor}}}


def color(hex_color):
    return {"solid": {"color": lit("'%s'" % hex_color)}}


def columna(entidad, prop, nombre=None):
    return {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": entidad}},
                "Property": prop,
            }
        },
        "queryRef": "%s.%s" % (entidad, prop),
        "nativeQueryRef": nombre or prop,
        "active": True,
    }


def medida(entidad, prop):
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": entidad}},
                "Property": prop,
            }
        },
        "queryRef": "%s.%s" % (entidad, prop),
        "nativeQueryRef": prop,
    }


def titulo_de(visual):
    bloques = visual.get("visualContainerObjects", {}).get("title") or []
    if not bloques:
        return ""
    texto = bloques[0]["properties"]["text"]["expr"]["Literal"]["Value"]
    return texto.strip("'")


def poner_subtitulo(visual, texto):
    vco = visual.setdefault("visualContainerObjects", {})
    vco["subTitle"] = [{
        "properties": {
            "show": lit("true"),
            "text": lit("'%s'" % texto.replace("'", "''")),
            "fontColor": color("#A9BDD2"),
            "fontFamily": lit("'IBM Plex Sans'"),
            "fontSize": lit("10D"),
            "titleWrap": lit("true"),
        }
    }]


def poner_titulo(visual, texto):
    vco = visual.setdefault("visualContainerObjects", {})
    vco["title"] = [{
        "properties": {
            "show": lit("true"),
            "text": lit("'%s'" % texto.replace("'", "''")),
            "fontColor": color("#F7FAFC"),
            "fontFamily": lit("'IBM Plex Sans'"),
            "fontSize": lit("13D"),
        }
    }]


def fondo_grafico(visual):
    objetos = visual.setdefault("objects", {})
    objetos["background"] = [{
        "properties": {
            "show": lit("true"),
            "transparency": lit("100D"),
        }
    }]
    eje = {
        "properties": {
            "labelColor": color("#A9BDD2"),
            "gridlineColor": color("#1E3A52"),
            "fontFamily": lit("'IBM Plex Sans'"),
            "fontSize": lit("11D"),
        }
    }
    for nombre in ("categoryAxis", "valueAxis"):
        objetos[nombre] = [eje]
    objetos["legend"] = [{
        "properties": {
            "labelColor": color("#A9BDD2"),
            "fontFamily": lit("'IBM Plex Sans'"),
            "fontSize": lit("11D"),
        }
    }]
    objetos["labels"] = [{
        "properties": {
            "color": color("#F7FAFC"),
            "fontFamily": lit("'IBM Plex Sans'"),
            "fontSize": lit("11D"),
        }
    }]


def fondo_tabla(visual):
    visual.setdefault("objects", {})["grid"] = [{
        "properties": {
            "gridVertical": lit("false"),
            "gridHorizontalColor": color("#1E3A52"),
            "outlineColor": color("#1E3A52"),
        }
    }]
    visual["objects"]["columnHeaders"] = [{
        "properties": {
            "fontColor": color("#F7FAFC"),
            "backColor": color("#0C2744"),
            "fontFamily": lit("'IBM Plex Sans'"),
            "fontSize": lit("11D"),
        }
    }]
    visual["objects"]["values"] = [{
        "properties": {
            "fontColor": color("#F7FAFC"),
            "backColor": color("#061525"),
            "backColorPrimary": color("#061525"),
            "backColorSecondary": color("#0C2744"),
            "fontFamily": lit("'IBM Plex Sans'"),
            "fontSize": lit("11D"),
        }
    }]


TEXTOS = {
    "Consumo por día": "Cada punto es un día de 2021. Muestra los meses altos y los días que se salen.",
    "Quién consume": "Parte del total medido que corresponde a residencial, comercial, industrial, oficial y otros.",
    "Forma del día": "Promedio de cada hora, de 0 a 23. En una casa sube al final de la tarde.",
    "Residencial por estrato": "Solo casas. El estrato 3 puede sumar más kWh aunque el 2 tenga más cuentas.",
    "Valor por mes": "El eje es el periodo de la factura, no el calendario. Un mes puede facturar más aunque mida menos.",
    "Precio medio de la muestra": "Promedio de la tarifa usada en la muestra. En enero el estrato 1 queda en 573,05 pesos.",
    "Estado de las cuentas": "Cuántas cuentas quedan pagadas, pendientes o en mora en cada mes.",
    "Valor por tipo de cliente": "Qué tipo de cliente explica la plata, no solo los kWh.",
    "Dónde ocurrieron": "Cada punto es un equipo en Medellín. El tamaño es el número de fallas, no un barrio.",
    "Horas con más fallas": "Las 12 horas con más eventos. Es un orden de lo que ya pasó, no un pronóstico.",
    "Fallas por mes": "En qué meses de 2021 se acumularon las 522 fallas.",
    "Lluvia del día y número de fallas": "La lluvia se cuenta una vez por día. No va escrita dentro de cada falla.",
    "Fallas por tipo de equipo": "Si el poste, la protección, la línea, el transformador o la subestación acumula más eventos.",
    "Edad y número de fallas": "Cada punto es un equipo. A la derecha están los más viejos. Arriba, los que más fallaron.",
    "Equipos con más eventos": "Arriba queda el que más falló, no el más nuevo. El estado de esta corrida es en servicio.",
    "Costo por tipo de trabajo": "Cuánto se fue en preventivo y cuánto en correctivo. No se mezcla con el conteo de fallas.",
    "Suscriptores por estrato": "Cuentas publicadas por el SUI. El estrato 2 es el más grande de la ciudad, con 307.598.",
    "Resto de cuentas": "Industrial, comercial, oficial y otros. Comercial publica 76.833.",
    "Precio publicado por EPM en 2021": "Serie de estrato 1, rango mayor a CS, nivel I. Esta tarifa no tiene municipio.",
}

TARJETAS = {
    "kWh medidos": "Suma del medidor de la muestra. No es el kWh de la factura ni los 996.993 suscriptores.",
    "kWh promedio": "Promedio de una hora. Sirve para ver la forma del día, no el total.",
    "Valor facturado": "Plata de las cuentas del periodo. No se vuelve a sumar el medidor.",
    "kWh facturados": "kWh cobrados en la factura. Ya son la suma de las horas del mes.",
    "Cuentas": "Número de facturas del periodo. Hay una por cliente y por mes.",
    "Pagadas": "Cuentas con estado pagada.",
    "Pendientes": "Cuentas emitidas que todavía no se pagan.",
    "En mora": "Cuentas que siguieron sin pago.",
    "Fallas": "Eventos de la muestra. En esta corrida son 522.",
    "Clientes alcanzados": "Suma de clientes afectados en cada falla. No es una lista de clientes.",
    "Minutos": "Suma de la duración de las fallas.",
    "Costo total": "Lo que costó atender los 200 equipos. En esta corrida hay 428 mantenimientos.",
    "Habitantes publicados": "DANE, área Total, 2021. La cabecera y el resto ya van dentro de ese número.",
    "Suscriptores": "SUI, periodo 25, ubicación Total. No son los 1.000 clientes de la muestra.",
    "Precio publicado": "Tarifa EPM de estrato 1. No dice en qué ciudad.",
    "Fallas destacadas": "Solo entran las 12 horas con más fallas.",
    "Lluvia mm": "Milímetros de lluvia de la cabecera. Van aparte de la falla.",
}


def medida_de_tarjeta(visual):
    estado = visual.get("query", {}).get("queryState", {})
    rol = estado.get("Values") or estado.get("Data") or {}
    proyecciones = rol.get("projections") or []
    if not proyecciones:
        return ""
    campo = proyecciones[0]["field"]
    return campo.get("Measure", {}).get("Property", "")


def convertir_horas(data):
    visual = data["visual"]
    visual["visualType"] = "clusteredBarChart"
    visual["query"] = {
        "queryState": {
            "Category": {"projections": [columna("falla", "fecha_hora", "Hora")]},
            "Y": {"projections": [medida("falla", "Fallas destacadas")]},
            "Tooltips": {"projections": [
                medida("falla", "Clientes alcanzados"),
                medida("falla", "Minutos"),
            ]},
        },
        "sortDefinition": {
            "sort": [{
                "field": medida("falla", "Fallas destacadas")["field"],
                "direction": "Descending",
            }]
        },
    }
    visual["drillFilterOtherVisuals"] = True
    fondo_grafico(visual)
    poner_subtitulo(visual, TEXTOS["Horas con más fallas"])


def convertir_mapa(data):
    visual = data["visual"]
    consulta = visual["query"]["queryState"]
    visual["visualType"] = "azureMap"
    visual["query"]["queryState"] = {
        "Category": consulta["Category"],
        "Latitude": consulta["Latitude"],
        "Longitude": consulta["Longitude"],
        "Size": consulta["Size"],
    }
    visual["objects"] = {
        "mapSettings": [{
            "properties": {
                "style": lit("'night'"),
            }
        }]
    }
    poner_subtitulo(visual, TEXTOS["Dónde ocurrieron"])


def main():
    for ruta in PAGINAS.glob("*/visuals/*/visual.json"):
        data = json.loads(ruta.read_text(encoding="utf-8"))
        visual = data["visual"]
        tipo = visual.get("visualType")
        titulo = titulo_de(visual)

        if tipo == "textbox" or tipo == "slicer":
            continue

        if tipo == "stackedColumnChart":
            visual["visualType"] = "columnChart"
            tipo = "columnChart"

        if titulo == "Horas con más fallas":
            convertir_horas(data)
            ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            continue

        if tipo == "map":
            convertir_mapa(data)
            ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            continue

        if tipo == "card":
            estado = visual.get("query", {}).get("queryState", {})
            if "Data" in estado and "Values" not in estado:
                estado["Values"] = estado.pop("Data")
            nombre = medida_de_tarjeta(visual)
            explicacion = TARJETAS.get(nombre, "")
            if explicacion:
                poner_titulo(visual, nombre)
                poner_subtitulo(visual, explicacion)
        elif titulo in TEXTOS:
            poner_subtitulo(visual, TEXTOS[titulo])

        if tipo in GRAFICOS or visual.get("visualType") in GRAFICOS:
            fondo_grafico(visual)
        if tipo == "tableEx" or visual.get("visualType") == "tableEx":
            fondo_tabla(visual)

        ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
