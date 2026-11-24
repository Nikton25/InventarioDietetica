from flask import Blueprint

productos_bp = Blueprint("productos", __name__)

from app.productos import routes  