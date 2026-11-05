from collections import Counter

from ..dominio.modelos import EstadoPedido
from ..dominio.puertos import CatalogoLectura, RepositorioPedidos

STOCK_BAJO = 10


class ReportesServicio:
    """Indicadores del panel de administración."""

    def __init__(self, catalogo: CatalogoLectura, pedidos: RepositorioPedidos):
        self._catalogo = catalogo
        self._pedidos = pedidos

    def resumen(self) -> dict:
        pedidos = self._pedidos.listar()
        validos = [p for p in pedidos if p.estado is not EstadoPedido.CANCELADO]
        ingresos = sum(p.total for p in validos)
        vendidos = Counter()
        for p in validos:
            for l in p.lineas:
                vendidos[l.nombre] += l.cantidad
        por_estado = Counter(p.estado.value for p in pedidos)
        return {
            "pedidos": len(validos),
            "ingresos": ingresos,
            "ticket_promedio": round(ingresos / len(validos)) if validos else 0,
            "iva_recaudado": sum(p.iva for p in validos),
            "pendientes": por_estado["recibido"] + por_estado["preparando"] + por_estado["en_camino"],
            "por_estado": {e.value: por_estado[e.value] for e in EstadoPedido},
            "mas_vendidos": [{"nombre": n, "unidades": u} for n, u in vendidos.most_common(5)],
            "stock_bajo": [p.a_dict() for p in self._catalogo.listar() if p.stock < STOCK_BAJO],
        }
