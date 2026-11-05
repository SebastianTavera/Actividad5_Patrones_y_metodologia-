"""Paso 1 · Caja negra: partición de equivalencia (solo desde la especificación).

Clases (representante del centro de cada clase, lejos de las fronteras):

    ID   Variable           Clase                         Tipo      Representante
    C1   distancia_km       d <= 0                        Inválida  -2.5
    C2   distancia_km       0 < d <= 2                    Válida    1.0
    C3   distancia_km       2 < d <= 5                    Válida    3.5
    C4   distancia_km       5 < d <= 8                    Válida    6.5
    C5   distancia_km       d > 8                         Inválida  12.0
    C6   hora               h < 6                         Inválida  3
    C7   hora               6 <= h <= 18 (sin recargo)    Válida    12
    C8   hora               19 <= h <= 21 (con recargo)   Válida    20
    C9   hora               h > 21                        Inválida  23
    C10  cliente_frecuente  Es frecuente                  Válida    True
    C11  cliente_frecuente  No es frecuente               Válida    False

Reglas de combinación: un caso puede cubrir varias clases válidas; cada caso cubre
como máximo una clase inválida (si se mezclan dos, el primer error oculta el segundo).
"""
import pytest

from domicilio import tarifa_domicilio

# (id, distancia, hora, frecuente, clases que cubre, resultado esperado)
CASOS_VALIDOS = [
    ("EP-1", 1.0, 12, False, "C2, C7, C11", 3_000),
    ("EP-2", 3.5, 20, False, "C3, C8, C11", 5_000 + 1_500),
    ("EP-3", 6.5, 10, True, "C4, C7, C10", 8_000),          # frecuente, pero a más de 2 km
    ("EP-4", 1.0, 15, True, "C2, C7, C10", 0),              # E5: combinación frecuente + <= 2 km
]

CASOS_INVALIDOS = [
    ("EP-5", -2.5, 12, False, "C1"),
    ("EP-6", 12.0, 12, False, "C5"),
    ("EP-7", 3.5, 3, False, "C6"),
    ("EP-8", 3.5, 23, False, "C9"),
]


@pytest.mark.parametrize("caso,distancia,hora,frecuente,clases,esperado", CASOS_VALIDOS,
                         ids=[c[0] for c in CASOS_VALIDOS])
def test_clases_validas(caso, distancia, hora, frecuente, clases, esperado):
    assert tarifa_domicilio(distancia, hora, frecuente) == esperado


@pytest.mark.parametrize("caso,distancia,hora,frecuente,clases", CASOS_INVALIDOS,
                         ids=[c[0] for c in CASOS_INVALIDOS])
def test_clases_invalidas(caso, distancia, hora, frecuente, clases):
    with pytest.raises(ValueError):
        tarifa_domicilio(distancia, hora, frecuente)
