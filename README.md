# MercaBarrio · Tienda de barrio con Extreme Programming

Actividad 5 · Patrones y Metodologías para la Construcción de Software.
Caso de estudio XP (Sesión 11): reconstruir con **TDD** y **programación en parejas** el cálculo del total de
un pedido que falló en producción, y construir alrededor de él una **tienda en línea completa**.

- **Backend:** Python 3.10+ · Flask · SQLite (librería estándar)
- **Frontend:** HTML, CSS y JavaScript sin frameworks (módulos ES)
- **Pruebas:** pytest · 62 pruebas (kata, suite de aceptación, servicios y API) + prueba de mutación

Evidencia del ciclo TDD, un commit por cada paso rojo → verde → refactor: **[docs/EVIDENCIA_TDD.md](docs/EVIDENCIA_TDD.md)**

Entregables del caso (lista de pruebas, bitácora, suite oculta, mutantes y reflexión):
**[docs/ACTIVIDAD_XP.md](docs/ACTIVIDAD_XP.md)**

## Cómo ejecutar

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py                     # http://127.0.0.1:5000
python -m pytest -q               # todas las pruebas
python scripts/mutantes.py        # prueba de mutación M1-M3 sobre pedido.py
```

Clave del panel de administración: `admin123` (cámbiala con la variable `MERCABARRIO_ADMIN`).
La base de datos se crea sola en `mercabarrio.db` con 25 productos de ejemplo (`MERCABARRIO_DB` cambia la ruta).

## Funcionalidades

| Cliente | Tendero (Admin) |
|---|---|
| Catálogo con búsqueda, categorías, filtro canasta básica / con IVA y orden por precio o nombre | Indicadores: ingresos, pedidos, ticket promedio, pedidos por despachar |
| Detalle de producto (presentación, stock, impuesto, precio con IVA) | Gestión de pedidos: preparar → enviar → entregado, o cancelar (devuelve stock) |
| Carrito persistente con cantidades y aviso de stock | Inventario: crear, editar y retirar productos |
| Desglose en vivo: subtotal, descuento, IVA, domicilio y total | Reporte: más vendidos, pedidos por estado, IVA recaudado, stock bajo |
| Barras de progreso "te faltan $X para domicilio gratis / 10 % de descuento" | Acceso con clave |
| Checkout con datos de entrega validados y confirmación | |
| Mis pedidos: seguimiento por teléfono con línea de tiempo y cancelación | |

Los precios y totales **siempre** los calcula el backend con `pedido.py`; el navegador nunca duplica reglas de negocio.

## Reglas de negocio (`pedido.py`)

| ID | Regla |
|---|---|
| R1 | Subtotal = Σ precio × cantidad; carrito vacío = 0 |
| R2 | IVA 19 % a productos gravados; canasta básica exenta |
| R3 | Desde 100.000 de subtotal, 10 % de descuento **antes** del IVA |
| R4 | Domicilio de 4.000 si el subtotal es menor a 50.000; gratis desde 50.000 |
| R5 | Cantidad ≤ 0 → `ValueError` |
| R6 | Total redondeado al peso más cercano (redondeo comercial con `Decimal`) |

## Arquitectura

```
pedido.py                 ← núcleo del kata (TDD): Item, Desglose, desglose_pedido, total_pedido
test_pedido.py            ← 20 pruebas del kata (8 de referencia + 12 casos límite propios)
test_suite_oculta.py      ← suite de aceptación del docente
app.py                    ← arranque de Flask
tienda/
  dominio/                ← entidades, errores y puertos (interfaces). No conoce Flask ni SQLite
  servicios/              ← casos de uso: catálogo, cotizador, pedidos, inventario, reportes
  infraestructura/        ← adaptadores SQLite y datos semilla
  api/rutas.py            ← capa HTTP: JSON ↔ servicios, errores → códigos HTTP
  contenedor.py           ← raíz de composición (único lugar que conoce las clases concretas)
static/                   ← index.html, css/styles.css, js/*.js
tests/                    ← pruebas de servicios (con dobles en memoria) y de la API
scripts/mutantes.py       ← prueba de mutación automatizada
```

### Principios SOLID

| Principio | Dónde se aplica |
|---|---|
| **S** – Responsabilidad única | `pedido.py` solo calcula; `CotizadorServicio` arma líneas; `PedidosServicio` maneja el checkout; `rutas.py` solo traduce HTTP. En el frontend: `api.js` (HTTP), `carrito.js` (estado), `anim.js` (movimiento), una vista por archivo |
| **O** – Abierto/cerrado | `CotizadorServicio` recibe la calculadora como parámetro (`CalculadoraTotal`): se puede cambiar la política de precios sin modificar el servicio (ver `test_cotizador_acepta_otra_calculadora`). Los errores de dominio se mapean a HTTP con una tabla, no con `if` |
| **L** – Sustitución de Liskov | `SqliteProductos` y `ProductosEnMemoria` (pruebas) cumplen el mismo contrato y son intercambiables |
| **I** – Segregación de interfaces | `CatalogoLectura`, `InventarioEscritura` y `RepositorioPedidos` son contratos separados: `CatalogoServicio` solo puede leer, `ReportesServicio` no puede escribir |
| **D** – Inversión de dependencias | Los servicios dependen de `dominio/puertos.py`; `contenedor.py` inyecta las implementaciones SQLite. Por eso `tests/test_servicios.py` corre sin base de datos |

### Prácticas XP

| Práctica | Evidencia en el repositorio |
|---|---|
| TDD (rojo → verde → refactorizar) | `test_pedido.py` ordenado de lo simple a lo complejo; cada regla tiene su prueba |
| Programación en parejas | Protocolo ping-pong y bitácora en `docs/ACTIVIDAD_XP.md` |
| Refactorización | Constantes con nombre, funciones pequeñas con nombre de regla, `Decimal` |
| Diseño simple | Sin frameworks en el frontend; SQLite de la librería estándar; una sola fuente de verdad para precios |
| Integración continua | `python -m pytest -q` ejecuta las 62 pruebas en menos de un segundo |
| Propiedad colectiva y estándares | Estilo y nombres en español consistentes en todas las capas |

## Interfaz

Estilo minimalista de **mar profundo**: azules y cianes oscuros, **vidrio líquido opaco** (gradiente translúcido,
desenfoque de fondo, brillo interior y un reflejo que sigue al puntero) y fondo con corrientes y burbujas lentas.

Todas las animaciones comparten las mismas curvas (`--salida`, `--suave`, `--resorte`) para que cada transición
conecte con la siguiente: las pestañas y categorías tienen una píldora que se desliza, las tarjetas entran en
cascada, el detalle de producto crece desde la tarjeta pulsada (técnica FLIP), un punto de luz vuela en arco al
carrito, los totales cuentan hasta su nuevo valor, los pasos del checkout se deslizan lateralmente y la
confirmación dibuja su check. Respeta `prefers-reduced-motion` y funciona en móvil.
