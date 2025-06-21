from flask import Blueprint, render_template, abort
from app.auth.routes import login_required
from app.db import get_db
from app.aop import audit

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/<int:id>")
@login_required
@audit(action="view_order")
def view_order(id):
    """Shows details for a specific order."""
    db = get_db()
    order = db.execute(
        'SELECT id, customer_name, total_amount, status, created_at FROM "order" WHERE id = ?',
        (id,),
    ).fetchone()

    if order is None:
        abort(404, f"Order id {id} doesn't exist.")

    return render_template("fragments/order_detail.html", order=order)
