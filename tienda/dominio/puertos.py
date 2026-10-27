"""Puertos (interfaces) de los que dependen los servicios.

Inversión de dependencias (D): los servicios conocen estas abstracciones, nunca
SQLite. Segregación de interfaces (I): lectura de catálogo, escritura de
inventario y pedidos son contratos separados; cada servicio pide solo lo que usa.
"""
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Protocol

from pedido import Desglose, Item

from .modelos import EstadoPedido, Pedido, Producto


class CatalogoLectura(ABC):
    @abstractmethod
    def listar(self, texto: str = "", categoria: str = "", solo_activos: bool = True) -> list[Producto]: ...

    @abstractmethod
    def obtener(self, producto_id: int) -> Producto | None: ...

    @abstractmethod
    def categorias(self) -> list[str]: ...


class InventarioEscritura(ABC):
    @abstractmethod
    def guardar(self, producto: Producto) -> Producto: ...

    @abstractmethod
    def desactivar(self, producto_id: int) -> bool: ...

    @abstractmethod
    def ajustar_stock(self, producto_id: int, delta: int) -> None: ...


class RepositorioPedidos(ABC):
    @abstractmethod
    def guardar(self, pedido: Pedido) -> Pedido: ...

    @abstractmethod
    def obtener(self, pedido_id: int) -> Pedido | None: ...

    @abstractmethod
    def listar(self, telefono: str = "", estado: str = "") -> list[Pedido]: ...

    @abstractmethod
    def cambiar_estado(self, pedido_id: int, estado: EstadoPedido) -> None: ...


class UnidadDeTrabajo(Protocol):
    """Agrupa varias escrituras en una sola transacción atómica."""

    def transaccion(self) -> AbstractContextManager: ...


class CalculadoraTotal(Protocol):
    """Cualquier función que convierta ítems en un desglose (por defecto, pedido.desglose_pedido)."""

    def __call__(self, items: list[Item]) -> Desglose: ...
