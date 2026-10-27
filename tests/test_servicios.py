"""Los servicios se prueban con dobles en memoria: no necesitan SQLite (principio D)."""
from contextlib import nullcontext

import pytest

from tienda.dominio.errores import (DatosInvalidos, NoEncontrado, StockInsuficiente,
                                    TransicionInvalida)
from tienda.dominio.modelos import Cliente, EstadoPedido, Producto
from tienda.dominio.puertos import CatalogoLectura, InventarioEscritura, RepositorioPedidos
from tienda.servicios.catalogo import CatalogoServicio
from tienda.servicios.cotizador import CotizadorServicio, Solicitud, leer_solicitudes
from tienda.servicios.inventario import InventarioServicio
from tienda.servicios.pedidos import PedidosServicio
from tienda.servicios.reportes import ReportesServicio


class ProductosEnMemoria(CatalogoLectura, InventarioEscritura):
    def __init__(self, productos):
        self.datos = {p.id: p for p in productos}

    def listar(self, texto="", categoria="", solo_activos=True):
        return [p for p in self.datos.values()
                if (not solo_activos or p.activo) and texto.lower() in p.nombre.lower()
                and (not categoria or p.categoria == categoria)]

    def obtener(self, producto_id):
        return self.datos.get(producto_id)

    def categorias(self):
        return sorted({p.categoria for p in self.datos.values()})

    def guardar(self, producto):
        if producto.id is None:
            producto.id = max(self.datos, default=0) + 1
        self.datos[producto.id] = producto
        return producto

    def desactivar(self, producto_id):
        if producto_id not in self.datos:
            return False
        self.datos[producto_id].activo = False
        return True

    def ajustar_stock(self, producto_id, delta):
        producto = self.datos[producto_id]
        if producto.stock + delta < 0:
            raise StockInsuficiente("sin stock")
        producto.stock += delta


class PedidosEnMemoria(RepositorioPedidos):
    def __init__(self):
        self.datos = {}

    def guardar(self, pedido):
        pedido.id = len(self.datos) + 1
        self.datos[pedido.id] = pedido
        return pedido

    def obtener(self, pedido_id):
        return self.datos.get(pedido_id)

    def listar(self, telefono="", estado=""):
        return [p for p in self.datos.values()
                if (not telefono or p.cliente.telefono == telefono) and (not estado or p.estado.value == estado)]

    def cambiar_estado(self, pedido_id, estado):
        self.datos[pedido_id].estado = estado


class UowFalsa:
    def transaccion(self):
        return nullcontext()


CLIENTE = Cliente("Ana Gómez", "310 555 1234", "Calle 45 # 12-30")


@pytest.fixture
def productos():
    return ProductosEnMemoria([
        Producto(1, "Arroz", 4_900, "Despensa", gravado=False, stock=10),
        Producto(2, "Gaseosa", 80_000, "Bebidas", gravado=True, stock=3),
        Producto(3, "Leche", 40_000, "Lácteos", gravado=False, stock=5),
    ])


@pytest.fixture
def pedidos_repo():
    return PedidosEnMemoria()


@pytest.fixture
def servicio_pedidos(productos, pedidos_repo):
    return PedidosServicio(CotizadorServicio(productos), productos, pedidos_repo, UowFalsa())


# --- Cotizador ---------------------------------------------------------------

def test_cotizar_usa_las_reglas_del_kata(productos):
    c = CotizadorServicio(productos).cotizar([Solicitud(2, 1), Solicitud(3, 1)])
    assert c.desglose.total == 121_680
    assert c.desglose.descuento == 12_000


def test_cotizar_informa_cuanto_falta_para_domicilio_gratis(productos):
    datos = CotizadorServicio(productos).cotizar([Solicitud(1, 2)]).a_dict()
    assert datos["domicilio"] == 4_000
    assert datos["metas"]["domicilio_gratis"]["faltante"] == 50_000 - 9_800


def test_cotizar_marca_productos_sin_stock_suficiente(productos):
    c = CotizadorServicio(productos).cotizar([Solicitud(2, 4)])
    assert c.sin_stock == [{"producto_id": 2, "nombre": "Gaseosa", "disponible": 3}]


def test_cotizar_cantidad_cero_es_dato_invalido(productos):
    with pytest.raises(DatosInvalidos, match="Arroz"):
        CotizadorServicio(productos).cotizar([Solicitud(1, 0)])


def test_cotizar_informa_productos_no_disponibles_sin_bloquear_el_carrito(productos):
    c = CotizadorServicio(productos).cotizar([Solicitud(1, 1), Solicitud(99, 1)])
    assert c.no_disponibles == [99]
    assert c.desglose.subtotal == 4_900


def test_no_se_puede_comprar_un_producto_retirado(servicio_pedidos, productos):
    productos.desactivar(1)
    with pytest.raises(NoEncontrado):
        servicio_pedidos.crear(CLIENTE, [Solicitud(1, 1)])


def test_cotizador_acepta_otra_calculadora(productos):
    """Abierto/cerrado: se puede cambiar la regla de precios sin tocar el servicio."""
    from pedido import Desglose
    fija = lambda items: Desglose(1, 0, 0, 0, 1)
    assert CotizadorServicio(productos, calcular=fija).cotizar([Solicitud(1, 1)]).desglose.total == 1


