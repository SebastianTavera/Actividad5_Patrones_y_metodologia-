# MercaBarrio · Tienda de barrio con Extreme Programming

Actividad 5 · Patrones y Metodologías para la Construcción de Software · Caso de estudio XP (Sesión 11).

MercaBarrio es una startup bogotana de pedidos para tiendas de barrio que publicó un cálculo de totales con
errores: cobraba IVA sobre la canasta básica y daba domicilio gratis un peso antes de lo debido. En este proyecto
se reconstruye ese cálculo con **TDD** y **programación en parejas** (`pedido.py`), se mide su calidad con una
suite de aceptación y prueba de mutación, y alrededor de él se construye una **tienda en línea completa**.

| | |
|---|---|
| **Backend** | Python 3.10+ · Flask · SQLite (librería estándar) |
| **Frontend** | HTML, CSS y JavaScript sin frameworks (módulos ES) |
| **Pruebas** | pytest · 73 pruebas + prueba de mutación (3 de 3 mutantes detectados) |
| **Entregables del caso** | [docs/ACTIVIDAD_XP.md](docs/ACTIVIDAD_XP.md) |
| **Evidencia TDD** | [docs/EVIDENCIA_TDD.md](docs/EVIDENCIA_TDD.md): un commit por cada paso rojo → verde → refactor |

---

## 1. Cómo ejecutar el proyecto completo

### Requisitos
- **Python 3.10 o superior** (`python --version`).
- **Git**, solo si vas a clonar el repositorio.
- Un navegador moderno (Chrome, Edge, Firefox o Safari).

### Paso 1 · Obtener el código

```bash
git clone -b claude/mercabarrio-tienda-xp https://github.com/SebastianTavera/Actividad5_Patrones_y_metodologia-.git
cd Actividad5_Patrones_y_metodologia-
```

Si lo descargaste como ZIP, entra a la carpeta donde están `app.py` y `requirements.txt`. Al descomprimir
suele quedar una carpeta dentro de otra con el mismo nombre: hay que entrar a la de adentro.

### Paso 2 · Crear un entorno virtual (recomendado) e instalar dependencias

**Windows (PowerShell o CMD)**
```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Solo se instalan dos paquetes: `flask` y `pytest`.

### Paso 3 · Ejecutar las pruebas

```bash
python -m pytest -q                       # las 73 pruebas → "73 passed"
python -m pytest -q test_pedido.py        # solo el kata TDD → 23 pruebas
python -m pytest -q test_suite_oculta.py  # solo la suite de aceptación → 8 pruebas
python scripts/mutantes.py                # prueba de mutación → "Mutantes detectados: 3 de 3"
```

### Paso 4 · Abrir la tienda

```bash
python app.py
```

Abre **http://127.0.0.1:5000** en el navegador. La terminal queda ocupada mientras el servidor corre;
para detenerlo usa `Ctrl + C`.

- La primera vez se crea `mercabarrio.db` con 25 productos de ejemplo.
- Panel de administración: pestaña **Admin**, clave **`admin123`**.

> **Importante:** abre la tienda siempre por `http://127.0.0.1:5000`. Si abres `static/index.html` con la
> extensión Live Server (puerto 5500) o con doble clic, la página sale sin estilos y sin productos, porque el
> backend de Python no está detrás.

### Configuración opcional (variables de entorno)

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `MERCABARRIO_ADMIN` | Clave del panel de administración | `admin123` |
| `MERCABARRIO_DB` | Ruta del archivo de base de datos | `mercabarrio.db` junto a `app.py` |
| `PORT` | Puerto del servidor | `5000` |

Ejemplo en PowerShell: `$env:MERCABARRIO_ADMIN = "otra-clave"; python app.py`.
Ejemplo en macOS/Linux: `MERCABARRIO_ADMIN=otra-clave python app.py`.

Para empezar con la base de datos limpia, detén el servidor y borra `mercabarrio.db`.

### Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `No module named 'flask'` | No se instalaron las dependencias: ejecuta el paso 2 dentro de la carpeta del proyecto |
| `Could not open requirements file` o `can't open file 'app.py'` | La terminal no está en la carpeta del proyecto: usa `cd` hasta la carpeta que contiene `app.py` |
| `pytest` encuentra cientos de errores de otras carpetas | Lo ejecutaste fuera del proyecto (por ejemplo en `C:\Users\tu-usuario`) |
| La página sale en blanco o con una figura negra gigante | La abriste por Live Server o como archivo: usa `http://127.0.0.1:5000` |
| Cambié el código y no veo cambios | Reinicia `python app.py` y recarga con `Ctrl + F5` |

