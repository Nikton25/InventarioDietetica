import pytest
from app.extensions import db
from app.models import Producto


@pytest.fixture
def logged_in_client(client):
    client.post(
        "/login",
        data={"username": "admin_test", "password": "clave_segura_123"},
    )
    return client


def test_list_productos_empty(logged_in_client):
    response = logged_in_client.get("/productos")
    assert response.status_code == 200
    assert "No hay productos cargados" in response.get_data(as_text=True)


def test_create_producto_valid(logged_in_client, app):
    response = logged_in_client.post(
        "/productos/nuevo",
        data={
            "nombre": "Avena Arrollada",
            "categoria": "Cereales",
            "precio_unitario": "2400.50",
            "stock_actual": "35",
            "unidad_medida": "kg",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Avena Arrollada" in response.get_data(as_text=True)

    with app.app_context():
        prod = Producto.query.filter_by(nombre="Avena Arrollada").first()
        assert prod is not None
        assert prod.precio_unitario == 2400.50
        assert prod.stock_actual == 35.0


def test_create_producto_invalid_preserves_form_and_flashes_danger(logged_in_client, app):
    response = logged_in_client.post(
        "/productos/nuevo",
        data={
            "nombre": "Producto Inválido",
            "categoria": "CategoriaInexistente",
            "precio_unitario": "-10",
            "stock_actual": "5",
            "unidad_medida": "kg",
        },
        follow_redirects=True,
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "alert-danger" in text
    assert "Producto Inválido" in text

    with app.app_context():
        assert Producto.query.count() == 0


def test_edit_producto_and_404_when_missing(logged_in_client, app):
    with app.app_context():
        p = Producto(
            nombre="Semillas de Chía",
            categoria="Semillas",
            precio_unitario=5000.0,
            stock_actual=10.0,
            unidad_medida="kg",
        )
        db.session.add(p)
        db.session.commit()
        pid = p.id

    response = logged_in_client.post(
        f"/productos/{pid}/editar",
        data={
            "nombre": "Semillas de Chía Premium",
            "categoria": "Semillas",
            "precio_unitario": "5500",
            "stock_actual": "8.5",
            "unidad_medida": "kg",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Semillas de Chía Premium" in response.get_data(as_text=True)

    not_found = logged_in_client.get("/productos/9999/editar")
    assert not_found.status_code == 404


def test_delete_producto(logged_in_client, app):
    with app.app_context():
        p = Producto(
            nombre="Lentejas",
            categoria="Legumbres",
            precio_unitario=3200.0,
            stock_actual=20.0,
            unidad_medida="kg",
        )
        db.session.add(p)
        db.session.commit()
        pid = p.id

    response = logged_in_client.post(f"/productos/{pid}/eliminar", follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(Producto, pid) is None
