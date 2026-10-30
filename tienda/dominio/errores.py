"""Errores de dominio. La capa HTTP los traduce a códigos de estado."""


class ErrorTienda(Exception):
    """Base de todos los errores de negocio de la tienda."""


class DatosInvalidos(ErrorTienda):
    """Los datos recibidos no cumplen las reglas (400)."""


class NoEncontrado(ErrorTienda):
    """El recurso solicitado no existe (404)."""


class StockInsuficiente(ErrorTienda):
    """No hay unidades suficientes para atender el pedido (409)."""


class TransicionInvalida(ErrorTienda):
    """El pedido no puede pasar al estado solicitado (409)."""


class NoAutorizado(ErrorTienda):
    """Credenciales de administración ausentes o incorrectas (401)."""
