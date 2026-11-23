"""Corre la limpieza y deja los datos listos para los reportes."""

import importlib.util
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))


def cargar(nombre):
    ruta = CARPETA / nombre
    spec = importlib.util.spec_from_file_location(nombre.replace("-", "_").replace(".py", ""), ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def main():
    fuentes = cargar("01-fuentes-publicas.py")
    operacion = cargar("02-operacion.py")
    indicadores = cargar("03-indicadores.py")
    fuentes.limpiar()
    operacion.limpiar()
    indicadores.armar()
    print("Listo. Los reportes leen la carpeta datos-reportes.")


if __name__ == "__main__":
    main()
