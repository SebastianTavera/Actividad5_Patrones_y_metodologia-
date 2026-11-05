from ..dominio.errores import DatosInvalidos, NoEncontrado, StockInsuficiente, TransicionInvalida
from ..dominio.modelos import Cliente, EstadoPedido, Pedido
from ..dominio.puertos import InventarioEscritura, RepositorioPedidos, UnidadDeTrabajo
from .cotizador import CotizadorServicio, Solicitud


class PedidosServicio:
    """Checkout y ciclo de vida de los pedidos."""

    def __init__(self, cotizador: CotizadorServicio, inventario: InventarioEscritura,
                 pedidos: RepositorioPedidos, uow: UnidadDeTrabajo):
        self._cotizador = cotizador
        self._inventario = inventario
        self._pedidos = pedidos
        self._uow = uow

    def crear(self, cliente: Cliente, solicitudes: list[Solicitud], notas: str = "") -> Pedido:
        cliente.validar()
        cliente = Cliente(cliente.nombre.strip(), _digitos(cliente.telefono), cliente.direccion.strip())
        if not solicitudes:
            raise DatosInvalidos("El carrito está vacío")
        with self._uow.transaccion():
            cotizacion = self._cotizador.cotizar(solicitudes)
            if cotizacion.no_disponibles:
                raise NoEncontrado("Algunos productos de tu carrito ya no están disponibles")
            if cotizacion.sin_stock:
                faltan = ", ".join(f"{p['nombre']} (quedan {p['disponible']})"
                                   for p in cotizacion.sin_stock)
                raise StockInsuficiente(f"No hay unidades suficientes: {faltan}")
            for linea in cotizacion.lineas:
                self._inventario.ajustar_stock(linea.producto_id, -linea.cantidad)
            d = cotizacion.desglose
            return self._pedidos.guardar(Pedido(
                id=None, cliente=cliente, lineas=cotizacion.lineas,
                subtotal=d.subtotal, descuento=d.descuento, iva=d.iva,
                domicilio=d.domicilio, total=d.total, notas=notas.strip()[:280],
            ))

    def consultar(self, pedido_id: int) -> Pedido:
        pedido = self._pedidos.obtener(pedido_id)
        if pedido is None:
            raise NoEncontrado(f"El pedido {pedido_id} no existe")
        return pedido

    def historial(self, telefono: str = "", estado: str = "") -> list[Pedido]:
        return self._pedidos.listar(telefono=_digitos(telefono), estado=estado)

    def cambiar_estado(self, pedido_id: int, estado: str) -> Pedido:
        try:
            nuevo = EstadoPedido(estado)
        except ValueError:
            raise DatosInvalidos(f"Estado desconocido: {estado}") from None
        with self._uow.transaccion():
            pedido = self.consultar(pedido_id)
            if not pedido.puede_pasar_a(nuevo):
                raise TransicionInvalida(
                    f"Un pedido {pedido.estado.value} no puede pasar a {nuevo.value}")
            if nuevo is EstadoPedido.CANCELADO:
                for linea in pedido.lineas:
                    self._inventario.ajustar_stock(linea.producto_id, linea.cantidad)
            self._pedidos.cambiar_estado(pedido_id, nuevo)
        return self.consultar(pedido_id)

    def cancelar_por_cliente(self, pedido_id: int, telefono: str) -> Pedido:
        pedido = self.consultar(pedido_id)
        if _digitos(pedido.cliente.telefono) != _digitos(telefono):
            raise NoEncontrado(f"El pedido {pedido_id} no existe")
        return self.cambiar_estado(pedido_id, EstadoPedido.CANCELADO.value)


def _digitos(texto: str) -> str:
    return "".join(c for c in texto if c.isdigit())
