"""Arma las tablas que leen los reportes. Cada indicador sale de su grano."""

import pandas as pd

from comunes import guardar
from rutas import ANIO, CODIGO, INDICADORES, MODELO, OPERACION

TIPOS = ["Residencial", "Industrial", "Comercial", "Oficial", "Otros"]


def medidor(clientes):
    por_tipo = {}
    por_estrato = {}
    por_hora = {}
    control_kwh = 0.0
    control_n = 0
    lectura = {
        "cliente_id": str,
        "fecha_hora": str,
        "consumo_kwh": float,
    }
    for bloque in pd.read_csv(OPERACION / "04-consumo.csv", dtype=lectura, chunksize=1_000_000):
        bloque = bloque.merge(clientes[["cliente_id", "tipo_cliente", "estrato"]], on="cliente_id", how="left")
        if bloque["tipo_cliente"].isna().any():
            raise SystemExit("Hay consumo sin cliente")
        bloque["periodo"] = bloque["fecha_hora"].str.slice(0, 7)
        bloque["hora"] = bloque["fecha_hora"].str.slice(11, 13).astype(int)
        enero = (bloque["cliente_id"] == "C0001") & (bloque["periodo"] == "2021-01")
        control_kwh += bloque.loc[enero, "consumo_kwh"].sum()
        control_n += int(enero.sum())
        for (periodo, tipo), kwh in bloque.groupby(["periodo", "tipo_cliente"], sort=False)["consumo_kwh"].sum().items():
            por_tipo[(periodo, tipo)] = por_tipo.get((periodo, tipo), 0.0) + float(kwh)
        residencial = bloque[bloque["estrato"].notna()]
        for (periodo, estrato), kwh in residencial.groupby(["periodo", "estrato"], sort=False)["consumo_kwh"].sum().items():
            por_estrato[(periodo, int(estrato))] = por_estrato.get((periodo, int(estrato)), 0.0) + float(kwh)
        for (periodo, tipo, hora), grupo in bloque.groupby(["periodo", "tipo_cliente", "hora"], sort=False):
            actual = por_hora.setdefault((periodo, tipo, int(hora)), [0.0, 0])
            actual[0] += float(grupo["consumo_kwh"].sum())
            actual[1] += int(len(grupo))

    periodos = [f"{ANIO}-{mes:02d}" for mes in range(1, 13)]
    kwh_anio = round(sum(por_tipo.values()), 4)
    tipo = pd.DataFrame([
        {"periodo": periodo, "tipo_cliente": tipo, "kwh": round(por_tipo.get((periodo, tipo), 0.0), 1)}
        for periodo in periodos for tipo in TIPOS
    ])
    estrato = pd.DataFrame([
        {"periodo": periodo, "estrato": estrato, "kwh": round(kwh, 1)}
        for (periodo, estrato), kwh in sorted(por_estrato.items())
    ])
    hora = pd.DataFrame([
        {
            "periodo": periodo,
            "tipo_cliente": tipo,
            "hora": hora,
            "kwh": round(valores[0], 4),
            "mediciones": valores[1],
        }
        for (periodo, tipo, hora), valores in sorted(por_hora.items())
    ])
    mes = pd.DataFrame([
        {
            "periodo": periodo,
            "kwh": round(sum(por_tipo.get((periodo, tipo), 0.0) for tipo in TIPOS), 1),
        }
        for periodo in periodos
    ])
    guardar(mes, INDICADORES / "medidor-mes.csv")
    guardar(tipo, INDICADORES / "medidor-tipo.csv")
    guardar(estrato, INDICADORES / "medidor-estrato.csv")
    guardar(hora, INDICADORES / "medidor-hora.csv")
    return round(control_kwh, 4), control_n, kwh_anio


def cuenta(clientes):
    factura = pd.read_csv(MODELO / "factura.csv", dtype={"cliente_id": str})
    factura = factura.merge(clientes[["cliente_id", "tipo_cliente"]], on="cliente_id", how="left")
    factura["valor_peso"] = factura["valor_facturado"]
    factura["peso_tarifa"] = factura["tarifa"] * factura["consumo_kwh_mes"]
    mes = factura.groupby("periodo", as_index=False).agg(
        valor=("valor_facturado", "sum"),
        kwh=("consumo_kwh_mes", "sum"),
        peso_tarifa=("peso_tarifa", "sum"),
        facturas=("cliente_id", "size"),
    )
    estados = factura.groupby(["periodo", "estado_pago"]).size().unstack(fill_value=0).reset_index()
    mes = mes.merge(estados, on="periodo")
    mes["tarifa_media"] = (mes["peso_tarifa"] / mes["kwh"]).round(2)
    mes["valor"] = mes["valor"].round(2)
    mes["kwh"] = mes["kwh"].round(1)
    mes = mes.drop(columns="peso_tarifa")
    tipo = factura.groupby(["periodo", "tipo_cliente"], as_index=False).agg(
        valor=("valor_facturado", "sum"),
        kwh=("consumo_kwh_mes", "sum"),
    )
    tipo["valor"] = tipo["valor"].round(2)
    tipo["kwh"] = tipo["kwh"].round(1)
    guardar(mes, INDICADORES / "cuenta-mes.csv")
    guardar(tipo, INDICADORES / "cuenta-tipo.csv")
    return factura