def test_leer_solicitudes_une_productos_repetidos():
    assert leer_solicitudes([{"producto_id": 1, "cantidad": 2}, {"producto_id": "1", "cantidad": 3}]) == [
        Solicitud(1, 5)]


def test_leer_solicitudes_rechaza_formato_invalido():
    with pytest.raises(DatosInvalidos):
        leer_solicitudes([{"producto_id": "x"}])


# --- Pedidos -----------------------------------------------------------------

def test_crear_pedido_descuenta_stock_y_normaliza_telefono(servicio_pedidos, productos):
    pedido = servicio_pedidos.crear(CLIENTE, [Solicitud(1, 4)])
    assert pedido.total == 4_900 * 4 + 4_000
    assert pedido.cliente.telefono == "3105551234"
    assert productos.obtener(1).stock == 6


def test_crear_pedido_sin_stock_no_toca_inventario(servicio_pedidos, productos):
    with pytest.raises(StockInsuficiente, match="Gaseosa"):
        servicio_pedidos.crear(CLIENTE, [Solicitud(1, 1), Solicitud(2, 4)])
    assert productos.obtener(1).stock == 10


def test_crear_pedido_con_carrito_vacio(servicio_pedidos):
    with pytest.raises(DatosInvalidos):
        servicio_pedidos.crear(CLIENTE, [])


def test_crear_pedido_valida_datos_del_cliente(servicio_pedidos):
    with pytest.raises(DatosInvalidos, match="teléfono"):
        servicio_pedidos.crear(Cliente("Ana Gómez", "12", "Calle 45 # 12-30"), [Solicitud(1, 1)])


def test_cancelar_devuelve_el_stock(servicio_pedidos, productos):
    pedido = servicio_pedidos.crear(CLIENTE, [Solicitud(1, 4)])
    servicio_pedidos.cambiar_estado(pedido.id, "cancelado")
    assert productos.obtener(1).stock == 10


def test_ciclo_de_vida_del_pedido(servicio_pedidos):
    pedido = servicio_pedidos.crear(CLIENTE, [Solicitud(1, 1)])
    for estado in ("preparando", "en_camino", "entregado"):
        pedido = servicio_pedidos.cambiar_estado(pedido.id, estado)
    assert pedido.estado is EstadoPedido.ENTREGADO


def test_pedido_entregado_no_se_puede_cancelar(servicio_pedidos):
    pedido = servicio_pedidos.crear(CLIENTE, [Solicitud(1, 1)])
    for estado in ("preparando", "en_camino", "entregado"):
        servicio_pedidos.cambiar_estado(pedido.id, estado)
    with pytest.raises(TransicionInvalida):
        servicio_pedidos.cambiar_estado(pedido.id, "cancelado")


def test_cliente_solo_cancela_sus_pedidos(servicio_pedidos):
    pedido = servicio_pedidos.crear(CLIENTE, [Solicitud(1, 1)])
    with pytest.raises(NoEncontrado):
        servicio_pedidos.cancelar_por_cliente(pedido.id, "3000000000")
    assert servicio_pedidos.cancelar_por_cliente(pedido.id, "310-555-1234").estado is EstadoPedido.CANCELADO


def test_historial_por_telefono(servicio_pedidos):
    servicio_pedidos.crear(CLIENTE, [Solicitud(1, 1)])
    assert len(servicio_pedidos.historial(telefono="(310) 555 1234")) == 1
    assert servicio_pedidos.historial(telefono="3000000000") == []


# --- Catálogo, inventario y reportes ----------------------------------------

def test_catalogo_filtra_por_impuesto_y_ordena(productos):
    servicio = CatalogoServicio(productos)
    assert [p.nombre for p in servicio.buscar(impuesto="exento", orden="precio_desc")] == ["Leche", "Arroz"]


def test_catalogo_detalle_de_producto_inactivo(productos):
    productos.desactivar(1)
    with pytest.raises(NoEncontrado):
        CatalogoServicio(productos).detalle(1)


def test_inventario_crea_y_valida(productos):
    servicio = InventarioServicio(productos, productos)
    nuevo = servicio.crear({"nombre": "Sal", "precio": 1_800, "categoria": "Despensa", "gravado": False})
    assert nuevo.id == 4 and nuevo.stock == 0
    with pytest.raises(DatosInvalidos, match="precio"):
        servicio.crear({"nombre": "Gratis", "precio": 0, "categoria": "Despensa"})


def test_inventario_actualiza_parcialmente(productos):
    actualizado = InventarioServicio(productos, productos).actualizar(1, {"stock": 99})
    assert (actualizado.nombre, actualizado.stock) == ("Arroz", 99)


def test_reportes_excluyen_cancelados(servicio_pedidos, productos, pedidos_repo):
    servicio_pedidos.crear(CLIENTE, [Solicitud(3, 2)])
    cancelado = servicio_pedidos.crear(CLIENTE, [Solicitud(1, 1)])
    servicio_pedidos.cambiar_estado(cancelado.id, "cancelado")
    resumen = ReportesServicio(productos, pedidos_repo).resumen()
    assert resumen["pedidos"] == 1
    assert resumen["ingresos"] == 80_000
    assert resumen["mas_vendidos"] == [{"nombre": "Leche", "unidades": 2}]
