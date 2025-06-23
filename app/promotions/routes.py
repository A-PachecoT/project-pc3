# -*- coding: utf-8 -*-
"""
Módulo de gestión de promociones.

Define las rutas para visualizar y crear nuevas promociones.
El acceso y la funcionalidad de creación están controlados por
los aspectos `@feature_flag` y `@validate_with`.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.auth.routes import login_required
from app.db import get_db
from app.aop import feature_flag, validate_with
from app.schemas import PromotionSchema

bp = Blueprint("promotions", __name__, url_prefix="/promotions")


@bp.route("/", methods=("GET", "POST"))
@login_required
@feature_flag("promo_editor")
@validate_with(PromotionSchema, methods=["POST"])
def manage_promotions():
    """
    Gestiona la creación y visualización de promociones.

    Si el método es GET, muestra el listado de promociones existentes y un
    formulario para crear una nueva (si el feature flag 'promo_editor' está activo).
    Si el método es POST, la data del formulario es validada por el decorador
    `@validate_with`. Si es válida, se inserta la nueva promoción en la
    base de datos. Si no, el decorador maneja los errores.
    """
    db = get_db()

    if request.method == "POST":
        # La validación es manejada por el decorador @validate_with.
        # Se accede a los datos validados a través del objeto g.
        promo = g.validated_data

        db.execute(
            "INSERT INTO promotion (name, discount_percent, start_date, end_date) VALUES (?, ?, ?, ?)",
            (promo.name, promo.discount_percent, promo.start_date, promo.end_date),
        )
        db.commit()
        flash(f'Promoción "{promo.name}" creada exitosamente.')
        return redirect(url_for("promotions.manage_promotions"))

    promotions = db.execute(
        "SELECT id, name, discount_percent, start_date, end_date FROM promotion ORDER BY start_date DESC"
    ).fetchall()

    return render_template("fragments/promotions.html", promotions=promotions)