---

## 2. Qué hace la aplicación

### Como cliente

| Función | Detalle |
|---|---|
| **Catálogo** | 25 productos en filas compactas o en cuadrícula (botón junto al orden; la preferencia se recuerda) |
| **Información de cada producto** | Imagen, nombre, presentación, estrellas y número de reseñas, sello de descuento, precio con IVA incluido y precio anterior tachado, aviso "Quedan N" cuando hay poco stock |
| **Búsqueda y filtros** | Búsqueda por texto, categorías, canasta básica / con IVA, orden por destacados, mejor calificados, mayor descuento, precio o nombre |
| **Favoritos** | Botón ♥ en cada producto y chip **♥ Favoritos** para ver solo los guardados |
| **Detalle de producto** | Descripción, ficha técnica completa, stock, precio sin IVA, selector de cantidad |
| **Carrito** | Panel lateral con cantidades, aviso de stock y desglose en vivo (subtotal sin IVA, descuento, IVA, domicilio, total) |
| **Metas de compra** | Barras "te faltan $X para domicilio gratis" y "te faltan $X para 10 % de descuento" |
| **Barra del carrito (celular)** | Barra fija abajo con "N productos · Ver carrito · $total" |
| **Compra** | Datos de entrega validados (nombre, teléfono, dirección, notas) y confirmación con número de pedido |
| **Mis pedidos** | Seguimiento por teléfono, línea de tiempo (recibido → en preparación → en camino → entregado) y cancelación |

### Como tendero (Admin)

| Función | Detalle |
|---|---|
| **Indicadores** | Ingresos, número de pedidos, ticket promedio y pedidos por despachar |
| **Pedidos** | Filtro por estado y botones para avanzar (preparar → enviar → entregado) o cancelar; al cancelar se devuelve el stock |
| **Inventario** | Crear, editar y retirar productos: precio, precio anterior (oferta), stock, categoría, presentación, IVA y características |
| **Reporte** | Más vendidos, pedidos por estado, IVA recaudado y productos con stock bajo |

---

## 3. Reglas de negocio (`pedido.py`)

| ID | Regla |
|---|---|
| R1 | Subtotal = Σ precio × cantidad. Un carrito vacío cuesta 0 |
| R2 | IVA del 19 % a productos gravados; la canasta básica está exenta |
| R3 | Desde 100.000 de subtotal se descuenta el 10 % **antes** de calcular el IVA |
| R4 | Domicilio de 4.000 si el subtotal es menor a 50.000; gratis desde 50.000 |
| R5 | Una cantidad ≤ 0 se rechaza con `ValueError` |
| R6 | El total se redondea al peso más cercano (redondeo comercial: ,5 sube) |

Funciones públicas del módulo:

| Función | Qué devuelve |
|---|---|
| `total_pedido(items)` | El total a pagar (la función que pide la guía) |
| `desglose_pedido(items)` | Subtotal, descuento, IVA, domicilio y total; lo usa el carrito |
| `precio_publico(precio, gravado)` | El precio que ve el cliente en el catálogo, con IVA incluido si es gravado |

**Una sola fuente de verdad:** toda cifra de dinero que muestra la tienda sale de estas funciones. El navegador
nunca calcula IVA, descuentos ni domicilio. Usamos `Decimal` porque `round()` de Python con `float` redondea al
par: la solución de referencia de la guía da 59.678 donde corresponde 59.679.

---

## 4. Estructura del proyecto y qué hace cada parte

