# domicilio.py
"""Tarifa de domicilio de MercaBarrio (valores en pesos colombianos).

Especificación de tarifa_domicilio(distancia_km, hora, cliente_frecuente):
    E1  La distancia se mide en km con un decimal. Solo se atiende si es mayor que 0
        y menor o igual a 8; si no, se lanza ValueError.
    E2  La hora es un entero de 0 a 23. Solo se atiende de 6 a 21 (ambas incluidas);
        si no, se lanza ValueError.
    E3  Tarifa base: hasta 2 km, 3.000; más de 2 y hasta 5 km, 5.000; más de 5 y
        hasta 8 km, 8.000.
    E4  Desde las 19 horas se suma un recargo nocturno de 1.500.
    E5  Un cliente frecuente a 2 km o menos no paga domicilio, a cualquier hora.

Este archivo es el código bajo prueba del Caso de estudio "Tipos de Pruebas y
Herramientas" (Sesión 13). Se conserva tal como lo entrega la guía.
"""


def tarifa_domicilio(distancia_km: float, hora: int, cliente_frecuente: bool) -> int:
    if distancia_km <= 0 or distancia_km > 8:
        raise ValueError("Distancia fuera de cobertura")
    if hora < 6 or hora > 21:
        raise ValueError("Fuera del horario de servicio")
    if distancia_km <= 2:
        tarifa = 3_000
    elif distancia_km <= 5:
        tarifa = 5_000
    else:
        tarifa = 8_000
    if hora >= 19:
        tarifa += 1_500
    if cliente_frecuente and distancia_km <= 2:
        tarifa = 0
    return tarifa
