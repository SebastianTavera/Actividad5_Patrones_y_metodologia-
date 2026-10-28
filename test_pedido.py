# test_pedido.py
# Lista de pruebas del kata, ordenada de lo más simple a lo más complejo.
# Los casos marcados con (*) son casos límite: valores justo en el umbral de una regla.
import pytest

from pedido import Item, total_pedido


# --- Lista de referencia del kata (pruebas 1 a 8) ---------------------------

def test_carrito_vacio_cuesta_cero():                      # 1 · R1
    assert total_pedido([]) == 0


def test_un_producto_exento():                             # 2 · R1, R2
    assert total_pedido([Item("arroz", 60_000, 1, gravado=False)]) == 60_000


def test_cantidad_multiplica_precio():                     # 3 · R1
    assert total_pedido([Item("arroz", 30_000, 2, gravado=False)]) == 60_000


def test_producto_gravado_paga_iva():                      # 4 · R2
    assert total_pedido([Item("gaseosa", 60_000, 1)]) == 71_400


def test_cobro_de_domicilio_bajo_el_umbral():              # 5 · R4
    assert total_pedido([Item("arroz", 20_000, 1, gravado=False)]) == 24_000


def test_descuento_en_el_umbral():                         # 6 · R3 (*)
    assert total_pedido([Item("arroz", 100_000, 1, gravado=False)]) == 90_000

