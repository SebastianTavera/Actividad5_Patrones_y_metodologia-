from ..dominio.errores import NoEncontrado
from ..dominio.modelos import Producto
from ..dominio.puertos import CatalogoLectura

ORDENES = {
    "relevancia": lambda p: p.id,
    "precio_asc": lambda p: p.precio,
    "precio_desc": lambda p: -p.precio,
    "nombre": lambda p: p.nombre.lower(),
    "calificacion": lambda p: (-p.calificacion, -p.resenas),
    "descuento": lambda p: (-p.descuento_pct, p.precio),
}


class CatalogoServicio:
    """Consulta del catálogo para los clientes. Solo lee (no conoce el inventario)."""

    def __init__(self, catalogo: CatalogoLectura):
        self._catalogo = catalogo

    def buscar(self, texto: str = "", categoria: str = "", orden: str = "relevancia",
               impuesto: str = "") -> list[Producto]:
        productos = self._catalogo.listar(texto=texto.strip(), categoria=categoria)
        if impuesto == "exento":
            productos = [p for p in productos if not p.gravado]
        elif impuesto == "gravado":
            productos = [p for p in productos if p.gravado]
        return sorted(productos, key=ORDENES.get(orden, ORDENES["relevancia"]))

    def detalle(self, producto_id: int) -> Producto:
        producto = self._catalogo.obtener(producto_id)
        if producto is None or not producto.activo:
            raise NoEncontrado(f"El producto {producto_id} no existe")
        return producto

    def categorias(self) -> list[str]:
        return self._catalogo.categorias()
