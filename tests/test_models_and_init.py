from app.config import normalize_database_url
from app.extensions import bcrypt, db
from app.models import Producto, Usuario


def test_normalize_database_url_converts_postgres_prefix():
    raw = "postgres://user:pass@localhost:5432/dbname"
    assert normalize_database_url(raw) == "postgresql://user:pass@localhost:5432/dbname"
    assert normalize_database_url(None) == "sqlite:///dietetica.db"


def test_admin_user_created_automatically_on_startup(app):
    with app.app_context():
        admin = Usuario.query.filter_by(username="admin_test").first()
        assert admin is not None
        assert bcrypt.check_password_hash(admin.password_hash, "clave_segura_123")


def test_producto_model_persistence(app):
    with app.app_context():
        prod = Producto(
            nombre="Almendras Nonpareil",
            categoria="Frutos Secos",
            precio_unitario=18500.0,
            stock_actual=12.5,
            unidad_medida="kg",
        )
        db.session.add(prod)
        db.session.commit()

        saved = db.session.get(Producto, prod.id)
        assert saved is not None
        assert saved.nombre == "Almendras Nonpareil"
        assert saved.categoria == "Frutos Secos"
        assert saved.precio_unitario == 18500.0
        assert saved.stock_actual == 12.5
        assert saved.unidad_medida == "kg"


def test_ml_model_loaded_in_app_config(app):
    assert "ML_MODEL" in app.config
    assert app.config["ML_MODEL"] is not None


def test_crear_admin_cli_command(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["crear-admin"])
    assert result.exit_code == 0
    assert "admin_test" in result.output
