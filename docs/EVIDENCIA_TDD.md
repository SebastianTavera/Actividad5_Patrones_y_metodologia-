# Evidencia TDD del kata `total_pedido`

Esta rama reconstruye el kata **un commit por cada paso del ciclo** rojo → verde → refactorizar.
En cada commit se ejecutó `python -m pytest -q test_pedido.py` y la salida real quedó en el mensaje
del commit (`git log` la muestra completa).

Convención de los mensajes:

- `ROJO prueba n` — se agrega la prueba n antes del código y se ve fallar.
- `VERDE prueba n` — el código mínimo que la hace pasar, con todas las anteriores en verde.
- `REFACTOR tras prueba n` — mejora de diseño sin cambiar comportamiento, todo en verde.
- `PRUEBA n (caso límite…)` — caso límite que el código ya cumplía. La guía pide preguntarse si
  prueba algo nuevo: estos fijan los bordes de las reglas y matan mutantes (la prueba 9 mata a M2).

## Resumen por prueba

| # | Prueba | ¿Se vio fallar? | Resultado en rojo | Resultado en verde | Refactorización |
|---|---|---|---|---|---|
| 1 | carrito vacío cuesta 0 (R1) | Sí, falló primero | 1 error | 1 passed | No |
| 2 | un producto exento (R1, R2) | Sí, falló primero | 1 failed, 1 passed | 2 passed | No |
| 3 | la cantidad multiplica el precio (R1) | Sí, falló primero | 1 failed, 2 passed | 3 passed | No |
| 4 | producto gravado paga IVA 19 % (R2) | Sí, falló primero | 1 failed, 3 passed | 4 passed | Sí: Extraer la constante TASA_IVA y la variable iva. |
| 5 | cobro de domicilio bajo 50.000 (R4) | Sí, falló primero | 1 failed, 4 passed | 5 passed | Sí: Constantes UMBRAL_DOMICILIO y COSTO_DOMICILIO. |
| 6 | descuento del 10 % en el umbral de 100.000 (R3) | Sí, falló primero | 1 failed, 5 passed | 6 passed | Sí: Constantes UMBRAL_DESCUENTO y TASA_DESCUENTO. |
| 7 | pedido mixto: descuento antes del IVA (R2+R3) | Sí, falló primero | 1 failed, 6 passed | 7 passed | No |
| 8 | cantidad cero es inválida (R5) | Sí, falló primero | 1 failed, 7 passed | 8 passed | No |
| 9 | domicilio gratis en 50.000 exacto (R4) | No (ya cubierta) | — | 9 passed | No |
| 10 | justo bajo el umbral de domicilio (R4) | No (ya cubierta) | — | 10 passed | No |
| 11 | justo bajo el umbral de descuento (R3) | No (ya cubierta) | — | 11 passed | No |
| 12 | descuento en el umbral con producto gravado (R2+R3) | No (ya cubierta) | — | 12 passed | No |
| 13 | redondeo al peso más cercano (R6) | No (ya cubierta) | — | 13 passed | No |
| 14 | redondeo comercial desde medio peso (R6) | Sí, falló primero | 1 failed, 13 passed | 14 passed | No |
| 15 | varios gravados con cantidad (R1+R2+R4) | No (ya cubierta) | — | 15 passed | No |
| 16 | cantidad negativa es inválida (R5) | No (ya cubierta) | — | 16 passed | No |
| 17 | ítem inválido entre válidos rechaza todo (R5) | No (ya cubierta) | — | 17 passed | No |
| 18 | el error nombra el producto inválido (R5) | Sí, falló primero | 1 failed, 17 passed | 18 passed | Sí: Funciones pequeñas con nombre de regla: _validar_cantidades, _tasa_descuento, _domicilio; tipos y docstring. |
| 19 | desglose del pedido mixto | Sí, falló primero | 1 error | 19 passed | No |
| 20 | desglose del carrito vacío | No (ya cubierta) | — | 20 passed | No |
| 21 | precio público de un exento (R2) | Sí, falló primero | 1 error | 21 passed | No |
| 22 | precio público de un gravado (R2+R6) | Sí, falló primero | 1 failed, 21 passed | 22 passed | No |
| 23 | precio público desde medio peso (R6) | No (ya cubierta) | — | 23 passed | No |

## Verificación final

- Suite de aceptación oculta: `8 passed in 0.01s`
- Prueba de mutación:

```
Mutante Resultado   Pruebas que lo detectan
M1      DETECTADO   test_descuento_en_el_umbral, test_descuento_en_el_umbral_con_producto_gravado
        Descuento solo si el subtotal es estrictamente mayor que 100.000
M2      DETECTADO   test_domicilio_gratis_en_el_umbral_exacto
        Domicilio también cuando el subtotal es exactamente 50.000
M3      DETECTADO   test_cantidad_cero_es_invalida, test_item_invalido_entre_validos_rechaza_todo, test_error_nombra_el_producto_invalido
        La cantidad 0 deja de considerarse inválida

Mutantes detectados: 3 de 3
```

## Historial de commits (más antiguo primero)

```
b956635 Preparación del kata: pedido.py y test_pedido.py vacíos
c63690f ROJO prueba 1: carrito vacío cuesta 0 (R1)
92a86a9 VERDE prueba 1: carrito vacío cuesta 0 (R1)
300c774 ROJO prueba 2: un producto exento (R1, R2)
90088bf VERDE prueba 2: un producto exento (R1, R2)
44bb696 ROJO prueba 3: la cantidad multiplica el precio (R1)
c191aca VERDE prueba 3: la cantidad multiplica el precio (R1)
39efc32 ROJO prueba 4: producto gravado paga IVA 19 % (R2)
c122e6f VERDE prueba 4: producto gravado paga IVA 19 % (R2)
fb8c771 REFACTOR tras prueba 4: Extraer la constante TASA_IVA y la variable iva
242b697 ROJO prueba 5: cobro de domicilio bajo 50.000 (R4)
ad29cec VERDE prueba 5: cobro de domicilio bajo 50.000 (R4)
0ad2ac0 REFACTOR tras prueba 5: Constantes UMBRAL_DOMICILIO y COSTO_DOMICILIO
4f61270 ROJO prueba 6: descuento del 10 % en el umbral de 100.000 (R3)
7b7a9c0 VERDE prueba 6: descuento del 10 % en el umbral de 100.000 (R3)
6fa3602 REFACTOR tras prueba 6: Constantes UMBRAL_DESCUENTO y TASA_DESCUENTO
25a44df ROJO prueba 7: pedido mixto: descuento antes del IVA (R2+R3)
f74e199 VERDE prueba 7: pedido mixto: descuento antes del IVA (R2+R3)
2cdf639 ROJO prueba 8: cantidad cero es inválida (R5)
689986b VERDE prueba 8: cantidad cero es inválida (R5)
aece8ad PRUEBA 9 (caso límite, pasa sin código nuevo): domicilio gratis en 50.000 exacto (R4)
7793fb8 PRUEBA 10 (caso límite, pasa sin código nuevo): justo bajo el umbral de domicilio (R4)
8f2c067 PRUEBA 11 (caso límite, pasa sin código nuevo): justo bajo el umbral de descuento (R3)
ff07c02 PRUEBA 12 (caso límite, pasa sin código nuevo): descuento en el umbral con producto gravado (R2+R3)
3423d27 PRUEBA 13 (caso límite, pasa sin código nuevo): redondeo al peso más cercano (R6)
5d43a2d ROJO prueba 14: redondeo comercial desde medio peso (R6)
8924373 VERDE prueba 14: redondeo comercial desde medio peso (R6)
54a756b PRUEBA 15 (caso límite, pasa sin código nuevo): varios gravados con cantidad (R1+R2+R4)
eebac6c PRUEBA 16 (caso límite, pasa sin código nuevo): cantidad negativa es inválida (R5)
c582634 PRUEBA 17 (caso límite, pasa sin código nuevo): ítem inválido entre válidos rechaza todo (R5)
17e36c5 ROJO prueba 18: el error nombra el producto inválido (R5)
79ea535 VERDE prueba 18: el error nombra el producto inválido (R5)
6364fab REFACTOR tras prueba 18: Funciones pequeñas con nombre de regla
7ac53fa ROJO prueba 19: desglose del pedido mixto
9d9f17f VERDE prueba 19: desglose del pedido mixto
1a666d8 PRUEBA 20 (caso límite, pasa sin código nuevo): desglose del carrito vacío
a888a1b Paso 4.1: suite de aceptación oculta
036afd3 Paso 4.2: prueba de mutación M1-M3
2242a44 Bitácora de evidencia TDD generada desde el historial
ba0e473 ROJO prueba 21: precio público de un producto exento (R2)
7a4b9f8 VERDE prueba 21: precio público de un producto exento (R2)
34cbd84 ROJO prueba 22: precio público de un gravado incluye IVA (R2+R6)
8ffa4e1 VERDE prueba 22: precio público de un gravado incluye IVA (R2+R6)
5d7f56c PRUEBA 23 (caso límite, pasa sin código nuevo): precio público desde medio peso (R6)
```

Para revisar un paso: `git show <hash>`; para ver el estado del código en un paso: `git checkout <hash>`.
