# domicilio_equipo_ejemplo.py
"""Versión de EJEMPLO de la función que "el desarrollador quería publicar".

La guía dice que el docente entrega el archivo real (domicilio_equipo.py). Mientras
no se tenga, este archivo sirve para ensayar la prueba de fuego: contiene dos defectos
sembrados en comparaciones de frontera, que no cambian ninguna rama del código.
Si el docente entrega su archivo, se usa ese y se ignora este.

Defectos respecto a domicilio.py (compárense con `diff`):
    D-A  `elif distancia_km <= 5`  ->  `elif distancia_km < 5`    (5 km cobra 8.000)
    D-B  `if hora >= 19`           ->  `if hora > 19`             (a las 19 h no hay recargo)
"""


def tarifa_domicilio(distancia_km: float, hora: int, cliente_frecuente: bool) -> int:
    if distancia_km <= 0 or distancia_km > 8:
        raise ValueError("Distancia fuera de cobertura")
    if hora < 6 or hora > 21:
        raise ValueError("Fuera del horario de servicio")
    if distancia_km <= 2:
        tarifa = 3_000
    elif distancia_km < 5:
        tarifa = 5_000
    else:
        tarifa = 8_000
    if hora > 19:
        tarifa += 1_500
    if cliente_frecuente and distancia_km <= 2:
        tarifa = 0
    return tarifa
