# pedido.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    nombre: str
    precio: int
    cantidad: int
    gravado: bool = True


def total_pedido(items):
    subtotal = sum(i.precio * i.cantidad for i in items)
    base_gravada = sum(i.precio * i.cantidad for i in items if i.gravado)
    return round(subtotal + base_gravada * 0.19)
