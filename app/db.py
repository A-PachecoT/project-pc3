# -*- coding: utf-8 -*-
"""
Módulo de gestión de la base de datos para la aplicación Flask.

Proporciona funciones para conectar, cerrar e inicializar la base de datos SQLite.
Utiliza el contexto de la aplicación (`g`) para gestionar la conexión,
asegurando que solo se abre una conexión por petición y se cierra al finalizar.
"""
import sqlite3
import click
from flask import current_app, g


def get_db():
    """
    Conecta a la base de datos y la almacena en el contexto de la aplicación.

    Si no existe una conexión `db` en el objeto `g` de Flask, crea una nueva
    conexión a la base de datos SQLite configurada en la aplicación.
    Establece `sqlite3.Row` como `row_factory` para poder acceder a las
    columnas por nombre.

    Returns:
        sqlite3.Connection: El objeto de conexión a la base de datos.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """
    Cierra la conexión a la base de datos si existe en el contexto.

    Esta función está diseñada para ser registrada con `teardown_appcontext`,
    asegurando que la conexión se cierre automáticamente al final de cada petición.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """
    Inicializa la base de datos ejecutando el script del esquema SQL.

    Obtiene una conexión a la base de datos y ejecuta el contenido del
    archivo `schema.sql` para crear la estructura de tablas y datos iniciales.
    """
    db = get_db()
    # Ejecuta el archivo schema.sql para crear las tablas
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """
    Comando de CLI para inicializar la base de datos.

    Limpia los datos existentes y crea las tablas nuevas.
    Se puede ejecutar desde la terminal con `flask init-db`.
    """
    init_db()
    click.echo("Base de datos inicializada.")


def init_app(app):
    """

    Registra las funciones de gestión de la base de datos en la instancia de la aplicación.

    Args:
        app (Flask): La instancia de la aplicación Flask.
    """
    # Registra close_db para que se llame al limpiar el contexto de la aplicación
    app.teardown_appcontext(close_db)
    # Añade el comando init-db a la CLI de Flask
    app.cli.add_command(init_db_command)
