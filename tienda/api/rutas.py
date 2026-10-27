"""Capa HTTP: traduce JSON <-> servicios. No contiene reglas de negocio."""
import hmac
from functools import wraps

from flask import Blueprint, jsonify, request

import pedido as reglas

from ..contenedor import Servicios
from ..dominio.errores import (DatosInvalidos, ErrorTienda, NoAutorizado, NoEncontrado,
                               StockInsuficiente, TransicionInvalida)
from ..dominio.modelos import Cliente
from ..servicios.cotizador import leer_solicitudes

CODIGOS = {DatosInvalidos: 400, NoAutorizado: 401, NoEncontrado: 404,
           StockInsuficiente: 409, TransicionInvalida: 409}


def _cuerpo() -> dict:
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise DatosInvalidos("El cuerpo de la petición debe ser un objeto JSON")
    return datos


def crear_api(servicios: Servicios, clave_admin: str) -> Blueprint:
    api = Blueprint("api", __name__, url_prefix="/api")

    @api.errorhandler(ErrorTienda)
    def error_de_negocio(error: ErrorTienda):
        codigo = next((c for tipo, c in CODIGOS.items() if isinstance(error, tipo)), 400)
        return jsonify({"error": str(error)}), codigo

    def solo_admin(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            clave = request.headers.get("X-Admin-Clave", "")
            if not hmac.compare_digest(clave.encode(), clave_admin.encode()):
                raise NoAutorizado("Clave de administración incorrecta")
            return vista(*args, **kwargs)
        return envoltura

    # --- Público -----------------------------------------------------------

    @api.get("/reglas")
    def reglas_de_negocio():
        return jsonify({
            "tasa_iva": float(reglas.TASA_IVA), "tasa_descuento": float(reglas.TASA_DESCUENTO),
            "umbral_descuento": reglas.UMBRAL_DESCUENTO, "umbral_domicilio": reglas.UMBRAL_DOMICILIO,
            "costo_domicilio": reglas.COSTO_DOMICILIO,
        })

    @api.get("/categorias")
    def categorias():
        return jsonify(servicios.catalogo.categorias())

    @api.get("/productos")
    def productos():
        a = request.args
        encontrados = servicios.catalogo.buscar(a.get("q", ""), a.get("categoria", ""),
                                                a.get("orden", "relevancia"), a.get("impuesto", ""))
        return jsonify([p.a_dict() for p in encontrados])

    @api.get("/productos/<int:producto_id>")
    def producto(producto_id: int):
        return jsonify(servicios.catalogo.detalle(producto_id).a_dict())

    @api.post("/carrito/cotizar")
    def cotizar():
        solicitudes = leer_solicitudes(_cuerpo().get("items", []))
        return jsonify(servicios.cotizador.cotizar(solicitudes).a_dict())

    @api.post("/pedidos")
    def crear_pedido():
        datos = _cuerpo()
        c = datos.get("cliente") or {}
        cliente = Cliente(str(c.get("nombre", "")), str(c.get("telefono", "")), str(c.get("direccion", "")))
        nuevo = servicios.pedidos.crear(cliente, leer_solicitudes(datos.get("items", [])),
                                        str(datos.get("notas", "")))
        return jsonify(nuevo.a_dict()), 201

    @api.get("/pedidos")
    def mis_pedidos():
        telefono = request.args.get("telefono", "")
        if not any(ch.isdigit() for ch in telefono):
            raise DatosInvalidos("Indica el teléfono con el que hiciste el pedido")
        return jsonify([p.a_dict() for p in servicios.pedidos.historial(telefono=telefono)])

    @api.post("/pedidos/<int:pedido_id>/cancelar")
    def cancelar_pedido(pedido_id: int):
        telefono = str(_cuerpo().get("telefono", ""))
        return jsonify(servicios.pedidos.cancelar_por_cliente(pedido_id, telefono).a_dict())

    # --- Administración ----------------------------------------------------

    @api.get("/admin/sesion")
    @solo_admin
    def sesion_admin():
        return jsonify({"ok": True})

    @api.get("/admin/resumen")
    @solo_admin
    def resumen():
        return jsonify(servicios.reportes.resumen())

    @api.get("/admin/pedidos")
    @solo_admin
    def todos_los_pedidos():
        return jsonify([p.a_dict() for p in servicios.pedidos.historial(estado=request.args.get("estado", ""))])

    @api.patch("/admin/pedidos/<int:pedido_id>")
    @solo_admin
    def cambiar_estado(pedido_id: int):
        estado = str(_cuerpo().get("estado", ""))
        return jsonify(servicios.pedidos.cambiar_estado(pedido_id, estado).a_dict())

    @api.get("/admin/productos")
    @solo_admin
    def inventario():
        return jsonify([p.a_dict() for p in servicios.inventario.listar(request.args.get("q", ""))])

    @api.post("/admin/productos")
    @solo_admin
    def crear_producto():
        return jsonify(servicios.inventario.crear(_cuerpo()).a_dict()), 201

    @api.put("/admin/productos/<int:producto_id>")
    @solo_admin
    def actualizar_producto(producto_id: int):
        return jsonify(servicios.inventario.actualizar(producto_id, _cuerpo()).a_dict())

    @api.delete("/admin/productos/<int:producto_id>")
    @solo_admin
    def eliminar_producto(producto_id: int):
        servicios.inventario.eliminar(producto_id)
        return "", 204

    return api
