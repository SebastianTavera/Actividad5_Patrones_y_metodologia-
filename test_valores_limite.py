"""Paso 2 · Caja negra: análisis de valores límite.

Por cada frontera se prueba el valor exacto y el valor a un paso del otro lado
(0,1 km para la distancia; 1 hora para la hora). Las fronteras 2, 5 y 8 km
pertenecen al tramo de su izquierda; 0 km queda fuera de cobertura.

Valores neutros: hora 10 y no frecuente al probar la distancia; 1 km y no
frecuente al probar la hora.
"""
import pytest

from domicilio import tarifa_domicilio

ERROR = ValueError

# (id, variable, frontera, distancia, hora, frecuente, esperado)
CASOS = [
    # Distancia (hora 10, no frecuente)
    ("VL-1", "distancia_km", 0, 0, 10, False, ERROR),
    ("VL-2", "distancia_km", 0, 0.1, 10, False, 3_000),
    ("VL-3", "distancia_km", 2, 2, 10, False, 3_000),
    ("VL-4", "distancia_km", 2, 2.1, 10, False, 5_000),
    ("VL-5", "distancia_km", 5, 5, 10, False, 5_000),
    ("VL-6", "distancia_km", 5, 5.1, 10, False, 8_000),
    ("VL-7", "distancia_km", 8, 8, 10, False, 8_000),
    ("VL-8", "distancia_km", 8, 8.1, 10, False, ERROR),
    # Hora (1 km, no frecuente)
    ("VL-9", "hora", 6, 1, 5, False, ERROR),
    ("VL-10", "hora", 6, 1, 6, False, 3_000),
    ("VL-11", "hora", 19, 1, 18, False, 3_000),
    ("VL-12", "hora", 19, 1, 19, False, 3_000 + 1_500),
    ("VL-13", "hora", 21, 1, 21, False, 3_000 + 1_500),
    ("VL-14", "hora", 21, 1, 22, False, ERROR),
    # Frontera de E5: cliente frecuente a 2 km (hora 10)
    ("VL-15", "distancia_km (frecuente)", 2, 2, 10, True, 0),
    ("VL-16", "distancia_km (frecuente)", 2, 2.1, 10, True, 5_000),
]


@pytest.mark.parametrize("caso,variable,frontera,distancia,hora,frecuente,esperado", CASOS,
                         ids=[c[0] for c in CASOS])
def test_valor_limite(caso, variable, frontera, distancia, hora, frecuente, esperado):
    if esperado is ERROR:
        with pytest.raises(ValueError):
            tarifa_domicilio(distancia, hora, frecuente)
    else:
        assert tarifa_domicilio(distancia, hora, frecuente) == esperado
