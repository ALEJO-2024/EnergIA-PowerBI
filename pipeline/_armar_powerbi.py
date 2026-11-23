# -*- coding: utf-8 -*-
"""Arma el modelo TMDL y las cinco páginas PBIR. No forma parte del pipeline de datos."""

import json
import shutil
import uuid
from pathlib import Path

RAIZ = Path(r"C:\Users\ruizd\Pictures\BI")
DATOS = RAIZ / "datos finales"
MODELO = RAIZ / "dashboard - power bi.SemanticModel" / "definition"
INFORME = RAIZ / "dashboard - power bi.Report" / "definition"
TEMA = RAIZ / "dashboard - power bi.Report" / "StaticResources" / "RegisteredResources"


def m(texto):
    return "\n".join("\t\t\t" + linea for linea in texto.strip().splitlines())


def csv_m(archivo, tipos, vacios=None):
    lista = ", ".join('{"%s", %s}' % (c, t) for c, t in tipos)
    ruta = str(DATOS / archivo).replace("\\", "\\\\")
    nombres = '    Nombres = Table.TransformColumnNames(Encabezados, each Text.Replace(_, Character.FromNumber(65279), "")),\n'
    if vacios:
        cols = ", ".join('"%s"' % c for c in vacios)
        medio = (
            nombres
            + '    Limpios = Table.ReplaceValue(Nombres, "", null, Replacer.ReplaceValue, {%s}),\n' % cols
            + "    Tipos = Table.TransformColumnTypes(Limpios, {%s})\n" % lista
        )
    else:
        medio = nombres + "    Tipos = Table.TransformColumnTypes(Nombres, {%s})\n" % lista
    cuerpo = (
        "let\n"
        '    Origen = Csv.Document(File.Contents("%s"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),\n'
        "    Encabezados = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),\n"
        "%s"
        "in\n"
        "    Tipos"
    ) % (ruta, medio)
    return m(cuerpo)


def col(nombre, tipo, key=False, suma="none", categoria=None, formato=None):
    lineas = [
        "\tcolumn %s" % nombre,
        "\t\tdataType: %s" % tipo,
        "\t\tlineageTag: %s" % uuid.uuid4(),
        "\t\tsummarizeBy: %s" % suma,
        "\t\tsourceColumn: %s" % nombre,
    ]
    if key:
        lineas.append("\t\tisKey")
    if categoria:
        lineas.append("\t\tdataCategory: %s" % categoria)
    if formato:
        fmt = formato if formato.startswith('"') else '"%s"' % formato
        lineas.append("\t\tformatString: %s" % fmt)
    return "\n".join(lineas) + "\n"


def med(nombre, dax, formato):
    fmt = formato if formato.startswith('"') else '"%s"' % formato
    return (
        "\tmeasure '%s' = ```\n\t\t%s\n\t\t```\n\t\tformatString: %s\n\t\tlineageTag: %s\n"
        % (nombre, dax, fmt, uuid.uuid4())
    )


def tabla(nombre, columnas, medidas, consulta):
    texto = "table %s\n\tlineageTag: %s\n\n" % (nombre, uuid.uuid4())
    texto += "".join(columnas) + "\n"
    texto += "".join(medidas)
    texto += "\tpartition %s = m\n\t\tmode: import\n\t\tsource = ```\n%s\n\t\t\t```\n" % (nombre, consulta)
    return texto


