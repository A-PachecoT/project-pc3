# -*- coding: utf-8 -*-
"""
Módulo de gestión de productos.

Define las rutas para visualizar el listado de productos.
"""
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
    """
    Muestra un listado de todos los productos disponibles.

    Recupera todos los productos de la base de datos y los muestra
    en una plantilla. El resultado de esta vista se cachea durante 60 segundos
    y su tiempo de ejecución es medido, gracias a los decoradores `@cache` y
    `@metrics`.
    """
    db = get_db()
    products = db.execute(
        "SELECT id, name, price, stock FROM product ORDER BY name"
    ).fetchall()
    return render_template("fragments/products.html", products=products)