```
├── pedido.py                     Reglas de negocio del kata (TDD)
├── test_pedido.py                23 pruebas del kata
├── test_suite_oculta.py          8 pruebas de aceptación del docente
├── app.py                        Arranca Flask, sirve la página y la API
├── requirements.txt              flask, pytest
├── pytest.ini                    Le dice a pytest dónde están las pruebas
├── scripts/
│   └── mutantes.py               Prueba de mutación automatizada (M1, M2, M3)
├── docs/
│   └── ACTIVIDAD_XP.md           Entregables del caso de estudio
├── tienda/                       Backend de la tienda, en capas
│   ├── dominio/
│   │   ├── modelos.py            Producto, Cliente, Pedido, LineaPedido, estados del pedido
│   │   ├── errores.py            Errores de negocio (datos inválidos, no encontrado, sin stock…)
│   │   └── puertos.py            Interfaces de las que dependen los servicios
│   ├── servicios/
│   │   ├── catalogo.py           Búsqueda, filtros y orden del catálogo
│   │   ├── cotizador.py          Arma las líneas del carrito y llama a pedido.py
│   │   ├── pedidos.py            Compra, historial, cambio de estado y cancelación
│   │   ├── inventario.py         Alta, edición y retiro de productos
│   │   └── reportes.py           Indicadores y reporte del panel
│   ├── infraestructura/
│   │   ├── sqlite.py             Base de datos, transacciones y migración de columnas
│   │   └── semilla.py            25 productos de ejemplo
│   ├── api/
│   │   └── rutas.py              Endpoints HTTP (JSON) y traducción de errores a códigos
│   └── contenedor.py             Conecta las piezas concretas (raíz de composición)
├── tests/
│   ├── test_servicios.py         27 pruebas de servicios con repositorios en memoria
│   └── test_api.py               15 pruebas de la API con SQLite real
└── static/                       Frontend
    ├── index.html                Página única con las tres vistas, el carrito y el modal
    ├── css/styles.css            Estilos, paleta, vidrio líquido y animaciones
    └── js/
        ├── app.js                Punto de entrada y navegación entre vistas
        ├── api.js                Único módulo que habla con el backend
        ├── tienda.js             Catálogo, filtros, favoritos, vistas y detalle
        ├── cajon.js              Carrito, compra en 3 pasos y barra del celular
        ├── pedidos.js            Vista "Mis pedidos"
        ├── admin.js              Panel de administración
        ├── carrito.js            Estado del carrito (ids y cantidades, guardado en el navegador)
        ├── anim.js               Animaciones compartidas
        ├── ui.js                 Avisos, ventana modal y confirmaciones
        ├── formato.js            Formato de pesos y fechas, escape de HTML
        └── iconos.js             Ilustraciones por categoría e íconos
```

### Raíz del proyecto

- **`pedido.py`**: el módulo que pide la guía. Define `Item` y `Desglose`, las constantes con nombre
  (`TASA_IVA`, `UMBRAL_DESCUENTO`, `TASA_DESCUENTO`, `UMBRAL_DOMICILIO`, `COSTO_DOMICILIO`) y funciones pequeñas
  con nombre de regla (`_validar_cantidades`, `_tasa_descuento`, `_domicilio`, `_al_peso`). No depende de nada
  de la tienda.
- **`test_pedido.py`**: las pruebas en el orden en que se escribieron, de lo más simple a lo más complejo. Cada una
  lleva un comentario con su número de caso y la regla que protege (por ejemplo `# 9 · R4 (*)`, donde `*` marca
  un caso límite).
- **`test_suite_oculta.py`**: la suite de aceptación que entrega el docente en el Paso 4, copiada sin cambios.
- **`scripts/mutantes.py`**: para cada mutante copia `pedido.py` con el defecto a una carpeta temporal, ejecuta
  **solo** `test_pedido.py` e informa si lo detecta. No modifica el archivo original.
- **`app.py`**: crea la aplicación Flask con `crear_app()`, registra la API y sirve `static/index.html` en `/`.

### Backend (`tienda/`)

Está organizado en capas. Cada capa solo conoce a la de abajo:

```
navegador ──HTTP/JSON──▶ api/rutas.py ──▶ servicios/* ──▶ dominio/puertos.py ◀── infraestructura/sqlite.py
                                              │
                                              └──▶ pedido.py (reglas de dinero)
```

- **`dominio/`** contiene las entidades y reglas propias de la tienda, sin Flask ni SQLite:
  - `modelos.py`:
    - `Producto` valida sus datos y calcula `descuento_pct`.
    - `Cliente` valida nombre, teléfono y dirección.
    - `Pedido` sabe a qué estados puede pasar (`TRANSICIONES`): un pedido entregado o cancelado no cambia más.
  - `errores.py` define `DatosInvalidos`, `NoEncontrado`, `StockInsuficiente`, `TransicionInvalida` y `NoAutorizado`.
  - `puertos.py` define los contratos `CatalogoLectura`, `InventarioEscritura`, `RepositorioPedidos`,
    `UnidadDeTrabajo` y `CalculadoraTotal`.
- **`servicios/`** contiene un caso de uso por archivo:
  - `CatalogoServicio`: busca, filtra por impuesto y ordena.
  - `CotizadorServicio`: convierte el carrito en líneas con los precios del catálogo, marca lo que no tiene stock
    y calcula el desglose con `pedido.desglose_pedido`.
  - `PedidosServicio`: en una sola transacción valida el cliente, cotiza, descuenta stock y guarda el pedido. También
    cambia estados y devuelve el stock al cancelar.
  - `InventarioServicio`: crea, edita parcialmente y retira productos (el retiro es lógico: el producto deja de
    mostrarse, pero los pedidos viejos lo conservan).
  - `ReportesServicio`: calcula ingresos, ticket promedio, más vendidos y stock bajo, sin contar los pedidos cancelados.
