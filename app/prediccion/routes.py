from flask import render_template
from flask_login import login_required
from app.prediccion import prediccion_bp


@prediccion_bp.route("/prediccion", methods=["GET"])
@login_required
def index():
    return render_template("base.html")
