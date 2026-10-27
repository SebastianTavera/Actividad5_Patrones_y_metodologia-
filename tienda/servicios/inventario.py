from ..dominio.errores import DatosInvalidos, NoEncontrado
from ..dominio.modelos import Producto
from ..dominio.puertos import CatalogoLectura, InventarioEscritura

CAMPOS_EDITABLES = ("nombre", "precio", "categoria", "gravado", "stock", "descripcion", "unidad")


def producto_desde_dict(datos: dict, base: Producto | None = None) -> Producto:
    if not isinstance(datos, dict):
        raise DatosInvalidos("Se esperaba un objeto con los datos del producto")
    valores = base.a_dict() if base else {"id": None, "activo": True, "descripcion": "", "unidad": "und",
                                          "gravado": True, "stock": 0}
    for campo in CAMPOS_EDITABLES:
        if campo in datos:
            valores[campo] = datos[campo]
    try:
        return Producto(
            id=valores["id"], nombre=str(valores.get("nombre", "")).strip(),
            precio=int(valores.get("precio", 0)), categoria=str(valores.get("categoria", "")).strip(),
            gravado=bool(valores["gravado"]), stock=int(valores["stock"]),
            descripcion=str(valores["descripcion"]).strip(), unidad=str(valores["unidad"]).strip() or "und",
            activo=valores["activo"],
        )
    except (TypeError, ValueError):
        raise DatosInvalidos("Precio y stock deben ser números enteros") from None


class InventarioServicio:
    """Administración del catálogo: altas, cambios y bajas de productos."""

    def __init__(self, catalogo: CatalogoLectura, inventario: InventarioEscritura):
        self._catalogo = catalogo
        self._inventario = inventario

    def listar(self, texto: str = "") -> list[Producto]:
        return self._catalogo.listar(texto=texto, solo_activos=True)

    def crear(self, datos: dict) -> Producto:
        producto = producto_desde_dict(datos)
        producto.validar()
        return self._inventario.guardar(producto)

    def actualizar(self, producto_id: int, datos: dict) -> Producto:
        actual = self._catalogo.obtener(producto_id)
        if actual is None or not actual.activo:
            raise NoEncontrado(f"El producto {producto_id} no existe")
        producto = producto_desde_dict(datos, base=actual)
        producto.validar()
        return self._inventario.guardar(producto)

    def eliminar(self, producto_id: int) -> None:
        if not self._inventario.desactivar(producto_id):
            raise NoEncontrado(f"El producto {producto_id} no existe")
