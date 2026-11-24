import numpy as np
from flask import current_app, flash, render_template, request
from flask_login import login_required
from app.prediccion import prediccion_bp


@prediccion_bp.route("/prediccion", methods=["GET", "POST"])
@login_required
def index():
    resultado = None
    datos = {}

    if request.method == "POST":
        datos = request.form
        try:
            stock_actual = float(request.form.get("stock_actual", ""))
            ventas_diarias = float(request.form.get("ventas_diarias", ""))
            dias_entrega = float(request.form.get("dias_entrega", ""))
        except ValueError:
            flash("Todos los parámetros deben ser valores numéricos válidos.", "danger")
            return render_template("prediccion/index.html", resultado=None, datos=datos)

        if stock_actual < 0 or ventas_diarias <= 0 or dias_entrega < 1:
            flash(
                "Parámetros fuera de rango: stock >= 0, ventas diarias > 0 y días de entrega >= 1.",
                "danger",
            )
            return render_template("prediccion/index.html", resultado=None, datos=datos)

        model = current_app.config["ML_MODEL"]
        features = np.array([[stock_actual, ventas_diarias, dias_entrega]])
        prediccion = int(model.predict(features)[0])
        probabilidades = model.predict_proba(features)[0]
        prob_clase = float(probabilidades[prediccion]) * 100.0

        veredicto = "Necesita reposición" if prediccion == 1 else "Stock suficiente"
        resultado = {
            "necesita_reposicion": prediccion == 1,
            "veredicto": veredicto,
            "probabilidad": round(prob_clase, 1),
            "dias_cobertura": round(stock_actual / ventas_diarias, 1),
        }

    return render_template("prediccion/index.html", resultado=resultado, datos=datos)
