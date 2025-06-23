# -*- coding: utf-8 -*-
"""
Módulo de autenticación y gestión de usuarios.

Define las rutas para el login, logout y la gestión de la sesión de usuario.
También incluye el decorador `login_required` para proteger vistas que
requieren que un usuario haya iniciado sesión.
"""
import functools
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db
from app.aop import secure

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """
    Gestiona el inicio de sesión del usuario.

    Si el método es POST, valida las credenciales del usuario contra la base de datos.
    Si son correctas, guarda el ID del usuario en la sesión y redirige
    a la lista de productos. Si no, muestra un error.
    Si el método es GET, simplemente muestra el formulario de login.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Usuario incorrecto."
        elif not check_password_hash(user["password"], password):
            error = "Contraseña incorrecta."

        if error is None:
            # Si las credenciales son válidas, se guarda el usuario en la sesión
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("products.list_products"))

        flash(error)

    return render_template("fragments/login.html")


@bp.before_app_request
def load_logged_in_user():
    """
    Carga los datos del usuario logueado en `g.user` antes de cada petición.

    Esta función se ejecuta antes de cada request. Comprueba si existe un
    `user_id` en la sesión y, de ser así, obtiene los datos del usuario
    de la base de datos y los almacena en `g.user` para que estén
    disponibles durante el resto de la petición.
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/logout")
def logout():
    """Cierra la sesión del usuario y redirige a la página de login."""
    session.clear()
    return redirect(url_for("auth.login"))


def login_required(view):
    """
    Decorador para proteger vistas que requieren autenticación.

    Si el usuario no está logueado (`g.user` es None), lo redirige a la
    página de login. De lo contrario, permite el acceso a la vista.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


# Ejemplo de una ruta segura que utiliza el aspecto @secure
@bp.route("/admin_only")
@login_required
@secure(roles=["admin"])
def admin_only():
    """
    Una ruta de ejemplo protegida que solo es accesible para administradores.

    Demuestra el uso combinado de `@login_required` y el aspecto `@secure`.
    """
    return "¡Bienvenido, Administrador!"
