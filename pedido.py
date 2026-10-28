# pedido.py
from dataclasses import dataclass

TASA_IVA = 0.19
UMBRAL_DESCUENTO = 100_000
TASA_DESCUENTO = 0.10
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
    tasa = TASA_DESCUENTO if subtotal >= UMBRAL_DESCUENTO else 0
    descuento = subtotal * tasa
    iva = base_gravada * (1 - tasa) * TASA_IVA
    domicilio = COSTO_DOMICILIO if subtotal < UMBRAL_DOMICILIO else 0
    return round(subtotal - descuento + iva + domicilio)
