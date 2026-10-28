# pedido.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    nombre: str
    precio: int
    cantidad: int
    gravado: bool = True


def total_pedido(items):
    return 0
