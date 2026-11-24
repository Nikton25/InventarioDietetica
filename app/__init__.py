from pathlib import Path
import click
import joblib
from flask import Flask
from app.config import Config
from app.extensions import bcrypt, db, login_manager
from app.models import Usuario


def ensure_admin_user(app: Flask) -> Usuario | None:
    username = app.config.get("ADMIN_USERNAME")
    password = app.config.get("ADMIN_PASSWORD")
    if not username or not password:
        return None

    existing = Usuario.query.filter_by(username=username).first()
    if existing:
        return existing

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    admin = Usuario(username=username, password_hash=password_hash)
    db.session.add(admin)
    db.session.commit()
    return admin


def load_ml_model(app: Flask) -> None:
    model_path = Path(app.config["MODEL_PATH"])
    if not model_path.exists():
        from ml.train_model import train_and_save_model

        train_and_save_model(model_path)
    app.config["ML_MODEL"] = joblib.load(model_path)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    load_ml_model(app)

    from app.auth import auth_bp
    from app.prediccion import prediccion_bp
    from app.productos import productos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(prediccion_bp)

    @app.cli.command("crear-admin")
    def crear_admin_command() -> None:
        """Crea el usuario administrador inicial desde las variables de entorno."""
        admin = ensure_admin_user(app)
        if admin:
            click.echo(f"Usuario administrador '{admin.username}' disponible.")
        else:
            click.echo("Definí ADMIN_USERNAME y ADMIN_PASSWORD en el entorno.")

    with app.app_context():
        db.create_all()
        ensure_admin_user(app)

    return app
