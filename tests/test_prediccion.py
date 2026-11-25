import pytest


@pytest.fixture
def logged_in_client(client):
    client.post(
        "/login",
        data={"username": "admin_test", "password": "clave_segura_123"},
    )
    return client


def test_prediccion_get_renders_form(logged_in_client):
    response = logged_in_client.get("/prediccion")
    assert response.status_code == 200
    assert "Predicción de Reposición" in response.get_data(as_text=True)


def test_prediccion_post_necesita_reposicion(logged_in_client):
    response = logged_in_client.post(
        "/prediccion",
        data={
            "stock_actual": "4",
            "ventas_diarias": "8",
            "dias_entrega": "7",
        },
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Necesita reposición" in text
    assert "%" in text


def test_prediccion_post_stock_suficiente(logged_in_client):
    response = logged_in_client.post(
        "/prediccion",
        data={
            "stock_actual": "90",
            "ventas_diarias": "1.5",
            "dias_entrega": "2",
        },
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Stock suficiente" in text
    assert "%" in text


def test_prediccion_post_low_stock_low_sales_necesita_reposicion(logged_in_client):
    response = logged_in_client.post(
        "/prediccion",
        data={
            "stock_actual": "2",
            "ventas_diarias": "1.5",
            "dias_entrega": "5",
        },
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Necesita reposición" in text
    assert "%" in text


def test_prediccion_post_invalid_values_flashes_danger(logged_in_client):
    response = logged_in_client.post(
        "/prediccion",
        data={
            "stock_actual": "10",
            "ventas_diarias": "0",
            "dias_entrega": "0",
        },
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "alert-danger" in text
