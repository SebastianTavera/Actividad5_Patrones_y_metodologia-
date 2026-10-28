# Caso de estudio XP · MercaBarrio — Entregables del grupo

> Patrones y Metodologías para la Construcción de Software · Sesión 11
> Pregunta central: *¿Escribir la prueba antes que el código, y hacerlo entre dos, produce un módulo con menos defectos que el original?*

| Entregable de la guía | Dónde está |
|---|---|
| 1. `pedido.py` y `test_pedido.py` con todas las pruebas en verde | [`pedido.py`](../pedido.py), [`test_pedido.py`](../test_pedido.py) |
| 2. Bitácora de la pareja | [Paso 2](#paso-2--acuerdos-y-bitácora-de-la-pareja) |
| 3. Registro de la suite oculta y de los 3 mutantes | [Paso 4](#paso-4--medición-de-la-calidad) · [`scripts/mutantes.py`](../scripts/mutantes.py) |
| 4. Respuestas a las 5 preguntas de reflexión | [4.4](#44-preguntas-de-reflexión) |

Cómo reproducir la evidencia:

```bash
python -m pytest -q test_pedido.py           # kata: 23 pruebas propias
python -m pytest -q test_suite_oculta.py     # suite de aceptación: 8 pruebas
python scripts/mutantes.py                   # mutantes M1, M2, M3
python -m pytest -q                          # todo el proyecto (kata + tienda)
```

---

## Paso 1 · Reglas de negocio y lista de pruebas

| ID | Regla |
|---|---|
| R1 | El subtotal es la suma de precio × cantidad. Un carrito vacío cuesta 0 |
| R2 | Los productos gravados pagan IVA del 19 %; los de canasta básica están exentos |
| R3 | Si el subtotal es de 100.000 o más, se descuenta el 10 % **antes** de calcular el IVA |
| R4 | Si el subtotal es menor a 50.000 se cobra domicilio de 4.000; desde 50.000 es gratis |
| R5 | Una cantidad ≤ 0 es inválida y se rechaza con un error |
| R6 | El total se redondea al peso más cercano |

Lista ordenada (de lo más trivial a lo más complejo). `*` = caso límite (valor justo en el umbral).

| # | Caso | Entrada | Esperado | Regla |
|---|---|---|---|---|
| 1 | Carrito vacío | ninguno | 0 | R1 |
| 2 | Un producto exento | arroz 60.000 × 1 | 60.000 | R1, R2 |
| 3 | La cantidad multiplica | arroz 30.000 × 2 | 60.000 | R1 |
| 4 | Producto gravado | gaseosa 60.000 × 1 | 71.400 | R2 |
| 5 | Cobro de domicilio | arroz 20.000 × 1 | 24.000 | R4 |
| 6 | Descuento en el umbral `*` | arroz 100.000 × 1 | 90.000 | R3 |
| 7 | Pedido mixto | gaseosa 80.000 + arroz 40.000 | 121.680 | R2 + R3 |
| 8 | Cantidad cero `*` | arroz 10.000 × 0 | `ValueError` | R5 |
| 9 | **Domicilio gratis en el umbral exacto** `*` | arroz 50.000 × 1 | 50.000 | R4 |
| 10 | Justo bajo el umbral de domicilio `*` | arroz 49.999 × 1 | 53.999 | R4 |
| 11 | Justo bajo el umbral de descuento `*` | arroz 99.999 × 1 | 99.999 | R3 |
| 12 | Descuento en el umbral con gravado `*` | licuadora 100.000 × 1 | 107.100 | R2 + R3 |
| 13 | Redondeo al peso | jabón 10.001 × 1 | 15.901 | R6 |
| 14 | **Redondeo desde medio peso** `*` | aceite 50.150 × 1 (total exacto 59.678,5) | 59.679 | R6 |
| 15 | Varios gravados con cantidad | gaseosa 5.000 × 3 + galletas 2.000 × 4 | 31.370 | R1 + R2 + R4 |
| 16 | Cantidad negativa | arroz 10.000 × −2 | `ValueError` | R5 |
| 17 | Ítem inválido entre válidos | arroz ×1 + pan ×0 | `ValueError` | R5 |
| 18 | El error nombra el producto | pan × 0 | `ValueError` que menciona "pan" | R5 |
| 19 | Desglose del pedido mixto | caso 7 | subtotal 120.000, descuento 12.000, IVA 13.680, domicilio 0 | todas |
| 20 | Desglose del carrito vacío | ninguno | todo en 0 | R1 |
| 21 | Precio público de un exento | arroz 4.900 | 4.900 | R2 |
| 22 | Precio público de un gravado | gaseosa 6.900 | 8.211 | R2 + R6 |
| 23 | Precio público desde medio peso `*` | 50.150 gravado (59.678,5) | 59.679 | R6 |

**Comparación con la lista de referencia.** A la referencia (casos 1–8) le faltaban los casos 9–18. El más
importante es la **respuesta a la pregunta de discusión**: el caso límite de R4 que no aparece en la referencia
es *subtotal exactamente 50.000* (caso 9). Sin él, el mutante M2 sobrevive (ver Paso 4).
Los casos 19–20 se agregaron porque la tienda necesita mostrar el desglose, no solo el total.

---

## Paso 2 · Acuerdos y bitácora de la pareja

**Acuerdos firmados antes de empezar**

- [x] Cambiamos el teclado en cada prueba, sin excepción.
- [x] Ejecutamos todas las pruebas después de cada cambio (`python -m pytest -q`).
- [x] Ninguno escribe código de producción sin una prueba en rojo.
- [x] Cualquiera puede pedir una pausa de 2 minutos.

Firmas: ______________________ (A) · ______________________ (B)

**Protocolo ping-pong.** A escribe la prueba y la ve fallar → B escribe el código mínimo → refactorizan con
todo en verde → B escribe la siguiente prueba → pasa el teclado a A.

**Bitácora** (completar nombres y minutos reales de la sesión; la alternancia sigue el protocolo):

| Prueba | Escribió la prueba | La hizo pasar | ¿Hubo refactorización? | Minutos |
|---|---|---|---|---|
| 1 Carrito vacío | A | B | No (se creó `Item`) | |
| 2 Producto exento | B | A | No | |
| 3 Cantidad multiplica | A | B | No | |
| 4 Producto gravado | B | A | Sí: `base_gravada` y constante `TASA_IVA` | |
| 5 Domicilio | A | B | Sí: `UMBRAL_DOMICILIO`, `COSTO_DOMICILIO`; guarda para carrito vacío | |
| 6 Descuento en el umbral | B | A | Sí: `UMBRAL_DESCUENTO`, `TASA_DESCUENTO`, `>=` | |
| 7 Pedido mixto | A | B | Sí: IVA calculado sobre `base_gravada * (1 - tasa)` | |
| 8 Cantidad inválida | B | A | Sí: se extrajo `_validar_cantidades` | |
| 9–18 casos límite propios | alternando | alternando | Sí: `Decimal` + `ROUND_HALF_UP` (caso 14) | |
| 19–20 desglose | A | B | Sí: `desglose_pedido` y `total_pedido` delega en él | |

**Rotación a los 30 minutos.** Quien llega se pone al día solo leyendo `test_pedido.py`: cada prueba tiene el
nombre de la regla que protege y un comentario con el número de caso y la regla (`# 6 · R3 (*)`).

**Lista de chequeo de refactorización** (verificada en `pedido.py`)

- [x] Sin números mágicos: `TASA_IVA`, `UMBRAL_DESCUENTO`, `TASA_DESCUENTO`, `UMBRAL_DOMICILIO`, `COSTO_DOMICILIO`.
- [x] Nombres que explican la regla: `base_gravada`, `descuento`, `domicilio`, `_tasa_descuento`, `_domicilio`.
- [x] Todas las pruebas siguen en verde después de cada cambio.

---

## Paso 3 · Kata TDD

Resultado final en [`pedido.py`](../pedido.py). Decisiones de diseño:

- **Diseño simple**: una función pública por responsabilidad (`desglose_pedido`, `total_pedido`) y funciones
  privadas pequeñas con nombre de regla (`_validar_cantidades`, `_tasa_descuento`, `_domicilio`, `_al_peso`).
- **Aritmética exacta con `Decimal`**: con `float`, `50.150 × 0,19` no es exactamente 9.528,5 y `round()` de
  Python redondea al par (redondeo bancario). La regla R6 pide "al peso más cercano", que en comercio es
  redondeo hacia arriba desde ,5. La prueba 14 lo fija.
- **R5 valida todos los ítems antes de calcular**: un ítem inválido entre válidos rechaza el pedido completo.

---

## Paso 4 · Medición de la calidad

### 4.1 Suite de aceptación oculta

`python -m pytest -q test_suite_oculta.py` → **8 de 8 pasan · 0 fallas**.

| Prueba oculta | ¿Cubierta por nuestra lista? |
|---|---|
| `test_limite_domicilio_exacto` | Sí, caso 9 |
| `test_justo_bajo_limite_domicilio` | Sí, caso 10 |
| `test_limite_descuento_exacto_gravado` | Sí, caso 12 |
| `test_justo_bajo_limite_descuento` | Sí, caso 11 |
| `test_redondeo_al_peso` | Sí, caso 13 |
| `test_varios_items_gravados_cantidad` | Sí, caso 15 |
| `test_cantidad_negativa` | Sí, caso 16 |
| `test_item_invalido_entre_validos` | Sí, caso 17 |

### 4.2 Prueba de mutación

Automatizada en `scripts/mutantes.py` (aplica el mutante a una copia, ejecuta **solo** `test_pedido.py` y
deshace el cambio). Resultado real:

| Mutante | Cambio en el código | ¿Lo detectan nuestras pruebas? | Pruebas que lo matan |
|---|---|---|---|
| M1 | `subtotal >= UMBRAL_DESCUENTO` → `>` | **Detectado** | casos 6 y 12 |
| M2 | `subtotal < UMBRAL_DOMICILIO` → `<=` | **Detectado** | caso 9 |
| M3 | `item.cantidad <= 0` → `< 0` | **Detectado** | casos 8, 17 y 18 |

Comparación: con solo las 8 pruebas de la lista de referencia, **M2 sobrevive** (así lo indica también la
tabla de resultados esperados de la guía).

### 4.3 Registro de resultados de la pareja

| Pareja | Pruebas propias | Fallas en la suite oculta (de 8) | Mutantes detectados (de 3) | Minutos del kata |
|---|---|---|---|---|
| A + B | 23 | 0 | 3 | ___ |

Hallazgo adicional: la solución de referencia de la guía (con `float` y `round()`) **falla** nuestra prueba 14
(devuelve 59.678 en vez de 59.679). La suite oculta no lo detecta porque ninguno de sus casos cae exactamente
en ,5.

### 4.4 Preguntas de reflexión

> Las respuestas 1, 2 y 5 se apoyan en los datos medidos arriba. Las respuestas 3 y 4 dependen de lo que vivió
> cada pareja en clase: el texto es una propuesta basada en el caso y deben ajustarlo a su experiencia real.

**1. ¿Qué mutante sobrevivió a sus pruebas? ¿Qué prueba de una línea lo habría detectado?**
Ninguno sobrevivió (3 de 3). Con la lista de referencia sobrevive M2; lo mata una sola línea:
`assert total_pedido([Item("arroz", 50_000, 1, gravado=False)]) == 50_000`. Lo agregamos porque al marcar
casos límite con `*` en el Paso 1 nos preguntamos "¿qué pasa *justo* en cada umbral?" para las dos reglas con
umbral (R3 y R4), y la referencia solo lo hacía para R3.

**2. Los dos defectos de producción de MercaBarrio, ¿los habría evitado alguna prueba de su lista? ¿Cuál?**
Sí, ambos.
- *Cobraba IVA sobre la canasta básica* → casos 2 y 7: arroz exento debe costar 60.000, y en el pedido mixto
  el IVA (13.680) se calcula solo sobre la gaseosa. Con IVA sobre todo, el caso 2 daría 71.400.
- *Domicilio gratis un peso antes de lo debido* → casos 10 y 9: con 49.999 se debe cobrar domicilio (53.999)
  y con 50.000 no. El defecto equivale a comparar contra 49.999, y el caso 10 falla de inmediato.

**3. Un error que el navegante detectó antes de que el conductor ejecutara las pruebas.**
En el caso 7 el conductor iba a calcular el IVA sobre `base_gravada` completa y restar el descuento al final.
El navegante, que tenía R3 a la vista, señaló "el descuento va **antes** del IVA": habría dado 123.200 en lugar
de 121.680 (es la pista de la guía). Se corrigió a `base_gravada * (1 - tasa) * TASA_IVA` antes de ejecutar.

**4. Quien llegó en la rotación, ¿pudo entender el código leyendo solo las pruebas? ¿Qué dice eso de las pruebas como documentación?**
Sí: los nombres (`test_domicilio_gratis_en_el_umbral_exacto`, `test_pedido_mixto_descuento_antes_del_iva`) y
los comentarios `# n · Regla` funcionan como una especificación ejecutable; se lee la regla, el ejemplo y el
resultado esperado. A diferencia de un documento, no puede quedar desactualizada: si el código cambia, la
prueba falla. Por eso el nombre de cada prueba describe el comportamiento, no la implementación.

**5. TDD y el trabajo en parejas cuestan tiempo. ¿En qué tipo de módulo vale la pena pagar ese costo y en cuál no?**
Vale la pena en lógica de negocio con reglas, umbrales y dinero (como `total_pedido`): un error cuesta
reclamos y plata, los casos límite son fáciles de equivocar y el módulo cambia con el negocio. En este proyecto,
además, las mismas pruebas protegen la tienda completa: el carrito, el checkout y los reportes usan
`desglose_pedido`. Vale menos en código desechable (prototipos, scripts de una vez) o en detalles visuales
de interfaz que cambian a diario y se validan mejor mirándolos; ahí basta con pruebas de integración ligeras
(como `tests/test_api.py`) y revisión.
