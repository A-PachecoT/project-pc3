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
    """Manage promotions."""
    db = get_db()

    if request.method == "POST":
        # Validation is now handled by the @validate_with decorator.
        # Access the validated data from the g object.
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
