from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app.auth import auth_bp
from app.extensions import bcrypt
from app.models import Usuario


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("productos.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and bcrypt.check_password_hash(usuario.password_hash, password):
            login_user(usuario)
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for("productos.index"))

        flash("Credenciales inválidas. Verificá tu usuario y contraseña.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