def escribir_modelo():
    carpeta = MODELO / "tables"
    if carpeta.exists():
        shutil.rmtree(carpeta)
    carpeta.mkdir(parents=True)

    ruta_activo = str(DATOS / "activo.csv").replace("\\", "\\\\")
    ruta_sui = str(DATOS / "sui.csv").replace("\\", "\\\\")
    activo_m = m(
        """
let
    Origen = Csv.Document(File.Contents("%s"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.TransformColumnNames(Table.PromoteHeaders(Origen, [PromoteAllScalars = true]), each Text.Replace(_, Character.FromNumber(65279), "")),
    Tipos = Table.TransformColumnTypes(Encabezados, {{"infraestructura_id", type text}, {"cod_divipola", type text}, {"tipo", type text}, {"latitud", type number}, {"longitud", type number}, {"fecha_instalacion", type date}, {"estado", type text}}),
    Salida = Table.AddColumn(Tipos, "antiguedad", each 2021 - Date.Year([fecha_instalacion]), Int64.Type)
in
    Salida
"""
        % ruta_activo
    )
    estrato_m = m(
        """
let
    Origen = Csv.Document(File.Contents("%s"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.TransformColumnNames(Table.PromoteHeaders(Origen, [PromoteAllScalars = true]), each Text.Replace(_, Character.FromNumber(65279), "")),
    Estrecho = Table.SelectColumns(Encabezados, {"cod_divipola", "estrato_1", "estrato_2", "estrato_3", "estrato_4", "estrato_5", "estrato_6"}),
    Largo = Table.Unpivot(Estrecho, {"estrato_1", "estrato_2", "estrato_3", "estrato_4", "estrato_5", "estrato_6"}, "estrato", "usuarios"),
    Nombres = Table.ReplaceValue(Largo, "estrato_", "", Replacer.ReplaceText, {"estrato"}),
    Limpios = Table.ReplaceValue(Nombres, "", null, Replacer.ReplaceValue, {"usuarios"}),
    Salida = Table.TransformColumnTypes(Limpios, {{"cod_divipola", type text}, {"estrato", type text}, {"usuarios", Int64.Type}})
in
    Salida
"""
        % ruta_sui
    )
    tipo_m = m(
        """
let
    Origen = Csv.Document(File.Contents("%s"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Encabezados = Table.TransformColumnNames(Table.PromoteHeaders(Origen, [PromoteAllScalars = true]), each Text.Replace(_, Character.FromNumber(65279), "")),
    Estrecho = Table.SelectColumns(Encabezados, {"cod_divipola", "industrial", "comercial", "oficial", "otros"}),
    Largo = Table.Unpivot(Estrecho, {"industrial", "comercial", "oficial", "otros"}, "tipo_cliente", "usuarios"),
    Limpios = Table.ReplaceValue(Largo, "", null, Replacer.ReplaceValue, {"usuarios"}),
    Salida = Table.TransformColumnTypes(Limpios, {{"cod_divipola", type text}, {"tipo_cliente", type text}, {"usuarios", Int64.Type}})
in
    Salida
"""
        % ruta_sui
    )

    archivos = {
        "geografia": tabla(
            "geografia",
            [
                col("cod_divipola", "string", key=True),
                col("nombre", "string"),
                col("departamento", "string"),
                col("tipo_municipio", "string"),
                col("latitud", "double", categoria="Latitude"),
                col("longitud", "double", categoria="Longitude"),
            ],
            [],
            csv_m("geografia.csv", [
                ("cod_divipola", "type text"), ("nombre", "type text"),
                ("departamento", "type text"), ("tipo_municipio", "type text"),
                ("latitud", "type number"), ("longitud", "type number"),
            ]),
        ),
        "tiempo": tabla(
            "tiempo",
            [
                col("fecha_hora", "dateTime", key=True),
                col("fecha", "dateTime"),
                col("hora", "int64"),
                col("mes", "int64"),
                col("anio", "int64"),
                col("periodo", "string"),
            ],
            [],
            csv_m("tiempo.csv", [
                ("fecha_hora", "type datetime"), ("fecha", "type date"),
                ("hora", "Int64.Type"), ("mes", "Int64.Type"),
                ("anio", "Int64.Type"), ("periodo", "type text"),
            ]),
        ),
        "cliente": tabla(
            "cliente",
            [
                col("cliente_id", "string", key=True),
                col("cod_divipola", "string"),
                col("tipo_cliente", "string"),
                col("estrato", "int64"),
                col("estado", "string"),
            ],
            [],
            csv_m("cliente.csv", [
                ("cliente_id", "type text"), ("cod_divipola", "type text"),
                ("tipo_cliente", "type text"), ("estrato", "Int64.Type"), ("estado", "type text"),
            ], vacios=["estrato"]),
        ),
        "activo": tabla(
            "activo",
            [
                col("infraestructura_id", "string", key=True),
                col("cod_divipola", "string"),
                col("tipo", "string"),
                col("latitud", "double", categoria="Latitude"),
                col("longitud", "double", categoria="Longitude"),
                col("fecha_instalacion", "dateTime"),
                col("estado", "string"),
                col("antiguedad", "int64"),
            ],
            [],
            activo_m,
        ),
        "consumo": tabla(
            "consumo",
            [
                col("cliente_id", "string"),
                col("fecha_hora", "dateTime"),
                col("consumo_kwh", "double", suma="sum", formato="#,0.0000"),
            ],
            [
                med("kWh medidos", "SUM(consumo[consumo_kwh])", "#,0.0"),
                med("kWh promedio", "AVERAGE(consumo[consumo_kwh])", "#,0.00"),
            ],
            csv_m("consumo.csv", [
                ("cliente_id", "type text"), ("fecha_hora", "type datetime"), ("consumo_kwh", "type number"),
            ]),
        ),
        "factura": tabla(
            "factura",
            [
                col("cliente_id", "string"),
                col("periodo", "string"),
                col("consumo_kwh_mes", "double", suma="sum", formato="#,0.0000"),
                col("valor_facturado", "double", suma="sum", formato="#,0.00"),
                col("tarifa", "double", formato="#,0.00"),
                col("estado_pago", "string"),
            ],
            [
                med("Valor facturado", "SUM(factura[valor_facturado])", '"$#,0"'),
                med("kWh facturados", "SUM(factura[consumo_kwh_mes])", "#,0.0"),
                med("Cuentas", "COUNTROWS(factura)", "#,0"),
                med("Pagadas", 'CALCULATE(COUNTROWS(factura), factura[estado_pago] = "pagada")', "#,0"),
                med("Pendientes", 'CALCULATE(COUNTROWS(factura), factura[estado_pago] = "pendiente")', "#,0"),
                med("En mora", 'CALCULATE(COUNTROWS(factura), factura[estado_pago] = "en mora")', "#,0"),
                med("Tarifa media", "AVERAGE(factura[tarifa])", '"$#,0.00"'),
            ],
            csv_m("factura.csv", [
                ("cliente_id", "type text"), ("periodo", "type text"),
                ("consumo_kwh_mes", "type number"), ("valor_facturado", "type number"),
                ("tarifa", "type number"), ("estado_pago", "type text"),
            ]),
        ),
        "falla": tabla(
            "falla",
            [
                col("incidente_id", "string", key=True),
                col("infraestructura_id", "string"),
                col("fecha_hora", "dateTime"),
                col("clientes_afectados", "int64", suma="sum"),
                col("duracion_minutos", "int64", suma="sum"),
            ],
            [
                med("Fallas", "COUNTROWS(falla)", "#,0"),
                med("Clientes alcanzados", "SUM(falla[clientes_afectados])", "#,0"),
                med("Minutos", "SUM(falla[duracion_minutos])", "#,0"),
            ],
            csv_m("falla.csv", [
                ("incidente_id", "type text"), ("infraestructura_id", "type text"),
                ("fecha_hora", "type datetime"), ("clientes_afectados", "Int64.Type"),
                ("duracion_minutos", "Int64.Type"),
            ]),
        ),
        "mantenimiento": tabla(
            "mantenimiento",
            [
                col("mantenimiento_id", "string", key=True),
                col("infraestructura_id", "string"),
                col("fecha", "dateTime"),
                col("tipo", "string"),
                col("costo", "double", suma="sum", formato="#,0"),
            ],
            [med("Costo total", "SUM(mantenimiento[costo])", '"$#,0"')],
            csv_m("mantenimiento.csv", [
                ("mantenimiento_id", "type text"), ("infraestructura_id", "type text"),
                ("fecha", "type date"), ("tipo", "type text"), ("costo", "type number"),
            ]),
        ),
        "clima": tabla(
            "clima",
            [
                col("cod_divipola", "string"),
                col("fecha_hora", "dateTime"),
                col("precipitacion_mm", "double", suma="sum", formato="#,0.0"),
                col("temperatura_2m", "double"),
                col("humedad_relativa", "double"),
                col("viento_kmh", "double"),
                col("presion_hpa", "double"),
            ],
            [med("Lluvia mm", "SUM(clima[precipitacion_mm])", "#,0.0")],
            csv_m("clima.csv", [
                ("cod_divipola", "type text"), ("fecha_hora", "type datetime"),
                ("precipitacion_mm", "type number"), ("temperatura_2m", "type number"),
                ("humedad_relativa", "type number"), ("viento_kmh", "type number"),
                ("presion_hpa", "type number"),
            ]),
        ),
        "poblacion": tabla(
            "poblacion",
            [
                col("cod_divipola", "string"),
                col("anio", "int64"),
                col("area", "string"),
                col("habitantes", "int64", suma="sum"),
            ],
            [med(
                "Habitantes publicados",
                'IF(ISFILTERED(geografia[cod_divipola]), CALCULATE(SUM(poblacion[habitantes]), poblacion[area] = "Total", poblacion[anio] = 2021), CALCULATE(SUM(poblacion[habitantes]), poblacion[area] = "Total", poblacion[anio] = 2021, geografia[cod_divipola] = "05001"))',
                "#,0",
            )],
            csv_m("poblacion.csv", [
                ("cod_divipola", "type text"), ("anio", "Int64.Type"),
                ("area", "type text"), ("habitantes", "Int64.Type"),
            ]),
        ),
        "sui": tabla(
            "sui",
            [
                col("cod_divipola", "string"),
                col("anio", "int64"),
                col("periodo", "int64"),
                col("ubicacion", "string"),
                col("empresa", "string"),
                *[col("estrato_%s" % i, "int64", suma="sum") for i in range(1, 7)],
                col("total_residencial", "int64", suma="sum"),
                col("industrial", "int64", suma="sum"),
                col("comercial", "int64", suma="sum"),
                col("oficial", "int64", suma="sum"),
                col("otros", "int64", suma="sum"),
                col("total_no_residencial", "int64", suma="sum"),
            ],
            [med(
                "Suscriptores",
                'IF(ISFILTERED(geografia[cod_divipola]), CALCULATE(SUM(sui[total_residencial]) + SUM(sui[total_no_residencial]), sui[anio] = 2021, sui[periodo] = 25, sui[ubicacion] = "Total"), CALCULATE(SUM(sui[total_residencial]) + SUM(sui[total_no_residencial]), sui[anio] = 2021, sui[periodo] = 25, sui[ubicacion] = "Total", geografia[cod_divipola] = "05001"))',
                "#,0",
            )],
            csv_m("sui.csv", [
                ("cod_divipola", "type text"), ("anio", "Int64.Type"), ("periodo", "Int64.Type"),
                ("ubicacion", "type text"), ("empresa", "type text"),
                ("estrato_1", "Int64.Type"), ("estrato_2", "Int64.Type"), ("estrato_3", "Int64.Type"),
                ("estrato_4", "Int64.Type"), ("estrato_5", "Int64.Type"), ("estrato_6", "Int64.Type"),
                ("total_residencial", "Int64.Type"), ("industrial", "Int64.Type"),
                ("comercial", "Int64.Type"), ("oficial", "Int64.Type"), ("otros", "Int64.Type"),
                ("total_no_residencial", "Int64.Type"),
            ], vacios=["estrato_1", "estrato_2", "estrato_3", "estrato_4", "estrato_5", "estrato_6", "industrial", "comercial", "oficial", "otros"]),
        ),
        "sui_estrato": tabla(
            "sui_estrato",
            [
                col("cod_divipola", "string"),
                col("estrato", "string"),
                col("usuarios", "int64", suma="sum"),
            ],
            [med(
                "Usuarios estrato",
                'IF(ISFILTERED(geografia[cod_divipola]), SUM(sui_estrato[usuarios]), CALCULATE(SUM(sui_estrato[usuarios]), geografia[cod_divipola] = "05001"))',
                "#,0",
            )],
            estrato_m,
        ),
        "sui_tipo": tabla(
            "sui_tipo",
            [
                col("cod_divipola", "string"),
                col("tipo_cliente", "string"),
                col("usuarios", "int64", suma="sum"),
            ],
            [med(
                "Usuarios tipo",
                'IF(ISFILTERED(geografia[cod_divipola]), SUM(sui_tipo[usuarios]), CALCULATE(SUM(sui_tipo[usuarios]), geografia[cod_divipola] = "05001"))',
                "#,0",
            )],
            tipo_m,
        ),
        "tarifa": tabla(
            "tarifa",
            [
                col("anio", "int64"),
                col("mes", "int64"),
                col("tipo_informacion", "string"),
                col("tipo_tarifa", "string"),
                col("tipo_dato", "string"),
                col("rango_consumo", "string"),
                col("nivel", "string"),
                col("precio_propiedad_epm", "double", formato="#,0.00"),
                col("precio_compartido", "double"),
                col("precio_propiedad_cliente", "double"),
                col("precio_punta", "double"),
                col("precio_fuera_punta", "double"),
            ],
            [med("Precio publicado", "AVERAGE(tarifa[precio_propiedad_epm])", '"$#,0.00"')],
            csv_m("tarifa.csv", [
                ("anio", "Int64.Type"), ("mes", "Int64.Type"),
                ("tipo_informacion", "type text"), ("tipo_tarifa", "type text"),
                ("tipo_dato", "type text"), ("rango_consumo", "type text"), ("nivel", "type text"),
                ("precio_propiedad_epm", "type number"), ("precio_compartido", "type number"),
                ("precio_propiedad_cliente", "type number"), ("precio_punta", "type number"),
                ("precio_fuera_punta", "type number"),
            ], vacios=["precio_compartido", "precio_propiedad_cliente", "precio_punta", "precio_fuera_punta"]),
        ),
    }
    for nombre, texto in archivos.items():
        (carpeta / ("%s.tmdl" % nombre)).write_text(texto, encoding="utf-8")

    orden = [
        "geografia", "tiempo", "cliente", "activo", "consumo", "factura", "falla",
        "mantenimiento", "clima", "poblacion", "sui", "sui_estrato", "sui_tipo", "tarifa",
    ]
    (MODELO / "model.tmdl").write_text(
        "\n".join([
            "model Model",
            "\tculture: es-CO",
            "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
            "\tsourceQueryCulture: es-CO",
            "\tvalueFilterBehavior: independent",
            "\tdataAccessOptions",
            "\t\tlegacyRedirects",
            "\t\treturnErrorValuesAsNull",
            "",
            "annotation __PBI_TimeIntelligenceEnabled = 1",
            "",
            'annotation PBI_ProTooling = ["DevMode"]',
            "",
            *["ref table %s\n" % n for n in orden],
            "ref cultureInfo es-CO",
            "",
        ]),
        encoding="utf-8",
    )
    pares = [
        ("cliente", "cod_divipola", "geografia", "cod_divipola"),
        ("activo", "cod_divipola", "geografia", "cod_divipola"),
        ("clima", "cod_divipola", "geografia", "cod_divipola"),
        ("poblacion", "cod_divipola", "geografia", "cod_divipola"),
        ("sui", "cod_divipola", "geografia", "cod_divipola"),
        ("sui_estrato", "cod_divipola", "geografia", "cod_divipola"),
        ("sui_tipo", "cod_divipola", "geografia", "cod_divipola"),
        ("consumo", "cliente_id", "cliente", "cliente_id"),
        ("consumo", "fecha_hora", "tiempo", "fecha_hora"),
        ("factura", "cliente_id", "cliente", "cliente_id"),
        ("falla", "infraestructura_id", "activo", "infraestructura_id"),
        ("falla", "fecha_hora", "tiempo", "fecha_hora"),
        ("mantenimiento", "infraestructura_id", "activo", "infraestructura_id"),
        ("clima", "fecha_hora", "tiempo", "fecha_hora"),
    ]
    rels = []
    for origen, col_o, destino, col_d in pares:
        rels.append(
            "relationship %s\n\tfromColumn: %s.%s\n\ttoColumn: %s.%s\n"
            % (uuid.uuid4().hex, origen, col_o, destino, col_d)
        )
    (MODELO / "relationships.tmdl").write_text("\n".join(rels), encoding="utf-8")


