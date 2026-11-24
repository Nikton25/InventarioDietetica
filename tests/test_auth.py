def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Iniciar Sesión" in response.get_data(as_text=True)


def test_login_success_and_logout(client):
    response = client.post(
        "/login",
        data={"username": "admin_test", "password": "clave_segura_123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Salir" in text

    logout_resp = client.get("/logout", follow_redirects=True)
    assert logout_resp.status_code == 200
    assert "Iniciar Sesión" in logout_resp.get_data(as_text=True)


def test_login_invalid_credentials_shows_error(client):
    response = client.post(
        "/login",
        data={"username": "admin_test", "password": "wrong_password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Credenciales inválidas" in response.get_data(as_text=True)


def test_unauthenticated_access_redirects_to_login(client):
    response = client.get("/productos", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
