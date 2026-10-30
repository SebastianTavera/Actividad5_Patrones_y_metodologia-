# test_suite_oculta.py
# Suite de aceptación entregada por el docente en el Paso 4 (copiada sin cambios).
import pytest
from pedido import Item, total_pedido

def test_limite_domicilio_exacto():
    assert total_pedido([Item("arroz", 50_000, 1, gravado=False)]) == 50_000

def test_justo_bajo_limite_domicilio():
    assert total_pedido([Item("arroz", 49_999, 1, gravado=False)]) == 53_999

def test_limite_descuento_exacto_gravado():
    assert total_pedido([Item("licuadora", 100_000, 1)]) == 107_100

def test_justo_bajo_limite_descuento():
    assert total_pedido([Item("arroz", 99_999, 1, gravado=False)]) == 99_999

def test_redondeo_al_peso():
    assert total_pedido([Item("jabon", 10_001, 1)]) == 15_901

def test_varios_items_gravados_cantidad():
    assert total_pedido([Item("gaseosa", 5_000, 3), Item("galletas", 2_000, 4)]) == 31_370

def test_cantidad_negativa():
    with pytest.raises(ValueError):
        total_pedido([Item("arroz", 10_000, -2, gravado=False)])

def test_item_invalido_entre_validos():
    with pytest.raises(ValueError):
        total_pedido([Item("arroz", 10_000, 1, gravado=False), Item("pan", 3_000, 0)])
