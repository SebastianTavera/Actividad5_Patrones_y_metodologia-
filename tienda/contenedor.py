"""Raíz de composición: el único lugar que conoce las implementaciones concretas."""
from dataclasses import dataclass

from .infraestructura.semilla import sembrar_si_vacio
from .infraestructura.sqlite import BaseDeDatos, SqlitePedidos, SqliteProductos
from .servicios.catalogo import CatalogoServicio
from .servicios.cotizador import CotizadorServicio
from .servicios.inventario import InventarioServicio
from .servicios.pedidos import PedidosServicio
from .servicios.reportes import ReportesServicio


@dataclass(frozen=True)
class Servicios:
    catalogo: CatalogoServicio
    cotizador: CotizadorServicio
    pedidos: PedidosServicio
    inventario: InventarioServicio
    reportes: ReportesServicio


def construir_servicios(ruta_db: str, sembrar: bool = True) -> Servicios:
    db = BaseDeDatos(ruta_db)
    if sembrar:
        sembrar_si_vacio(db)
    productos = SqliteProductos(db)
    pedidos = SqlitePedidos(db)
    cotizador = CotizadorServicio(productos)
    return Servicios(
        catalogo=CatalogoServicio(productos),
        cotizador=cotizador,
        pedidos=PedidosServicio(cotizador, productos, pedidos, db),
        inventario=InventarioServicio(productos, productos),
        reportes=ReportesServicio(productos, pedidos),
    )
