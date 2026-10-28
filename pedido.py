# pedido.py
from dataclasses import dataclass

TASA_IVA = 0.19


@dataclass(frozen=True)
class Item:
    nombre: str
    precio: int
    cantidad: int
    gravado: bool = True


def total_pedido(items):
    subtotal = sum(i.precio * i.cantidad for i in items)
    base_gravada = sum(i.precio * i.cantidad for i in items if i.gravado)
    iva = base_gravada * TASA_IVA
    return round(subtotal + iva)