def servicio():
    equipos = pd.read_csv(MODELO / "activo.csv", dtype={"infraestructura_id": str, "cod_divipola": str})
    equipos["edad"] = ANIO - pd.to_datetime(equipos["fecha_instalacion"]).dt.year
    fallas = pd.read_csv(MODELO / "falla.csv", dtype={"incidente_id": str, "infraestructura_id": str})
    fallas = fallas.merge(
        equipos[["infraestructura_id", "tipo", "latitud", "longitud", "edad", "estado"]],
        on="infraestructura_id",
        how="left",
    )
    if "precipitacion_mm" in fallas.columns or fallas[["latitud", "longitud"]].isna().any().any():
        raise SystemExit("La falla de reporte quedó mal armada")
    trabajos = pd.read_csv(MODELO / "mantenimiento.csv", dtype={"infraestructura_id": str})
    clima = pd.read_csv(MODELO / "clima.csv", dtype={"cod_divipola": str})
    clima["periodo"] = clima["fecha_hora"].str.slice(0, 7)
    lluvia = clima.groupby("periodo", as_index=False)["precipitacion_mm"].sum()
    lluvia["precipitacion_mm"] = lluvia["precipitacion_mm"].round(1)
    guardar(fallas, INDICADORES / "fallas.csv")
    guardar(lluvia, INDICADORES / "lluvia-mes.csv")
    guardar(equipos, INDICADORES / "equipos.csv")
    guardar(trabajos, INDICADORES / "mantenimiento.csv")
    return len(fallas)


def contexto():
    habitantes = pd.read_csv(MODELO / "poblacion.csv", dtype={"cod_divipola": str})
    sector = pd.read_csv(MODELO / "sui.csv", dtype={"cod_divipola": str})
    medellin = sector[sector["cod_divipola"] == CODIGO].iloc[0]
    estratos = pd.DataFrame({
        "cod_divipola": CODIGO,
        "estrato": range(1, 7),
        "usuarios": [int(medellin[f"estrato_{i}"]) for i in range(1, 7)],
    })
    tipos = pd.DataFrame({
        "cod_divipola": CODIGO,
        "tipo_cliente": ["Industrial", "Comercial", "Oficial", "Otros"],
        "usuarios": [int(medellin[nombre]) for nombre in ("industrial", "comercial", "oficial", "otros")],
    })
    precios = pd.read_csv(MODELO / "tarifa.csv")
    suscriptores = int(medellin["total_residencial"] + medellin["total_no_residencial"])
    corte = pd.DataFrame([{
        "municipio": "Medellín",
        "cod_divipola": CODIGO,
        "anio": ANIO,
        "clientes_muestra": 1000,
        "activos_muestra": 200,
        "suscriptores_publicados": suscriptores,
        "habitantes_total": int(habitantes.loc[habitantes["area"] == "Total", "habitantes"].iloc[0]),
    }])
    guardar(corte, INDICADORES / "corte.csv")
    guardar(habitantes, INDICADORES / "contexto-habitantes.csv")
    guardar(estratos, INDICADORES / "contexto-sui-estrato.csv")
    guardar(tipos, INDICADORES / "contexto-sui-tipo.csv")
    guardar(precios, INDICADORES / "contexto-tarifa.csv")
    return suscriptores


def comprobar(control_kwh, control_n, kwh_medidos, facturas, suscriptores, n_fallas):
    cuenta_cliente = facturas[(facturas["cliente_id"] == "C0001") & (facturas["periodo"] == "2021-01")].iloc[0]
    if control_n != 744 or round(control_kwh, 4) != round(float(cuenta_cliente["consumo_kwh_mes"]), 4):
        raise SystemExit("El medidor de C0001 en enero no cuadra con su factura")
    if abs(kwh_medidos - round(float(facturas["consumo_kwh_mes"].sum()), 4)) > 0.01:
        raise SystemExit("El kWh medido del año no cuadra con la suma de las facturas")
    if suscriptores != 996993:
        raise SystemExit("Los suscriptores publicados de Medellín no son 996.993")
    if n_fallas != 522:
        raise SystemExit("No quedaron 522 fallas")
    precio = pd.read_csv(INDICADORES / "contexto-tarifa.csv")
    enero = float(precio.loc[precio["mes"] == 1, "precio_propiedad_epm"].iloc[0])
    if enero != 573.05:
        raise SystemExit("La tarifa de enero no quedó en 573,05")
    print("Comprobación: C0001 enero, suscriptores, tarifa y fallas cuadran.")


def armar():
    print("Indicadores para reportes")
    clientes = pd.read_csv(MODELO / "cliente.csv", dtype={"cliente_id": str, "cod_divipola": str})
    control_kwh, control_n, kwh_medidos = medidor(clientes)
    facturas = cuenta(clientes)
    n_fallas = servicio()
    suscriptores = contexto()
    comprobar(control_kwh, control_n, kwh_medidos, facturas, suscriptores, n_fallas)


if __name__ == "__main__":
    armar()
