from flask import Blueprint

prediccion_bp = Blueprint("prediccion", __name__)

from app.prediccion import routes
