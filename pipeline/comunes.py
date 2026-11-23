"""Limpieza que comparten las fuentes: código de cinco dígitos, tildes y precios."""

import unicodedata

import pandas as pd


def codigo(serie):
    texto = serie.astype(str).str.strip()
    texto = texto.str.replace(r"\.0$", "", regex=True)
    texto = texto.mask(texto.isin(["nan", "None", ""]))
    return texto.str.zfill(5)


def sin_tilde(texto):
    if pd.isna(texto):
        return ""
    base = unicodedata.normalize("NFD", str(texto).strip())
    limpio = "".join(letra for letra in base if unicodedata.category(letra) != "Mn")
    return " ".join(limpio.upper().split())


def decimal_coma(serie):
    texto = serie.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")


def precio_cop(serie):
    texto = serie.astype(str).str.strip()
    texto = texto.str.replace("$", "", regex=False).str.replace(" ", "", regex=False)
    texto = texto.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")


def numero_o_vacio(serie):
    texto = serie.astype(str).str.strip()
    texto = texto.mask(texto.isin(["", "ND", "nan", "None"]))
    return pd.to_numeric(texto, errors="coerce")


def guardar(tabla, ruta):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ruta, index=False, encoding="utf-8-sig")
    print(f"{ruta.relative_to(ruta.parents[2])}  {len(tabla)} filas")
