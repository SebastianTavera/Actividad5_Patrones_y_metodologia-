"""Adaptadores SQLite de los puertos del dominio (solo librería estándar)."""
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime

from ..dominio.errores import StockInsuficiente
from ..dominio.modelos import Cliente, EstadoPedido, LineaPedido, Pedido, Producto
from ..dominio.puertos import CatalogoLectura, InventarioEscritura, RepositorioPedidos

ESQUEMA = """
CREATE TABLE IF NOT EXISTS productos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT    NOT NULL,
    precio      INTEGER NOT NULL CHECK (precio > 0),
    categoria   TEXT    NOT NULL,
    gravado     INTEGER NOT NULL DEFAULT 1,
    stock       INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    descripcion TEXT    NOT NULL DEFAULT '',
    unidad      TEXT    NOT NULL DEFAULT 'und',
    activo      INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS pedidos (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL,
    telefono  TEXT NOT NULL,
    direccion TEXT NOT NULL,
    subtotal  INTEGER NOT NULL,
    descuento INTEGER NOT NULL,
    iva       INTEGER NOT NULL,
    domicilio INTEGER NOT NULL,
    total     INTEGER NOT NULL,
    estado    TEXT NOT NULL,
    creado    TEXT NOT NULL,
    notas     TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS lineas_pedido (
    pedido_id   INTEGER NOT NULL REFERENCES pedidos(id),
    producto_id INTEGER NOT NULL,
    nombre      TEXT    NOT NULL,
    precio      INTEGER NOT NULL,
    cantidad    INTEGER NOT NULL,
    gravado     INTEGER NOT NULL
);
"""


