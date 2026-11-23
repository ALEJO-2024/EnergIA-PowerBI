"""Tablero EnergIA. Sirve el resumen y el frontend ya construido."""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from chat import router as chat_router

AQUI = Path(__file__).resolve().parent
WEB = AQUI.parent / "web" / "dist"
RESUMEN = AQUI / "resumen.json"

app = FastAPI(title="EnergIA")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)


@app.get("/api/resumen")
def resumen():
    if not RESUMEN.exists():
        from agregar import construir
        construir()
    return json.loads(RESUMEN.read_text(encoding="utf-8"))


if WEB.exists():
    app.mount("/assets", StaticFiles(directory=WEB / "assets"), name="assets")

    @app.get("/")
    def inicio():
        return FileResponse(WEB / "index.html")

    @app.get("/{ruta:path}")
    def frontend(ruta: str):
        destino = WEB / ruta
        if destino.is_file():
            return FileResponse(destino)
        return FileResponse(WEB / "index.html")
