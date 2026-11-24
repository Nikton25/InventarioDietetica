from flask import render_template
from flask_login import login_required
from app.productos import productos_bp


@productos_bp.route("/", methods=["GET"])
@productos_bp.route("/productos", methods=["GET"])
@login_required
def index():
    return render_template("base.html")
