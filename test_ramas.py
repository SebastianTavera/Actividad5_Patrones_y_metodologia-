"""Paso 3.2 · Caja blanca: conjunto mínimo de casos para el 100 % de las ramas.

Tabla de ramas (6 decisiones, 12 ramas) y el caso que recorre cada una:

    Decisión                             Sí     No
    D1  distancia <= 0 or > 8            R-1    R-2, R-3, R-4, R-5
    D2  hora < 6 or > 21                 R-2    R-3, R-4, R-5
    D3  distancia <= 2                   R-3    R-4, R-5
    D4  distancia <= 5                   R-4    R-5
    D5  hora >= 19                       R-3    R-4, R-5
    D6  frecuente y distancia <= 2       R-3    R-4, R-5

Con 5 casos se marcan las 12 ramas: dos para las excepciones (cada una termina la
función) y tres caminos que llegan hasta el return.
"""
import pytest

from domicilio import tarifa_domicilio


def test_r1_distancia_fuera_de_cobertura():            # D1-sí
    with pytest.raises(ValueError):
        tarifa_domicilio(-1, 10, False)


def test_r2_fuera_del_horario():                       # D1-no, D2-sí
    with pytest.raises(ValueError):
        tarifa_domicilio(1, 3, False)


def test_r3_tramo_corto_nocturno_frecuente():          # D3-sí, D5-sí, D6-sí
    assert tarifa_domicilio(1, 20, True) == 0


def test_r4_tramo_medio_diurno():                      # D3-no, D4-sí, D5-no, D6-no
    assert tarifa_domicilio(3, 10, False) == 5_000


def test_r5_tramo_largo():                             # D4-no
    assert tarifa_domicilio(6, 10, False) == 8_000