def literal(valor):
    return {"expr": {"Literal": {"Value": valor}}}


def color(hex_color):
    return {"solid": {"color": {"expr": {"Literal": {"Value": "'%s'" % hex_color}}}}}


def campo(entidad, propiedad):
    return {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": entidad}}, "Property": propiedad}},
        "queryRef": "%s.%s" % (entidad, propiedad),
        "nativeQueryRef": propiedad,
        "active": True,
    }


def medida_campo(entidad, propiedad):
    return {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": entidad}}, "Property": propiedad}},
        "queryRef": "%s.%s" % (entidad, propiedad),
        "nativeQueryRef": propiedad,
    }


ESQUEMA_VISUAL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"


def contenedor(x, y, w, h, z, visual, titulo=None):
    vco = visual.setdefault("visualContainerObjects", {})
    vco["background"] = [{
        "properties": {
            "show": literal("true"),
            "color": color("#0C2744"),
            "transparency": literal("0D"),
        }
    }]
    vco["border"] = [{
        "properties": {
            "show": literal("true"),
            "color": color("#1E3A52"),
            "radius": literal("0D"),
        }
    }]
    if titulo:
        vco["title"] = [{
            "properties": {
                "show": literal("true"),
                "text": literal("'%s'" % titulo.replace("'", "''")),
                "fontColor": color("#F7FAFC"),
                "fontFamily": literal("'IBM Plex Sans'"),
                "fontSize": literal("14D"),
            }
        }]
    return {
        "$schema": ESQUEMA_VISUAL,
        "name": uuid.uuid4().hex[:20],
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": visual,
    }