- **`infraestructura/`** guarda los datos:
  - `sqlite.py` implementa los puertos con SQLite. `BaseDeDatos` usa una conexión por hilo y transacciones anidables.
    Si encuentra una base de una versión anterior, le agrega las columnas nuevas sola.
  - `semilla.py` carga el catálogo inicial. Si la base ya existía, completa las calificaciones, ofertas y fichas
    de los productos de ejemplo.
- **`api/rutas.py`** traduce JSON a llamadas de servicios. No contiene reglas de negocio. Los errores de dominio se
  convierten en códigos HTTP (400, 401, 404, 409) y las rutas de administración exigen la cabecera `X-Admin-Clave`.
- **`contenedor.py`** es el único lugar que crea las clases concretas y las conecta.

### Endpoints de la API

| Método | Ruta | Para qué |
|---|---|---|
| GET | `/api/reglas` | Umbrales y tasas (los muestra la portada) |
| GET | `/api/categorias` | Categorías con productos activos |
| GET | `/api/productos?q=&categoria=&orden=&impuesto=` | Catálogo filtrado y ordenado |
| GET | `/api/productos/<id>` | Un producto |
| POST | `/api/carrito/cotizar` | Desglose del carrito `{"items": [{"producto_id", "cantidad"}]}` |
| POST | `/api/pedidos` | Crear pedido `{"cliente": {...}, "items": [...], "notas": ""}` |
| GET | `/api/pedidos?telefono=` | Pedidos de un cliente |
| POST | `/api/pedidos/<id>/cancelar` | El cliente cancela su pedido `{"telefono"}` |
| GET | `/api/admin/sesion` | Comprueba la clave |
| GET | `/api/admin/resumen` | Indicadores y reporte |
| GET | `/api/admin/pedidos?estado=` | Todos los pedidos |
| PATCH | `/api/admin/pedidos/<id>` | Cambiar estado `{"estado"}` |
| GET / POST | `/api/admin/productos` | Listar / crear productos |
| PUT / DELETE | `/api/admin/productos/<id>` | Editar / retirar un producto |

Códigos de respuesta: `400` datos inválidos, `401` clave incorrecta, `404` no existe, `409` sin stock o cambio de
estado no permitido.

### Frontend (`static/`)

- **`index.html`** contiene las tres vistas (Tienda, Mis pedidos, Admin), el panel del carrito, la ventana modal, los
  avisos y la barra del carrito del celular. El contenido lo dibuja JavaScript con los datos de la API.
- **`css/styles.css`** define:
  - la paleta de mar profundo en variables (`--abismo`, `--profundo`, `--cian`, …);
  - el estilo de vidrio líquido (`.vidrio`);
  - las curvas de animación compartidas (`--salida`, `--suave`, `--resorte`);
  - el diseño adaptable a celular y el modo de movimiento reducido.
- **`js/`** tiene un módulo por responsabilidad:
  - `app.js` navega entre vistas con la URL (`#/tienda`, `#/pedidos`, `#/admin`) e inicia cada módulo.
  - `api.js` agrupa todas las llamadas `fetch` y convierte los errores del servidor en mensajes.
  - `tienda.js` dibuja productos, maneja filtros, favoritos, la vista lista/cuadrícula y el detalle.
  - `cajon.js` maneja el carrito: líneas, desglose, metas, los 3 pasos de compra y la barra del celular.
  - `carrito.js` guarda solo ids y cantidades; los precios siempre vienen del servidor.
  - `pedidos.js` y `admin.js` manejan sus vistas.
  - `anim.js`, `ui.js`, `formato.js` e `iconos.js` son utilidades compartidas.

En el navegador (`localStorage`) se guardan solo preferencias de quien navega: carrito, favoritos, vista elegida y
último teléfono consultado. Los pedidos y el inventario viven en la base de datos.

---

## 5. Pruebas

