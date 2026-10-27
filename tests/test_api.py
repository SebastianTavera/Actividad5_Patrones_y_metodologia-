"""Pruebas de integración: Flask + SQLite real en una carpeta temporal."""
import pytest

from app import crear_app

ADMIN = {"X-Admin-Clave": "secreta"}
CLIENTE = {"nombre": "Ana Gómez", "telefono": "3105551234", "direccion": "Calle 45 # 12-30"}


@pytest.fixture
def cliente(tmp_path):
    app = crear_app(ruta_db=str(tmp_path / "prueba.db"), clave_admin="secreta")
    return app.test_client()


def _id(cliente, nombre):
    return next(p["id"] for p in cliente.get("/api/productos").get_json() if p["nombre"] == nombre)


def test_pagina_principal_se_sirve(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert b"MercaBarrio" in respuesta.data


def test_catalogo_sembrado_y_busqueda(cliente):
    assert len(cliente.get("/api/productos").get_json()) >= 20
    encontrados = cliente.get("/api/productos?q=arroz").get_json()
    assert [p["nombre"] for p in encontrados] == ["Arroz blanco"]
    assert "Despensa" in cliente.get("/api/categorias").get_json()


def test_reglas_expuestas_para_la_interfaz(cliente):
    assert cliente.get("/api/reglas").get_json()["umbral_domicilio"] == 50_000


def test_cotizar_carrito(cliente):
    arroz = _id(cliente, "Arroz blanco")
    datos = cliente.post("/api/carrito/cotizar", json={"items": [{"producto_id": arroz, "cantidad": 2}]}).get_json()
    assert (datos["subtotal"], datos["domicilio"], datos["total"]) == (9_800, 4_000, 13_800)


def test_cotizar_cantidad_cero_responde_400(cliente):
    arroz = _id(cliente, "Arroz blanco")
    respuesta = cliente.post("/api/carrito/cotizar", json={"items": [{"producto_id": arroz, "cantidad": 0}]})
    assert respuesta.status_code == 400
    assert "Arroz" in respuesta.get_json()["error"]


def test_flujo_completo_de_compra(cliente):
    huevos = _id(cliente, "Huevos AA")
    stock_inicial = cliente.get(f"/api/productos/{huevos}").get_json()["stock"]
    respuesta = cliente.post("/api/pedidos", json={"cliente": CLIENTE, "items": [{"producto_id": huevos, "cantidad": 4}]})
    assert respuesta.status_code == 201
    pedido = respuesta.get_json()
    assert pedido["total"] == 66_000 and pedido["estado"] == "recibido"
    assert cliente.get(f"/api/productos/{huevos}").get_json()["stock"] == stock_inicial - 4

    mios = cliente.get("/api/pedidos?telefono=310 555 1234").get_json()
    assert [p["id"] for p in mios] == [pedido["id"]]

    cancelado = cliente.post(f"/api/pedidos/{pedido['id']}/cancelar", json={"telefono": "3105551234"})
    assert cancelado.get_json()["estado"] == "cancelado"
    assert cliente.get(f"/api/productos/{huevos}").get_json()["stock"] == stock_inicial


def test_pedido_sin_stock_responde_409(cliente):
    chocolatina = _id(cliente, "Chocolatina")
    respuesta = cliente.post("/api/pedidos", json={"cliente": CLIENTE, "items": [{"producto_id": chocolatina, "cantidad": 500}]})
    assert respuesta.status_code == 409


def test_pedido_con_cuerpo_invalido_responde_400(cliente):
    assert cliente.post("/api/pedidos", data="no es json").status_code == 400


def test_admin_requiere_clave(cliente):
    assert cliente.get("/api/admin/resumen").status_code == 401
    assert cliente.get("/api/admin/resumen", headers={"X-Admin-Clave": "otra"}).status_code == 401
    assert cliente.get("/api/admin/resumen", headers=ADMIN).status_code == 200


def test_admin_gestiona_productos(cliente):
    creado = cliente.post("/api/admin/productos", headers=ADMIN, json={
        "nombre": "Sal refinada", "precio": 1_800, "categoria": "Despensa", "gravado": False, "stock": 12})
    assert creado.status_code == 201
    pid = creado.get_json()["id"]
    editado = cliente.put(f"/api/admin/productos/{pid}", headers=ADMIN, json={"precio": 2_000})
    assert editado.get_json()["precio"] == 2_000
    assert cliente.delete(f"/api/admin/productos/{pid}", headers=ADMIN).status_code == 204
    assert cliente.get(f"/api/productos/{pid}").status_code == 404


def test_admin_avanza_estado_y_rechaza_transicion_invalida(cliente):
    arroz = _id(cliente, "Arroz blanco")
    pedido = cliente.post("/api/pedidos", json={"cliente": CLIENTE, "items": [{"producto_id": arroz, "cantidad": 1}]}).get_json()
    url = f"/api/admin/pedidos/{pedido['id']}"
    assert cliente.patch(url, headers=ADMIN, json={"estado": "entregado"}).status_code == 409
    assert cliente.patch(url, headers=ADMIN, json={"estado": "preparando"}).get_json()["estado"] == "preparando"
    resumen = cliente.get("/api/admin/resumen", headers=ADMIN).get_json()
    assert resumen["pedidos"] == 1 and resumen["por_estado"]["preparando"] == 1
