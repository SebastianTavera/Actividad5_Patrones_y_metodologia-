"""Entidades del dominio de la tienda. No dependen de Flask ni de SQLite."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from pedido import precio_publico

from .errores import DatosInvalidos


@dataclass
class Producto:
    id: int | None
    nombre: str
    precio: int
    categoria: str
    gravado: bool = True
    stock: int = 0
    descripcion: str = ""
    unidad: str = "und"
    activo: bool = True
    precio_anterior: int = 0          # precio de referencia tachado (0 = sin oferta)
    calificacion: float = 0.0         # promedio de 0 a 5
    resenas: int = 0
    caracteristicas: list[tuple[str, str]] = field(default_factory=list)

    @property
    def descuento_pct(self) -> int:
        if self.precio_anterior <= self.precio:
            return 0
        return round((self.precio_anterior - self.precio) * 100 / self.precio_anterior)

    def validar(self) -> None:
        errores = []
        if not self.nombre.strip():
            errores.append("El nombre es obligatorio")
        if self.precio <= 0:
            errores.append("El precio debe ser mayor a 0")
        if self.precio_anterior and self.precio_anterior <= self.precio:
            errores.append("El precio anterior debe ser mayor al precio actual (o 0 si no hay oferta)")
        if not 0 <= self.calificacion <= 5:
            errores.append("La calificación debe estar entre 0 y 5")
        if self.stock < 0:
            errores.append("El stock no puede ser negativo")
        if not self.categoria.strip():
            errores.append("La categoría es obligatoria")
        if errores:
            raise DatosInvalidos("; ".join(errores))

    def a_dict(self) -> dict:
        return {
            "id": self.id, "nombre": self.nombre, "precio": self.precio,
            "categoria": self.categoria, "gravado": self.gravado, "stock": self.stock,
            "descripcion": self.descripcion, "unidad": self.unidad, "activo": self.activo,
            "precio_anterior": self.precio_anterior, "descuento_pct": self.descuento_pct,
            "precio_final": precio_publico(self.precio, self.gravado),
            "precio_anterior_final": precio_publico(self.precio_anterior, self.gravado) if self.precio_anterior else 0,
            "calificacion": self.calificacion, "resenas": self.resenas,
            "caracteristicas": [list(c) for c in self.caracteristicas],
        }


@dataclass(frozen=True)
class Cliente:
    nombre: str
    telefono: str
    direccion: str

    def validar(self) -> None:
        errores = []
        if len(self.nombre.strip()) < 3:
            errores.append("Escribe tu nombre completo")
        digitos = "".join(c for c in self.telefono if c.isdigit())
        if len(digitos) < 7 or len(digitos) > 12:
            errores.append("El teléfono debe tener entre 7 y 12 dígitos")
        if len(self.direccion.strip()) < 5:
            errores.append("Escribe una dirección de entrega válida")
        if errores:
            raise DatosInvalidos("; ".join(errores))


@dataclass(frozen=True)
class LineaPedido:
    producto_id: int
    nombre: str
    precio: int
    cantidad: int
    gravado: bool

    @property
    def importe(self) -> int:
        return self.precio * self.cantidad


class EstadoPedido(str, Enum):
    RECIBIDO = "recibido"
    PREPARANDO = "preparando"
    EN_CAMINO = "en_camino"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


# Transiciones válidas del ciclo de vida del pedido.
TRANSICIONES: dict[EstadoPedido, set[EstadoPedido]] = {
    EstadoPedido.RECIBIDO: {EstadoPedido.PREPARANDO, EstadoPedido.CANCELADO},
    EstadoPedido.PREPARANDO: {EstadoPedido.EN_CAMINO, EstadoPedido.CANCELADO},
    EstadoPedido.EN_CAMINO: {EstadoPedido.ENTREGADO},
    EstadoPedido.ENTREGADO: set(),
    EstadoPedido.CANCELADO: set(),
}


@dataclass
class Pedido:
    id: int | None
    cliente: Cliente
    lineas: list[LineaPedido]
    subtotal: int
    descuento: int
    iva: int
    domicilio: int
    total: int
    estado: EstadoPedido = EstadoPedido.RECIBIDO
    creado: datetime = field(default_factory=datetime.now)
    notas: str = ""

    def puede_pasar_a(self, nuevo: EstadoPedido) -> bool:
        return nuevo in TRANSICIONES[self.estado]

    def a_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente": {"nombre": self.cliente.nombre, "telefono": self.cliente.telefono,
                        "direccion": self.cliente.direccion},
            "lineas": [{"producto_id": l.producto_id, "nombre": l.nombre, "precio": l.precio,
                        "cantidad": l.cantidad, "gravado": l.gravado, "importe": l.importe}
                       for l in self.lineas],
            "subtotal": self.subtotal, "descuento": self.descuento, "iva": self.iva,
            "domicilio": self.domicilio, "total": self.total,
            "estado": self.estado.value, "creado": self.creado.isoformat(timespec="seconds"),
            "notas": self.notas,
            "siguientes_estados": sorted(e.value for e in TRANSICIONES[self.estado]),
        }
