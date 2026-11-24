from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from app.extensions import db
from app.models import CATEGORIAS_VALIDAS, UNIDADES_VALIDAS, Producto
from app.productos import productos_bp


def validate_producto_form(form_data: dict) -> tuple[dict | None, str | None]:
    nombre = form_data.get("nombre", "").strip()
    categoria = form_data.get("categoria", "").strip()
    unidad_medida = form_data.get("unidad_medida", "").strip()
    precio_raw = form_data.get("precio_unitario", "").strip()
    stock_raw = form_data.get("stock_actual", "").strip()

    if not nombre or not categoria or not unidad_medida or not precio_raw or not stock_raw:
        return None, "Todos los campos son obligatorios."

    if categoria not in CATEGORIAS_VALIDAS:
        return None, "La categoría seleccionada no es válida."

    if unidad_medida not in UNIDADES_VALIDAS:
        return None, "La unidad de medida seleccionada no es válida."

    try:
        precio_unitario = float(precio_raw)
        stock_actual = float(stock_raw)
    except ValueError:
        return None, "El precio unitario y el stock actual deben ser valores numéricos."

    if precio_unitario < 0 or stock_actual < 0:
        return None, "El precio unitario y el stock actual no pueden ser negativos."

    return {
        "nombre": nombre,
        "categoria": categoria,
        "precio_unitario": precio_unitario,
        "stock_actual": stock_actual,
        "unidad_medida": unidad_medida,
    }, None


@productos_bp.route("/", methods=["GET"])
@productos_bp.route("/productos", methods=["GET"])
@login_required
def index():
    productos = Producto.query.order_by(Producto.nombre.asc()).all()
    return render_template("productos/index.html", productos=productos)


@productos_bp.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if request.method == "POST":
        cleaned, error = validate_producto_form(request.form)
        if error:
            flash(error, "danger")
            return render_template(
                "productos/form.html",
                modo="nuevo",
                datos=request.form,
                categorias=CATEGORIAS_VALIDAS,
                unidades=UNIDADES_VALIDAS,
            )

        producto = Producto(**cleaned)
        db.session.add(producto)
        db.session.commit()
        flash(f"Producto '{producto.nombre}' creado correctamente.", "success")
        return redirect(url_for("productos.index"))

    return render_template(
        "productos/form.html",
        modo="nuevo",
        datos={},
        categorias=CATEGORIAS_VALIDAS,
        unidades=UNIDADES_VALIDAS,
    )


@productos_bp.route("/productos/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id: int):
    producto = db.get_or_404(Producto, id)

    if request.method == "POST":
        cleaned, error = validate_producto_form(request.form)
        if error:
            flash(error, "danger")
            return render_template(
                "productos/form.html",
                modo="editar",
                producto=producto,
                datos=request.form,
                categorias=CATEGORIAS_VALIDAS,
                unidades=UNIDADES_VALIDAS,
            )

        producto.nombre = cleaned["nombre"]
        producto.categoria = cleaned["categoria"]
        producto.precio_unitario = cleaned["precio_unitario"]
        producto.stock_actual = cleaned["stock_actual"]
        producto.unidad_medida = cleaned["unidad_medida"]
        db.session.commit()
        flash(f"Producto '{producto.nombre}' actualizado correctamente.", "success")
        return redirect(url_for("productos.index"))

    datos_iniciales = {
        "nombre": producto.nombre,
        "categoria": producto.categoria,
        "precio_unitario": producto.precio_unitario,
        "stock_actual": producto.stock_actual,
        "unidad_medida": producto.unidad_medida,
    }
    return render_template(
        "productos/form.html",
        modo="editar",
        producto=producto,
        datos=datos_iniciales,
        categorias=CATEGORIAS_VALIDAS,
        unidades=UNIDADES_VALIDAS,
    )


@productos_bp.route("/productos/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id: int):
    producto = db.get_or_404(Producto, id)
    nombre = producto.nombre
    db.session.delete(producto)
    db.session.commit()
    flash(f"Producto '{nombre}' eliminado.", "info")
    return redirect(url_for("productos.index"))