| Archivo | Pruebas | Qué cubre |
|---|---|---|
| `test_pedido.py` | 23 | Reglas R1–R6, casos límite de cada umbral, redondeo, desglose y precio con IVA |
| `test_suite_oculta.py` | 8 | Suite de aceptación del docente |
| `tests/test_servicios.py` | 27 | Cotizador, compra, stock, estados, cancelación, catálogo, inventario y reportes con repositorios en memoria |
| `tests/test_api.py` | 15 | Endpoints con Flask y SQLite real: compra completa, errores HTTP, clave de admin, migración de bases viejas |

**Prueba de mutación** (`python scripts/mutantes.py`):

| Mutante | Defecto sembrado | Resultado | Prueba que lo detecta |
|---|---|---|---|
| M1 | Descuento solo si el subtotal es **mayor** que 100.000 | Detectado | Descuento en el umbral (casos 6 y 12) |
| M2 | Domicilio también con subtotal **exacto** de 50.000 | Detectado | Domicilio gratis en el umbral exacto (caso 9) |
| M3 | Cantidad 0 deja de ser inválida | Detectado | Cantidad cero (casos 8, 17 y 18) |

Con solo las 8 pruebas de referencia de la guía, M2 sobrevive. El caso 9 es el que faltaba.

---

## 6. Principios SOLID

| Principio | Dónde se aplica |
|---|---|
| **S** · Responsabilidad única | `pedido.py` solo calcula dinero; cada servicio es un caso de uso; `rutas.py` solo traduce HTTP. En el frontend, un módulo por responsabilidad (`api.js`, `carrito.js`, `anim.js`, una vista por archivo) |
| **O** · Abierto/cerrado | `CotizadorServicio` recibe la calculadora como parámetro (`CalculadoraTotal`): la política de precios cambia sin modificar el servicio (`test_cotizador_acepta_otra_calculadora`). Los errores se mapean a HTTP con una tabla, no con `if` |
| **L** · Sustitución de Liskov | `SqliteProductos` y `ProductosEnMemoria` (pruebas) cumplen el mismo contrato y son intercambiables |
| **I** · Segregación de interfaces | Lectura de catálogo, escritura de inventario y pedidos son contratos separados: `CatalogoServicio` solo puede leer y `ReportesServicio` no puede escribir |
| **D** · Inversión de dependencias | Los servicios dependen de `dominio/puertos.py`; `contenedor.py` inyecta SQLite. Por eso `tests/test_servicios.py` corre sin base de datos |

## 7. Prácticas de Extreme Programming

| Práctica | Evidencia |
|---|---|
| TDD (rojo → verde → refactorizar) | `test_pedido.py` ordenado de lo simple a lo complejo; `precio_publico` se agregó con sus pruebas en rojo primero (casos 21–23) |
| Programación en parejas | Protocolo ping-pong, acuerdos y bitácora en `docs/ACTIVIDAD_XP.md` |
| Refactorización | Constantes con nombre, funciones pequeñas con nombre de regla, `Decimal` para el redondeo |
| Diseño simple | Sin frameworks en el frontend; SQLite de la librería estándar; una sola fuente de verdad para el dinero |
| Integración continua | `python -m pytest -q` ejecuta las 73 pruebas en menos de un segundo |
| Propiedad colectiva y estándares | Nombres en español y el mismo estilo en todas las capas |

---

## 8. Diseño de la interfaz

- **Estilo:** minimalista de mar profundo, con azules y cianes oscuros y paneles de **vidrio líquido opaco**
  (gradiente translúcido, desenfoque, brillo interior y un reflejo que sigue al puntero).
- **Fondo:** limpio, con una luz difusa que sigue al mouse con inercia. En el celular, sin mouse, flota sola.
- **Productos:** filas compactas de unos 120 px, para ver muchos productos a la vez, con la opción de cambiar a
  cuadrícula. La ficha técnica completa está en el detalle de cada producto.
- **Animaciones:** todas comparten las mismas curvas, para que cada transición conecte con la siguiente:
  - las pestañas y categorías tienen una píldora que se desliza hasta la opción elegida;
  - cada producto aparece rápido y escalonado **solo la primera vez**, con las estrellas llenándose y el sello de
    descuento entrando;
  - el botón **Agregar** se transforma en el selector "− 1 +" y un punto de luz vuela en arco al carrito;
  - el detalle crece desde la imagen del producto (técnica FLIP);
  - los totales cuentan hasta su nuevo valor y los pasos de la compra se deslizan;
  - la confirmación dibuja su check y los botones muestran una onda donde se pulsan.
- **Accesibilidad:** navegación con teclado, textos para lectores de pantalla y respeto de `prefers-reduced-motion`.
- **Celular:** barra fija "Ver carrito · total" y categorías con un degradado que indica que se pueden deslizar.
