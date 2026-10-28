# pedido.py
from dataclasses import dataclass

TASA_IVA = 0.19
UMBRAL_DOMICILIO = 50_000
COSTO_DOMICILIO = 4_000


@dataclass(frozen=True)
class Item:
    nombre: str
    precio: int
    cantidad: int
    gravado: bool = True


def total_pedido(items):
    if not items:
        return 0
    subtotal = sum(i.precio * i.cantidad for i in items)
    base_gravada = sum(i.precio * i.cantidad for i in items if i.gravado)
    iva = base_gravada * TASA_IVA
    domicilio = COSTO_DOMICILIO if subtotal < UMBRAL_DOMICILIO else 0
    return round(subtotal + iva + domicilio)
