"""MercaBarrio · tienda de barrio en línea.

    pip install -r requirements.txt
    python app.py            -> http://127.0.0.1:5000
"""
import os
from pathlib import Path

from flask import Flask, send_from_directory

from tienda.api.rutas import crear_api
from tienda.contenedor import construir_servicios

RAIZ = Path(__file__).resolve().parent


def crear_app(ruta_db: str | None = None, clave_admin: str | None = None, sembrar: bool = True) -> Flask:
    app = Flask(__name__, static_folder=str(RAIZ / "static"), static_url_path="/static")
    app.json.ensure_ascii = False
    app.json.sort_keys = False
    servicios = construir_servicios(ruta_db or os.environ.get("MERCABARRIO_DB", str(RAIZ / "mercabarrio.db")),
                                    sembrar=sembrar)
    app.register_blueprint(crear_api(servicios, clave_admin or os.environ.get("MERCABARRIO_ADMIN", "admin123")))

    @app.get("/")
    def inicio():
        return send_from_directory(app.static_folder, "index.html")

    return app


if __name__ == "__main__":
    crear_app().run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
