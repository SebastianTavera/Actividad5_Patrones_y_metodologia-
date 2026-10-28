# test_pedido.py
# Lista de pruebas del kata, ordenada de lo más simple a lo más complejo.
# Los casos marcados con (*) son casos límite: valores justo en el umbral de una regla.
import pytest

from pedido import Item, desglose_pedido, precio_publico, total_pedido


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


def test_pedido_mixto_descuento_antes_del_iva():           # 7 · R2 + R3
    items = [Item("gaseosa", 80_000, 1), Item("arroz", 40_000, 1, gravado=False)]
    assert total_pedido(items) == 121_680


def test_cantidad_cero_es_invalida():                      # 8 · R5 (*)
    with pytest.raises(ValueError):
        total_pedido([Item("arroz", 10_000, 0, gravado=False)])


# --- Casos límite propios (los que la lista de referencia no tenía) ---------

def test_domicilio_gratis_en_el_umbral_exacto():           # 9 · R4 (*) mata al mutante M2
    assert total_pedido([Item("arroz", 50_000, 1, gravado=False)]) == 50_000


def test_justo_bajo_el_umbral_de_domicilio():              # 10 · R4 (*)
    assert total_pedido([Item("arroz", 49_999, 1, gravado=False)]) == 53_999


def test_justo_bajo_el_umbral_de_descuento():              # 11 · R3 (*) refuerza M1
    assert total_pedido([Item("arroz", 99_999, 1, gravado=False)]) == 99_999


def test_descuento_en_el_umbral_con_producto_gravado():    # 12 · R2 + R3 (*)
    assert total_pedido([Item("licuadora", 100_000, 1)]) == 107_100


def test_redondeo_al_peso_mas_cercano():                   # 13 · R6
    # 10.001 + 1.900,19 de IVA + 4.000 de domicilio = 15.901,19 -> 15.901
    assert total_pedido([Item("jabon", 10_001, 1)]) == 15_901


def test_redondeo_hacia_arriba_desde_medio_peso():         # 14 · R6 (*)
    # 50.150 + 9.528,5 de IVA = 59.678,5 -> 59.679 (redondeo comercial).
    # round() de Python usa redondeo bancario y daría 59.678.
    assert total_pedido([Item("aceite", 50_150, 1)]) == 59_679


def test_varios_items_gravados_con_cantidad():             # 15 · R1 + R2 + R4
    items = [Item("gaseosa", 5_000, 3), Item("galletas", 2_000, 4)]
    assert total_pedido(items) == 31_370


def test_cantidad_negativa_es_invalida():                  # 16 · R5
    with pytest.raises(ValueError):
        total_pedido([Item("arroz", 10_000, -2, gravado=False)])


def test_item_invalido_entre_validos_rechaza_todo():       # 17 · R5
    with pytest.raises(ValueError):
        total_pedido([Item("arroz", 10_000, 1, gravado=False), Item("pan", 3_000, 0)])


def test_error_nombra_el_producto_invalido():              # 18 · R5
    with pytest.raises(ValueError, match="pan"):
        total_pedido([Item("pan", 3_000, 0)])


# --- Desglose: el mismo cálculo explicado línea por línea (lo usa la tienda) -

def test_desglose_de_pedido_mixto():                       # 19
    items = [Item("gaseosa", 80_000, 1), Item("arroz", 40_000, 1, gravado=False)]
    d = desglose_pedido(items)
    assert (d.subtotal, d.descuento, d.iva, d.domicilio, d.total) == (
        120_000, 12_000, 13_680, 0, 121_680,
    )


def test_desglose_de_carrito_vacio_es_todo_cero():         # 20
    d = desglose_pedido([])
    assert (d.subtotal, d.descuento, d.iva, d.domicilio, d.total) == (0, 0, 0, 0, 0)


# --- Precio que ve el cliente: IVA incluido, redondeado al peso -------------

def test_precio_publico_de_producto_exento_no_cambia():   # 21 · R2
    assert precio_publico(4_900, gravado=False) == 4_900
