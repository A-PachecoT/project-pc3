# -*- coding: utf-8 -*-
"""
Módulo de visualización de transacciones.

Define la ruta para mostrar un listado paginado del historial de transacciones.
"""
from flask import Blueprint, render_template, request
from app.auth.routes import login_required
from app.db import get_db
from app.aop import cache, metrics

bp = Blueprint("transactions", __name__, url_prefix="/transactions")


@bp.route("/")
@login_required
@metrics
@cache(ttl=120)
def list_transactions():
    """
    Muestra una lista paginada del historial de transacciones.

    Obtiene el número de página de los argumentos de la URL. Recupera
    las transacciones correspondientes a esa página de la base de datos.
    El resultado se cachea durante 120 segundos para mejorar el rendimiento.
    """
    page = request.args.get("page", 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    transactions = db.execute(
        "SELECT id, description, amount, created_at FROM transaction_log ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    ).fetchall()

    return render_template(
        "fragments/transactions.html", transactions=transactions, page=page
    )
