"""Catálogo inicial de una tienda de barrio bogotana."""
import json

from ..dominio.modelos import Producto
from .sqlite import BaseDeDatos, SqliteProductos

# (nombre, precio, precio anterior, categoría, gravado, stock, unidad, calificación, reseñas,
#  descripción, características)
PRODUCTOS = [
    ("Arroz blanco", 4_900, 5_600, "Despensa", False, 80, "500 g", 4.8, 1243,
     "Grano largo, ideal para el día a día.",
     [("Tipo", "Grano largo"), ("Presentación", "500 g"), ("Rendimiento", "8 porciones"), ("Origen", "Tolima")]),
    ("Fríjol cargamanto", 7_800, 0, "Despensa", False, 40, "500 g", 4.6, 318,
     "Fríjol rojo de grano grande.",
     [("Variedad", "Cargamanto rojo"), ("Presentación", "500 g"), ("Remojo", "8 horas"), ("Origen", "Antioquia")]),
    ("Lenteja", 3_900, 4_500, "Despensa", False, 55, "500 g", 4.5, 402,
     "Lenteja seleccionada, cocción rápida.",
     [("Tipo", "Lenteja verde"), ("Presentación", "500 g"), ("Cocción", "25 minutos"), ("Proteína", "24 g por 100 g")]),
    ("Panela", 3_200, 0, "Despensa", False, 60, "500 g", 4.9, 876,
     "Panela de caña en bloque.",
     [("Formato", "Bloque"), ("Presentación", "500 g"), ("Ingredientes", "100 % caña"), ("Origen", "Santander")]),
    ("Aceite de girasol", 12_900, 15_900, "Despensa", True, 35, "900 ml", 4.7, 655,
     "Aceite vegetal para cocinar.",
     [("Tipo", "Girasol refinado"), ("Contenido", "900 ml"), ("Envase", "Botella PET"), ("Grasas trans", "0 g")]),
    ("Café tostado molido", 15_400, 18_900, "Despensa", True, 30, "500 g", 4.9, 1530,
     "Café colombiano de tostión media.",
     [("Tostión", "Media"), ("Molienda", "Media"), ("Presentación", "500 g"), ("Origen", "Huila")]),
    ("Pasta spaghetti", 3_600, 0, "Despensa", True, 45, "500 g", 4.4, 210,
     "Pasta de trigo durum.",
     [("Tipo", "Spaghetti n.° 5"), ("Trigo", "Durum"), ("Cocción", "9 minutos"), ("Presentación", "500 g")]),
    ("Leche entera", 4_300, 0, "Lácteos y huevos", False, 70, "1 L", 4.7, 980,
     "Leche pasteurizada en bolsa.",
     [("Tipo", "Entera pasteurizada"), ("Contenido", "1 L"), ("Empaque", "Bolsa"), ("Grasa", "3 %")]),
    ("Huevos AA", 16_500, 19_800, "Lácteos y huevos", False, 25, "30 und", 4.8, 742,
     "Cubeta de huevos rojos frescos.",
     [("Tamaño", "AA"), ("Cantidad", "30 unidades"), ("Color", "Rojo"), ("Empaque", "Cubeta")]),
    ("Queso campesino", 9_800, 0, "Lácteos y huevos", True, 20, "500 g", 4.5, 288,
     "Queso fresco semiduro.",
     [("Tipo", "Semiduro"), ("Peso", "500 g"), ("Leche", "De vaca"), ("Conservación", "Refrigerado")]),
    ("Yogur de fresa", 6_200, 7_400, "Lácteos y huevos", True, 30, "1 L", 4.3, 190,
     "Yogur con trozos de fruta.",
     [("Sabor", "Fresa"), ("Contenido", "1 L"), ("Fruta", "Trozos naturales"), ("Conservación", "Refrigerado")]),
    ("Papa pastusa", 3_500, 0, "Frutas y verduras", False, 90, "1 kg", 4.6, 512,
     "Papa lavada para sopas y fritos.",
     [("Variedad", "Pastusa"), ("Peso", "1 kg"), ("Uso", "Sopas y fritos"), ("Origen", "Boyacá")]),
    ("Plátano verde", 2_800, 0, "Frutas y verduras", False, 60, "1 kg", 4.4, 233,
     "Para patacones.",
     [("Estado", "Verde"), ("Peso", "1 kg"), ("Uso", "Patacones"), ("Origen", "Quindío")]),
    ("Tomate chonto", 4_200, 4_900, "Frutas y verduras", False, 40, "1 kg", 4.2, 167,
     "Tomate maduro para guisos.",
     [("Variedad", "Chonto"), ("Peso", "1 kg"), ("Madurez", "Pintón a maduro"), ("Uso", "Guisos y salsas")]),
    ("Banano", 3_000, 0, "Frutas y verduras", False, 50, "1 kg", 4.7, 389,
     "Banano criollo.",
     [("Variedad", "Criollo"), ("Peso", "1 kg"), ("Madurez", "Listo para comer"), ("Origen", "Urabá")]),
    ("Gaseosa cola", 6_900, 7_900, "Bebidas", True, 48, "1,5 L", 4.6, 1104,
     "Bebida gaseosa sabor cola.",
     [("Sabor", "Cola"), ("Contenido", "1,5 L"), ("Envase", "Botella PET"), ("Azúcar", "Regular")]),
    ("Agua sin gas", 2_500, 0, "Bebidas", True, 60, "600 ml", 4.8, 640,
     "Agua de manantial.",
     [("Tipo", "Manantial"), ("Contenido", "600 ml"), ("Gas", "Sin gas"), ("Envase", "Botella PET")]),
    ("Jugo de naranja", 7_500, 9_200, "Bebidas", True, 25, "1 L", 4.5, 275,
     "Jugo natural sin azúcar añadido.",
     [("Sabor", "Naranja"), ("Contenido", "1 L"), ("Azúcar añadido", "No"), ("Conservación", "Refrigerado")]),
    ("Jabón de baño", 4_800, 0, "Aseo", True, 40, "3 und", 4.6, 431,
     "Jabón humectante en barra.",
     [("Tipo", "Humectante"), ("Cantidad", "3 barras"), ("Peso", "110 g c/u"), ("Aroma", "Avena")]),
    ("Detergente en polvo", 18_900, 23_900, "Aseo", True, 22, "2 kg", 4.7, 812,
     "Detergente para ropa blanca y de color.",
     [("Peso", "2 kg"), ("Lavados", "40"), ("Uso", "Ropa blanca y color"), ("Lavadora", "Apto")]),
    ("Papel higiénico", 21_500, 25_900, "Aseo", True, 18, "12 rollos", 4.8, 1012,
     "Papel doble hoja.",
     [("Hoja", "Doble"), ("Rollos", "12"), ("Metros por rollo", "30 m"), ("Textura", "Suave")]),
    ("Crema dental", 8_900, 0, "Aseo", True, 8, "100 ml", 4.5, 356,
     "Protección anticaries.",
     [("Protección", "Anticaries"), ("Contenido", "100 ml"), ("Flúor", "1.450 ppm"), ("Sabor", "Menta")]),
    ("Galletas de soda", 5_400, 0, "Snacks", True, 35, "9 paquetes", 4.4, 198,
     "Galletas saladas tradicionales.",
     [("Tipo", "Saladas"), ("Paquetes", "9"), ("Peso", "270 g"), ("Ideal para", "Onces")]),
    ("Chocolatina", 2_900, 3_400, "Snacks", True, 6, "1 und", 4.9, 2210,
     "Chocolate con leche.",
     [("Tipo", "Chocolate con leche"), ("Peso", "40 g"), ("Cacao", "32 %"), ("Unidades", "1")]),
    ("Papas fritas", 3_800, 0, "Snacks", True, 40, "110 g", 4.3, 154,
     "Papas fritas con sal.",
     [("Sabor", "Natural con sal"), ("Peso", "110 g"), ("Corte", "Liso"), ("Empaque", "Bolsa")]),
]


def sembrar_si_vacio(db: BaseDeDatos) -> None:
    """Crea el catálogo si la base está vacía. En bases creadas con la versión anterior
    completa calificación, reseñas, oferta y características de los productos de ejemplo."""
    repo = SqliteProductos(db)
    vacia = not db.ejecutar("SELECT COUNT(*) FROM productos").fetchone()[0]
    with db.transaccion():
        for (nombre, precio, antes, categoria, gravado, stock, unidad, nota, resenas,
             descripcion, caracteristicas) in PRODUCTOS:
            if vacia:
                repo.guardar(Producto(None, nombre, precio, categoria, gravado, stock, descripcion, unidad,
                                      precio_anterior=antes, calificacion=nota, resenas=resenas,
                                      caracteristicas=caracteristicas))
            else:
                db.ejecutar(
                    "UPDATE productos SET precio_anterior = CASE WHEN ? > precio THEN ? ELSE 0 END,"
                    " calificacion = ?, resenas = ?, caracteristicas = ?"
                    " WHERE nombre = ? AND resenas = 0 AND precio_anterior = 0",
                    (antes, antes, nota, resenas,
                     json.dumps([list(c) for c in caracteristicas], ensure_ascii=False), nombre))