def grafico(tipo, roles, titulo):
    estado = {}
    for rol, proyecciones in roles.items():
        estado[rol] = {"projections": proyecciones}
    visual = {"visualType": tipo, "query": {"queryState": estado}, "drillFilterOtherVisuals": True}
    return visual


def texto(valor, tamano="20pt"):
    return {
        "visualType": "textbox",
        "objects": {
            "general": [{
                "properties": {
                    "paragraphs": [{
                        "textRuns": [{
                            "value": valor,
                            "textStyle": {
                                "fontFamily": "IBM Plex Sans",
                                "fontSize": tamano,
                                "color": "#F7FAFC",
                            },
                        }]
                    }]
                }
            }]
        },
    }


def slicer():
    visual = grafico("slicer", {"Values": [campo("geografia", "nombre")]}, None)
    visual["syncGroup"] = {"groupName": "municipio", "fieldChanges": True, "filterChanges": True}
    return contenedor(1560, 16, 336, 88, 1, visual, "Municipio")


def tarjeta(x, y, w, entidad, medida, z):
    return contenedor(x, y, w, 110, z, grafico("card", {"Data": [medida_campo(entidad, medida)]}, None))


def pagina(nombre, titulo, historia, visuales):
    encabezado = contenedor(24, 12, 1500, 40, 0, texto(titulo, "24pt"))
    sin_fondo = {
        "background": [{"properties": {"show": literal("false")}}],
        "border": [{"properties": {"show": literal("false")}}],
    }
    encabezado["visual"]["visualContainerObjects"] = sin_fondo
    relato = contenedor(24, 52, 1500, 64, 2, texto(historia, "12pt"))
    relato["visual"]["visualContainerObjects"] = sin_fondo
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": nombre,
        "displayName": titulo,
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920,
        "objects": {
            "background": [{"properties": {"color": color("#061525"), "transparency": literal("0D")}}],
        },
        "visuals": [encabezado, relato, slicer(), *visuales],
    }