class BaseDeDatos:
    """Una conexión por hilo; implementa la unidad de trabajo (transacciones anidables)."""

    def __init__(self, ruta: str):
        self._ruta = ruta
        self._local = threading.local()
        self.script(ESQUEMA)

    @property
    def _conexion(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conexion"):
            conexion = sqlite3.connect(self._ruta, isolation_level=None, timeout=10)
            conexion.row_factory = sqlite3.Row
            conexion.execute("PRAGMA foreign_keys = ON")
            self._local.conexion = conexion
            self._local.profundidad = 0
        return self._local.conexion

    def script(self, sql: str) -> None:
        self._conexion.executescript(sql)

    def ejecutar(self, sql: str, parametros: tuple = ()) -> sqlite3.Cursor:
        return self._conexion.execute(sql, parametros)

    @contextmanager
    def transaccion(self):
        conexion = self._conexion
        if self._local.profundidad == 0:
            conexion.execute("BEGIN IMMEDIATE")
        self._local.profundidad += 1
        try:
            yield
        except BaseException:
            self._local.profundidad -= 1
            if self._local.profundidad == 0:
                conexion.execute("ROLLBACK")
            raise
        else:
            self._local.profundidad -= 1
            if self._local.profundidad == 0:
                conexion.execute("COMMIT")


def _producto(fila: sqlite3.Row) -> Producto:
    return Producto(id=fila["id"], nombre=fila["nombre"], precio=fila["precio"],
                    categoria=fila["categoria"], gravado=bool(fila["gravado"]), stock=fila["stock"],
                    descripcion=fila["descripcion"], unidad=fila["unidad"], activo=bool(fila["activo"]))


class SqliteProductos(CatalogoLectura, InventarioEscritura):
    def __init__(self, db: BaseDeDatos):
        self._db = db

    def listar(self, texto: str = "", categoria: str = "", solo_activos: bool = True) -> list[Producto]:
        sql, parametros = "SELECT * FROM productos WHERE 1=1", []
        if solo_activos:
            sql += " AND activo = 1"
        if texto:
            sql += " AND (nombre LIKE ? OR descripcion LIKE ? OR categoria LIKE ?)"
            parametros += [f"%{texto}%"] * 3
        if categoria:
            sql += " AND categoria = ?"
            parametros.append(categoria)
        return [_producto(f) for f in self._db.ejecutar(sql + " ORDER BY id", tuple(parametros))]

    def obtener(self, producto_id: int) -> Producto | None:
        fila = self._db.ejecutar("SELECT * FROM productos WHERE id = ?", (producto_id,)).fetchone()
        return _producto(fila) if fila else None

    def categorias(self) -> list[str]:
        filas = self._db.ejecutar(
            "SELECT DISTINCT categoria FROM productos WHERE activo = 1 ORDER BY categoria")
        return [f["categoria"] for f in filas]

    def guardar(self, producto: Producto) -> Producto:
        valores = (producto.nombre, producto.precio, producto.categoria, int(producto.gravado),
                   producto.stock, producto.descripcion, producto.unidad, int(producto.activo))
        if producto.id is None:
            cursor = self._db.ejecutar(
                "INSERT INTO productos (nombre, precio, categoria, gravado, stock, descripcion, unidad, activo)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)", valores)
            producto.id = cursor.lastrowid
        else:
            self._db.ejecutar(
                "UPDATE productos SET nombre=?, precio=?, categoria=?, gravado=?, stock=?,"
                " descripcion=?, unidad=?, activo=? WHERE id=?", valores + (producto.id,))
        return producto

    def desactivar(self, producto_id: int) -> bool:
        cursor = self._db.ejecutar(
            "UPDATE productos SET activo = 0 WHERE id = ? AND activo = 1", (producto_id,))
        return cursor.rowcount == 1

    def ajustar_stock(self, producto_id: int, delta: int) -> None:
        cursor = self._db.ejecutar(
            "UPDATE productos SET stock = stock + ? WHERE id = ? AND stock + ? >= 0",
            (delta, producto_id, delta))
        if cursor.rowcount != 1:
            raise StockInsuficiente(f"No hay unidades suficientes del producto {producto_id}")


class SqlitePedidos(RepositorioPedidos):
    def __init__(self, db: BaseDeDatos):
        self._db = db

    def guardar(self, pedido: Pedido) -> Pedido:
        with self._db.transaccion():
            c = pedido.cliente
            cursor = self._db.ejecutar(
                "INSERT INTO pedidos (nombre, telefono, direccion, subtotal, descuento, iva,"
                " domicilio, total, estado, creado, notas) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (c.nombre, c.telefono, c.direccion, pedido.subtotal, pedido.descuento, pedido.iva,
                 pedido.domicilio, pedido.total, pedido.estado.value,
                 pedido.creado.isoformat(timespec="seconds"), pedido.notas))
            pedido.id = cursor.lastrowid
            for l in pedido.lineas:
                self._db.ejecutar(
                    "INSERT INTO lineas_pedido (pedido_id, producto_id, nombre, precio, cantidad, gravado)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (pedido.id, l.producto_id, l.nombre, l.precio, l.cantidad, int(l.gravado)))
        return pedido

    def obtener(self, pedido_id: int) -> Pedido | None:
        fila = self._db.ejecutar("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
        return self._pedido(fila) if fila else None

    def listar(self, telefono: str = "", estado: str = "") -> list[Pedido]:
        sql, parametros = "SELECT * FROM pedidos WHERE 1=1", []
        if telefono:
            sql += " AND telefono = ?"
            parametros.append(telefono)
        if estado:
            sql += " AND estado = ?"
            parametros.append(estado)
        filas = self._db.ejecutar(sql + " ORDER BY id DESC", tuple(parametros)).fetchall()
        return [self._pedido(f) for f in filas]

    def cambiar_estado(self, pedido_id: int, estado: EstadoPedido) -> None:
        self._db.ejecutar("UPDATE pedidos SET estado = ? WHERE id = ?", (estado.value, pedido_id))

    def _pedido(self, fila: sqlite3.Row) -> Pedido:
        lineas = [LineaPedido(l["producto_id"], l["nombre"], l["precio"], l["cantidad"], bool(l["gravado"]))
                  for l in self._db.ejecutar(
                      "SELECT * FROM lineas_pedido WHERE pedido_id = ? ORDER BY rowid", (fila["id"],))]
        return Pedido(
            id=fila["id"], cliente=Cliente(fila["nombre"], fila["telefono"], fila["direccion"]),
            lineas=lineas, subtotal=fila["subtotal"], descuento=fila["descuento"], iva=fila["iva"],
            domicilio=fila["domicilio"], total=fila["total"], estado=EstadoPedido(fila["estado"]),
            creado=datetime.fromisoformat(fila["creado"]), notas=fila["notas"])
