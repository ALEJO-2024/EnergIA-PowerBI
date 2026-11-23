"""Limpia la operación generada del corte. No vuelve a calcular el kWh de la factura."""

import pandas as pd

from comunes import guardar
from rutas import CODIGO, MODELO, OPERACION


def exigir(condicion, mensaje):
    if not condicion:
        raise SystemExit(mensaje)


def tiempo():
    tabla = pd.read_csv(OPERACION / "01-tiempo.csv", dtype=str)
    exigir(len(tabla) == 8760, "El calendario no tiene las 8.760 horas de 2021")
    exigir(tabla["fecha_hora"].duplicated().sum() == 0, "Hay horas repetidas en el calendario")
    guardar(tabla, MODELO / "tiempo.csv")


def cliente():
    tabla = pd.read_csv(OPERACION / "02-cliente.csv", dtype={"cliente_id": str, "cod_divipola": str, "estrato": str})
    exigir(set(tabla["cod_divipola"]) == {CODIGO}, "Hay clientes fuera de Medellín")
    exigir(len(tabla) == 1000, "La muestra no tiene 1.000 clientes")
    tabla["estrato"] = pd.to_numeric(tabla["estrato"], errors="coerce").astype("Int64")
    guardar(tabla, MODELO / "cliente.csv")
    return tabla


def activo():
    tabla = pd.read_csv(OPERACION / "03-activo.csv", dtype={"infraestructura_id": str, "cod_divipola": str})
    exigir(set(tabla["cod_divipola"]) == {CODIGO}, "Hay equipos fuera de Medellín")
    exigir(len(tabla) == 200, "La muestra no tiene 200 equipos")
    guardar(tabla, MODELO / "activo.csv")
    return tabla


def factura(clientes):
    tabla = pd.read_csv(OPERACION / "05-factura.csv", dtype={"cliente_id": str, "periodo": str})
    exigir(set(tabla["cliente_id"]) <= set(clientes["cliente_id"]), "Hay facturas sin cliente")
    exigir(len(tabla) == 12000, "No hay una factura por cliente y mes")
    guardar(tabla, MODELO / "factura.csv")
    return tabla


def falla(activos):
    tabla = pd.read_csv(OPERACION / "06-falla.csv", dtype={"incidente_id": str, "infraestructura_id": str})
    exigir("precipitacion_mm" not in tabla.columns, "La falla trae lluvia y no debe")
    exigir(set(tabla["infraestructura_id"]) <= set(activos["infraestructura_id"]), "Hay fallas sin equipo")
    tabla["periodo"] = tabla["fecha_hora"].str.slice(0, 7)
    guardar(tabla, MODELO / "falla.csv")
    return tabla


def mantenimiento(activos):
    tabla = pd.read_csv(OPERACION / "07-mantenimiento.csv", dtype={"mantenimiento_id": str, "infraestructura_id": str})
    exigir(set(tabla["infraestructura_id"]) <= set(activos["infraestructura_id"]), "Hay mantenimientos sin equipo")
    tabla["periodo"] = tabla["fecha"].str.slice(0, 7)
    guardar(tabla, MODELO / "mantenimiento.csv")


def limpiar():
    print("Operación de la muestra")
    tiempo()
    clientes = cliente()
    activos = activo()
    factura(clientes)
    falla(activos)
    mantenimiento(activos)


if __name__ == "__main__":
    limpiar()