def escribir_informe():
    paginas = INFORME / "pages"
    vieja = paginas / "356a3435e706c7ce18e5"
    if vieja.exists():
        shutil.rmtree(vieja)
    for carpeta in list(paginas.iterdir()):
        if carpeta.is_dir() and carpeta.name != "pages.json":
            shutil.rmtree(carpeta)

    kwh = medida_campo("consumo", "kWh medidos")
    promedio = medida_campo("consumo", "kWh promedio")
    p1 = pagina(
        "a1000000000000000001",
        "El año en el medidor",
        "La energía medida no es una línea plana. En una casa sube al final de la tarde. En un local pesa más el horario de trabajo. Esta página mira el medidor, no la factura.",
        [
            tarjeta(24, 120, 420, "consumo", "kWh medidos", 3),
            contenedor(24, 246, 1180, 390, 4, grafico("lineChart", {"Category": [campo("tiempo", "fecha")], "Y": [kwh]}, None), "Consumo por día"),
            contenedor(1220, 246, 676, 390, 5, grafico("clusteredColumnChart", {"Category": [campo("cliente", "tipo_cliente")], "Y": [kwh]}, None), "Quién consume"),
            contenedor(24, 652, 1180, 400, 6, grafico("lineChart", {"Category": [campo("tiempo", "hora")], "Series": [campo("cliente", "tipo_cliente")], "Y": [promedio]}, None), "Forma del día"),
            contenedor(1220, 652, 676, 400, 7, grafico("clusteredBarChart", {"Category": [campo("cliente", "estrato")], "Y": [medida_campo("consumo", "kWh medidos")]}, None), "Residencial por estrato"),
        ],
    )
    p1["visuals"][-1]["filterConfig"] = {
        "filters": [{
            "name": "soloResidencial",
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "cliente"}}, "Property": "tipo_cliente"}},
            "type": "Categorical",
            "filter": {
                "Version": 2,
                "From": [{"Name": "c", "Entity": "cliente", "Type": 0}],
                "Where": [{
                    "Condition": {
                        "In": {
                            "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": "tipo_cliente"}}],
                            "Values": [[{"Literal": {"Value": "'Residencial'"}}]],
                        }
                    }
                }],
            },
        }]
    }

    p2 = pagina(
        "a2000000000000000002",
        "La cuenta del mes",
        "Cada cliente tiene una sola cuenta por mes. El precio se mueve porque la tarifa publicada se mueve. C0001 en 2021-01: 145,9701 kWh en las 744 horas y el mismo número en la factura.",
        [
            tarjeta(24, 120, 360, "factura", "Valor facturado", 3),
            tarjeta(400, 120, 360, "factura", "kWh facturados", 4),
            tarjeta(776, 120, 360, "factura", "Pagadas", 5),
            tarjeta(1152, 120, 360, "factura", "Pendientes", 6),
            tarjeta(1528, 120, 368, "factura", "En mora", 7),
            contenedor(24, 246, 940, 380, 8, grafico("lineChart", {"Category": [campo("factura", "periodo")], "Y": [medida_campo("factura", "Valor facturado")]}, None), "Valor por mes"),
            contenedor(980, 246, 916, 380, 9, grafico("lineChart", {"Category": [campo("factura", "periodo")], "Y": [medida_campo("factura", "Tarifa media")]}, None), "Precio medio de la muestra"),
            contenedor(24, 642, 1100, 410, 10, grafico("stackedColumnChart", {"Category": [campo("factura", "periodo")], "Series": [campo("factura", "estado_pago")], "Y": [medida_campo("factura", "Cuentas")]}, None), "Estado de las cuentas"),
            contenedor(1140, 642, 756, 410, 11, grafico("clusteredBarChart", {"Category": [campo("cliente", "tipo_cliente")], "Y": [medida_campo("factura", "Valor facturado")]}, None), "Valor por tipo de cliente"),
        ],
    )

    p3 = pagina(
        "a3000000000000000003",
        "Dónde se fue la luz",
        "Cada falla cae sobre un equipo dentro de Medellín. En esta corrida hay 522 fallas. La lluvia va en el gráfico de abajo, una vez por día, no dentro de cada falla.",
        [
            tarjeta(24, 120, 460, "falla", "Fallas", 3),
            tarjeta(500, 120, 460, "falla", "Clientes alcanzados", 4),
            tarjeta(976, 120, 460, "falla", "Minutos", 5),
            contenedor(24, 246, 1000, 400, 6, grafico("map", {
                "Category": [campo("activo", "infraestructura_id")],
                "Latitude": [campo("activo", "latitud")],
                "Longitude": [campo("activo", "longitud")],
                "Size": [medida_campo("falla", "Fallas")],
            }, None), "Dónde ocurrieron"),
            contenedor(1040, 246, 856, 400, 7, grafico("tableEx", {"Values": [
                campo("tiempo", "fecha_hora"),
                medida_campo("falla", "Fallas"),
                medida_campo("falla", "Clientes alcanzados"),
                medida_campo("falla", "Minutos"),
            ]}, None), "Horas con más fallas"),
            contenedor(24, 662, 700, 390, 8, grafico("clusteredColumnChart", {"Category": [campo("tiempo", "mes")], "Y": [medida_campo("falla", "Fallas")]}, None), "Fallas por mes"),
            contenedor(740, 662, 1156, 390, 9, grafico("lineChart", {
                "Category": [campo("tiempo", "fecha")],
                "Y": [medida_campo("falla", "Fallas")],
                "Y2": [medida_campo("clima", "Lluvia mm")],
            }, None), "Lluvia del día y número de fallas"),
        ],
    )
    p3["visuals"][7]["visual"]["query"]["sortDefinition"] = {
        "sort": [{"field": medida_campo("falla", "Fallas")["field"], "direction": "Descending"}]
    }

    p4 = pagina(
        "a4000000000000000004",
        "Qué equipo falla más",
        "Los 200 equipos no fallan igual. En esta corrida hay 428 mantenimientos y el estado de los equipos es en servicio. Esta página ordena lo que ya falló.",
        [
            tarjeta(24, 120, 420, "mantenimiento", "Costo total", 3),
            contenedor(24, 246, 700, 390, 4, grafico("clusteredBarChart", {"Category": [campo("activo", "tipo")], "Y": [medida_campo("falla", "Fallas")]}, None), "Fallas por tipo de equipo"),
            contenedor(740, 246, 1156, 390, 5, grafico("scatterChart", {
                "X": [campo("activo", "antiguedad")],
                "Y": [medida_campo("falla", "Fallas")],
                "Details": [campo("activo", "infraestructura_id")],
            }, None), "Edad y número de fallas"),
            contenedor(24, 652, 1100, 400, 6, grafico("tableEx", {"Values": [
                campo("activo", "infraestructura_id"),
                campo("activo", "tipo"),
                campo("activo", "fecha_instalacion"),
                campo("activo", "estado"),
                medida_campo("falla", "Fallas"),
                medida_campo("falla", "Minutos"),
                medida_campo("mantenimiento", "Costo total"),
            ]}, None), "Equipos con más eventos"),
            contenedor(1140, 652, 756, 400, 7, grafico("clusteredColumnChart", {"Category": [campo("mantenimiento", "tipo")], "Y": [medida_campo("mantenimiento", "Costo total")]}, None), "Costo por tipo de trabajo"),
        ],
    )
    p4["visuals"][6]["visual"]["query"]["sortDefinition"] = {
        "sort": [{"field": medida_campo("falla", "Fallas")["field"], "direction": "Descending"}]
    }

    p5 = pagina(
        "a5000000000000000005",
        "Lo que publican las fuentes",
        "Contexto publicado. No es la muestra de 1.000 clientes. En 2021 hay 2.507.620 habitantes en el área Total y 996.993 suscriptores. No se suman entre sí ni con la cabecera.",
        [
            tarjeta(24, 120, 460, "poblacion", "Habitantes publicados", 3),
            tarjeta(500, 120, 460, "sui", "Suscriptores", 4),
            tarjeta(976, 120, 460, "tarifa", "Precio publicado", 5),
            contenedor(24, 250, 900, 400, 6, grafico("clusteredBarChart", {"Category": [campo("sui_estrato", "estrato")], "Y": [medida_campo("sui_estrato", "Usuarios estrato")]}, None), "Suscriptores por estrato"),
            contenedor(940, 250, 956, 400, 7, grafico("clusteredBarChart", {"Category": [campo("sui_tipo", "tipo_cliente")], "Y": [medida_campo("sui_tipo", "Usuarios tipo")]}, None), "Resto de cuentas"),
            contenedor(24, 670, 1872, 380, 8, grafico("lineChart", {"Category": [campo("tarifa", "mes")], "Y": [medida_campo("tarifa", "Precio publicado")]}, None), "Precio publicado por EPM en 2021"),
        ],
    )

    ids = []
    for pagina_obj in (p1, p2, p3, p4, p5):
        pid = pagina_obj["name"]
        visuales = pagina_obj.pop("visuals")
        destino = INFORME / "pages" / pid
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "page.json").write_text(json.dumps(pagina_obj, ensure_ascii=False, indent=2), encoding="utf-8")
        for visual in visuales:
            carpeta = destino / "visuals" / visual["name"]
            carpeta.mkdir(parents=True, exist_ok=True)
            (carpeta / "visual.json").write_text(json.dumps(visual, ensure_ascii=False, indent=2), encoding="utf-8")
        ids.append(pid)

    (INFORME / "pages" / "pages.json").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": ids,
        "activePageName": ids[0],
    }, indent=2), encoding="utf-8")


