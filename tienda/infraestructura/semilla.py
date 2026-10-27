"""Catálogo inicial de una tienda de barrio bogotana."""
from ..dominio.modelos import Producto
from .sqlite import BaseDeDatos, SqliteProductos

# (nombre, precio, categoría, gravado, stock, unidad, descripción)
PRODUCTOS = [
    ("Arroz blanco", 4_900, "Despensa", False, 80, "500 g", "Grano largo, ideal para el día a día."),
    ("Fríjol cargamanto", 7_800, "Despensa", False, 40, "500 g", "Fríjol rojo de grano grande."),
    ("Lenteja", 3_900, "Despensa", False, 55, "500 g", "Lenteja seleccionada, cocción rápida."),
    ("Panela", 3_200, "Despensa", False, 60, "500 g", "Panela de caña en bloque."),
    ("Aceite de girasol", 12_900, "Despensa", True, 35, "900 ml", "Aceite vegetal para cocinar."),
    ("Café tostado molido", 15_400, "Despensa", True, 30, "500 g", "Café colombiano de tostión media."),
    ("Pasta spaghetti", 3_600, "Despensa", True, 45, "500 g", "Pasta de trigo durum."),
    ("Leche entera", 4_300, "Lácteos y huevos", False, 70, "1 L", "Leche pasteurizada en bolsa."),
    ("Huevos AA", 16_500, "Lácteos y huevos", False, 25, "30 und", "Cubeta de huevos rojos frescos."),
    ("Queso campesino", 9_800, "Lácteos y huevos", True, 20, "500 g", "Queso fresco semiduro."),
    ("Yogur de fresa", 6_200, "Lácteos y huevos", True, 30, "1 L", "Yogur con trozos de fruta."),
    ("Papa pastusa", 3_500, "Frutas y verduras", False, 90, "1 kg", "Papa lavada para sopas y fritos."),
    ("Plátano verde", 2_800, "Frutas y verduras", False, 60, "1 kg", "Para patacones."),
    ("Tomate chonto", 4_200, "Frutas y verduras", False, 40, "1 kg", "Tomate maduro para guisos."),
    ("Banano", 3_000, "Frutas y verduras", False, 50, "1 kg", "Banano criollo."),
    ("Gaseosa cola", 6_900, "Bebidas", True, 48, "1,5 L", "Bebida gaseosa sabor cola."),
    ("Agua sin gas", 2_500, "Bebidas", True, 60, "600 ml", "Agua de manantial."),
    ("Jugo de naranja", 7_500, "Bebidas", True, 25, "1 L", "Jugo natural sin azúcar añadido."),
    ("Jabón de baño", 4_800, "Aseo", True, 40, "3 und", "Jabón humectante en barra."),
    ("Detergente en polvo", 18_900, "Aseo", True, 22, "2 kg", "Detergente para ropa blanca y de color."),
    ("Papel higiénico", 21_500, "Aseo", True, 18, "12 rollos", "Papel doble hoja."),
    ("Crema dental", 8_900, "Aseo", True, 8, "100 ml", "Protección anticaries."),
    ("Galletas de soda", 5_400, "Snacks", True, 35, "9 paquetes", "Galletas saladas tradicionales."),
    ("Chocolatina", 2_900, "Snacks", True, 6, "1 und", "Chocolate con leche."),
    ("Papas fritas", 3_800, "Snacks", True, 40, "110 g", "Papas fritas con sal."),
]


def sembrar_si_vacio(db: BaseDeDatos) -> None:
    if db.ejecutar("SELECT COUNT(*) FROM productos").fetchone()[0]:
        return
    repo = SqliteProductos(db)
    with db.transaccion():
        for nombre, precio, categoria, gravado, stock, unidad, descripcion in PRODUCTOS:
            repo.guardar(Producto(None, nombre, precio, categoria, gravado, stock, descripcion, unidad))
