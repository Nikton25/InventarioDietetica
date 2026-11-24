from flask_login import UserMixin
from app.extensions import db, login_manager

CATEGORIAS_VALIDAS = (
    "Cereales",
    "Semillas",
    "Legumbres",
    "Aceites",
    "Infusiones",
    "Frutos Secos",
)

UNIDADES_VALIDAS = (
    "kg",
    "gramos",
    "litros",
    "unidades",
    "paquetes",
)


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Producto(db.Model):
    __tablename__ = "producto"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    stock_actual = db.Column(db.Float, nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)


@login_manager.user_loader
def load_user(user_id: str) -> Usuario | None:
    return db.session.get(Usuario, int(user_id))