def escribir_tema():
    TEMA.mkdir(parents=True, exist_ok=True)
    tema = {
        "name": "EnergIA",
        "dataColors": ["#2EE6C8", "#9FD4FF", "#E7C27A", "#E08B84", "#A9BDD2", "#F7FAFC", "#7D93AA"],
        "foreground": "#F7FAFC",
        "foregroundNeutralSecondary": "#A9BDD2",
        "foregroundNeutralTertiary": "#7D93AA",
        "background": "#061525",
        "backgroundLight": "#0C2744",
        "backgroundNeutral": "#0C2744",
        "tableAccent": "#2EE6C8",
        "good": "#2EE6C8",
        "neutral": "#E7C27A",
        "bad": "#E08B84",
        "maximum": "#2EE6C8",
        "center": "#E7C27A",
        "minimum": "#E08B84",
        "textClasses": {
            "callout": {"fontFace": "IBM Plex Sans", "color": "#F7FAFC"},
            "title": {"fontFace": "IBM Plex Sans", "color": "#F7FAFC"},
            "header": {"fontFace": "IBM Plex Sans", "color": "#A9BDD2"},
            "label": {"fontFace": "IBM Plex Sans", "color": "#A9BDD2"},
        },
        "visualStyles": {
            "*": {
                "*": {
                    "*": [{
                        "fontFamily": "IBM Plex Sans",
                        "color": {"solid": {"color": "#F7FAFC"}},
                    }],
                    "background": [{"color": {"solid": {"color": "#0C2744"}}, "transparency": 0}],
                    "title": [{"fontFamily": "IBM Plex Sans", "fontColor": {"solid": {"color": "#F7FAFC"}}}],
                    "labels": [{"fontFamily": "IBM Plex Sans", "color": {"solid": {"color": "#A9BDD2"}}}],
                    "categoryAxis": [{"labelColor": {"solid": {"color": "#A9BDD2"}}, "fontFamily": "IBM Plex Sans"}],
                    "valueAxis": [{"labelColor": {"solid": {"color": "#A9BDD2"}}, "fontFamily": "IBM Plex Sans"}],
                }
            },
            "page": {"*": {"background": [{"color": {"solid": {"color": "#061525"}}, "transparency": 0}]}},
        },
    }
    (TEMA / "energia.json").write_text(json.dumps(tema, ensure_ascii=False, indent=2), encoding="utf-8")
    informe = json.loads((INFORME / "report.json").read_text(encoding="utf-8"))
    informe["themeCollection"]["customTheme"] = {
        "name": "EnergIA",
        "reportVersionAtImport": {"visual": "2.14.0", "report": "3.4.0", "page": "2.3.1"},
        "type": "RegisteredResources",
    }
    paquetes = informe["resourcePackages"]
    if not any(p["name"] == "RegisteredResources" for p in paquetes):
        paquetes.append({
            "name": "RegisteredResources",
            "type": "RegisteredResources",
            "items": [{"name": "EnergIA", "path": "energia.json", "type": "CustomTheme"}],
        })
    (INFORME / "report.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    escribir_modelo()
    escribir_informe()
    escribir_tema()
    print("listo")
