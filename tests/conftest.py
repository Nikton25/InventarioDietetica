import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key",
            "ADMIN_USERNAME": "admin_test",
            "ADMIN_PASSWORD": "clave_segura_123",
        }
    )
    yield test_app
    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
