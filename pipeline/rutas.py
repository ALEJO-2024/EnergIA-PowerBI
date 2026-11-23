"""Rutas del corte. Los reportes leen datos-reportes, no las muestras."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MUESTRAS = RAIZ / "muestras"
OPERACION = RAIZ / "generacion" / "salida"
REPORTES = RAIZ / "datos-reportes"
MODELO = REPORTES / "modelo"
INDICADORES = REPORTES / "indicadores"

CODIGO = "05001"
ANIO = 2021
