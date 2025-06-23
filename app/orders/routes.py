# -*- coding: utf-8 -*-
"""
Módulo de gestión de pedidos (órdenes).

Define las rutas relacionadas con la visualización de los pedidos.
"""
from flask import Blueprint, render_template, abort
from app.auth.routes import login_required
from app.db import get_db
from app.aop import audit

bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/<int:id>")
@login_required
@audit(action="view_order")
def view_order(id):
    """
    Muestra los detalles de un pedido específico.

    Recupera un pedido por su ID de la base de datos y lo muestra
    en una plantilla. Si el pedido no existe, devuelve un error 404.
    La acción es registrada por el decorador `@audit`.

    Args:
        id (int): El ID del pedido a visualizar.
    """
    db = get_db()
    order = db.execute(
        'SELECT id, customer_name, total_amount, status, created_at FROM "order" WHERE id = ?',
        (id,),
    ).fetchone()

    if order is None:
        abort(404, f"El pedido con id {id} no existe.")

    return render_template("fragments/order_detail.html", order=order)
