from flask import Blueprint, render_template
from app.auth.routes import login_required
from app.db import get_db
from app.aop import cache, metrics

bp = Blueprint("products", __name__, url_prefix="/products")


@bp.route("/")
@login_required
@metrics
@cache(ttl=60)
def list_products():
    """Shows a list of all products."""
    db = get_db()
    products = db.execute(
        "SELECT id, name, price, stock FROM product ORDER BY name"
    ).fetchall()
    return render_template("fragments/products.html", products=products)
