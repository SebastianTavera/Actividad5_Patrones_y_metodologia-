from dataclasses import dataclass, field

import pedido as reglas
from pedido import Desglose, Item

from ..dominio.errores import DatosInvalidos
from ..dominio.modelos import LineaPedido
from ..dominio.puertos import CalculadoraTotal, CatalogoLectura


@dataclass(frozen=True)
class Solicitud:
    producto_id: int
    cantidad: int


@dataclass(frozen=True)
class Cotizacion:
    lineas: list[LineaPedido]
    desglose: Desglose
    sin_stock: list[dict]
    categorias: dict[int, str] = field(default_factory=dict)
    no_disponibles: list[int] = field(default_factory=list)

    def a_dict(self) -> dict:
        d = self.desglose
        subtotal = d.subtotal
        return {
            "lineas": [{"producto_id": l.producto_id, "nombre": l.nombre, "precio": l.precio,
                        "cantidad": l.cantidad, "gravado": l.gravado, "importe": l.importe,
                        "precio_final": reglas.precio_publico(l.precio, l.gravado),
                        "importe_final": reglas.precio_publico(l.importe, l.gravado),
                        "categoria": self.categorias.get(l.producto_id, "")}
                       for l in self.lineas],
            "subtotal": d.subtotal, "descuento": d.descuento, "iva": d.iva,
            "domicilio": d.domicilio, "total": d.total,
            "metas": {
                "domicilio_gratis": _meta(subtotal, reglas.UMBRAL_DOMICILIO),
                "descuento": _meta(subtotal, reglas.UMBRAL_DESCUENTO),
            },
            "sin_stock": self.sin_stock,
            "no_disponibles": self.no_disponibles,
        }


def _meta(subtotal: int, umbral: int) -> dict:
    return {"umbral": umbral, "faltante": max(umbral - subtotal, 0),
            "progreso": min(subtotal / umbral, 1) if umbral else 1}


def leer_solicitudes(datos) -> list[Solicitud]:
    """Convierte el JSON del carrito en solicitudes, uniendo productos repetidos."""
    if not isinstance(datos, list):
        raise DatosInvalidos("El carrito debe ser una lista de productos")
    cantidades: dict[int, int] = {}
    for fila in datos:
        try:
            producto_id = int(fila["producto_id"])
            cantidad = int(fila["cantidad"])
        except (KeyError, TypeError, ValueError):
            raise DatosInvalidos("Cada producto necesita producto_id y cantidad enteros") from None
        cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad
    return [Solicitud(pid, cant) for pid, cant in cantidades.items()]


class CotizadorServicio:
    """Arma las líneas a partir del catálogo y delega el cálculo a las reglas de pedido.py."""

    def __init__(self, catalogo: CatalogoLectura, calcular: CalculadoraTotal = reglas.desglose_pedido):
        self._catalogo = catalogo
        self._calcular = calcular

    def cotizar(self, solicitudes: list[Solicitud]) -> Cotizacion:
        lineas, sin_stock, categorias, no_disponibles = [], [], {}, []
        for s in solicitudes:
            producto = self._catalogo.obtener(s.producto_id)
            if producto is None or not producto.activo:
                no_disponibles.append(s.producto_id)
                continue
            lineas.append(LineaPedido(producto.id, producto.nombre, producto.precio,
                                      s.cantidad, producto.gravado))
            categorias[producto.id] = producto.categoria
            if s.cantidad > producto.stock:
                sin_stock.append({"producto_id": producto.id, "nombre": producto.nombre,
                                  "disponible": producto.stock})
        items = [Item(l.nombre, l.precio, l.cantidad, l.gravado) for l in lineas]
        try:
            desglose = self._calcular(items)
        except ValueError as error:      # R5: cantidad <= 0
            raise DatosInvalidos(str(error)) from None
        return Cotizacion(lineas, desglose, sin_stock, categorias, no_disponibles)
