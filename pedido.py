# pedido.py
"""Cálculo del total de un pedido de MercaBarrio (valores en pesos colombianos).

Reglas de negocio:
    R1  Subtotal = suma de precio x cantidad. Un carrito vacío cuesta 0.
    R2  Los productos gravados pagan IVA del 19 %; los de canasta básica están exentos.
    R3  Si el subtotal es de 100.000 o más, se descuenta el 10 % antes de calcular el IVA.
    R4  Si el subtotal es menor a 50.000 se cobra domicilio de 4.000; desde 50.000 es gratis.
    R5  Una cantidad menor o igual a 0 es inválida y se rechaza con ValueError.
    R6  El total se redondea al peso más cercano.
"""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

TASA_IVA = Decimal("0.19")
UMBRAL_DESCUENTO = 100_000
TASA_DESCUENTO = Decimal("0.10")
UMBRAL_DOMICILIO = 50_000
COSTO_DOMICILIO = 4_000


@dataclass(frozen=True)
class Item:
    nombre: str
    precio: int
    cantidad: int
    gravado: bool = True


def _al_peso(valor: Decimal) -> int:
    return int(valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _validar_cantidades(items: list[Item]) -> None:
    for item in items:
        if item.cantidad <= 0:
            raise ValueError(f"Cantidad inválida para {item.nombre}")


def _tasa_descuento(subtotal: int) -> Decimal:
    return TASA_DESCUENTO if subtotal >= UMBRAL_DESCUENTO else Decimal(0)


def _domicilio(subtotal: int) -> int:
    return COSTO_DOMICILIO if subtotal < UMBRAL_DOMICILIO else 0


def total_pedido(items: list[Item]) -> int:
    if not items:
        return 0
    _validar_cantidades(items)

    subtotal = sum(i.precio * i.cantidad for i in items)
    base_gravada = sum(i.precio * i.cantidad for i in items if i.gravado)
    tasa = _tasa_descuento(subtotal)
    descuento = subtotal * tasa
    iva = base_gravada * (1 - tasa) * TASA_IVA
    domicilio = _domicilio(subtotal)
    return _al_peso(subtotal - descuento + iva + domicilio)
