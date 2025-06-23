# -*- coding: utf-8 -*-
"""
Módulo principal de la aplicación Flask.

Este archivo contiene la fábrica de la aplicación, `create_app`, que se encarga de
configurar y crear la instancia principal de la aplicación Flask.

Funciones:
    create_app: La fábrica de la aplicación.
"""
import os
from flask import Flask, redirect, url_for


def create_app(test_config=None):
    """
    Crea, configura y devuelve una instancia de la aplicación Flask.

    Esta es la función fábrica de la aplicación. Configura la app, inicializa
    la base de datos y registra todos los blueprints de las diferentes
    secciones (auth, products, orders, etc.).

    Args:
        test_config (dict, optional): Un mapeo de configuración para usar
            durante las pruebas, en lugar de la configuración de instancia.
            Defaults to None.

    Returns:
        Flask: La instancia de la aplicación Flask creada y configurada.
    """
    # Crear y configurar la aplicación
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "project.sqlite"),
    )

    if test_config is None:
        # Cargar la configuración de la instancia, si existe, cuando no se está testeando
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Cargar la configuración de prueba si se pasó
        app.config.from_mapping(test_config)

    # Asegurarse de que la carpeta de instancia exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicializar la base de datos
    from . import db

    db.init_app(app)

    # Registrar blueprints de los módulos
    from .auth import routes as auth_routes

    app.register_blueprint(auth_routes.bp)

    from .products import routes as product_routes

    app.register_blueprint(product_routes.bp)

    from .orders import routes as order_routes

    app.register_blueprint(order_routes.bp)

    from .transactions import routes as transaction_routes

    app.register_blueprint(transaction_routes.bp)

    from .promotions import routes as promotion_routes

    app.register_blueprint(promotion_routes.bp)

    # Una ruta raíz simple para redirigir a la página de login
    @app.route("/")
    def index():
        """Ruta raíz que redirige al formulario de login."""
        return redirect(url_for("auth.login"))

    return app
