# -*- coding: utf-8 -*-
"""
Módulo de Programación Orientada a Aspectos (AOP).

Este módulo define un conjunto de decoradores de Python que implementan
incumbencias transversales (cross-cutting concerns) para una aplicación Flask.
Estos decoradores permiten añadir funcionalidades como seguridad, caché, métricas,
auditoría y validación a las rutas de la aplicación de una manera limpia y reutilizable.

Aspectos implementados:
- secure: Control de acceso basado en roles.
- cache: Cacheo de respuestas en memoria con TTL.
- metrics: Medición del tiempo de ejecución.
- audit: Registro de acciones de usuario.
- feature_flag: Activación/desactivación de funcionalidades.
- validate_with: Validación de datos de formularios con Pydantic.
"""
import time
import functools
from flask import g, abort, current_app, render_template, request, flash, redirect
from pydantic import ValidationError
from app.db import get_db

# --- Caché en memoria ---
# Un diccionario simple que actúa como caché en memoria para los resultados de las vistas.
# Las claves son generadas a partir del nombre de la vista y sus argumentos.
_cache = {}

# --- Decoradores AOP ---


def secure(roles=None):
    """
    Aspecto de seguridad para controlar el acceso a una vista basado en roles.

    Este decorador es una fábrica que toma una lista de roles permitidos.
    Si el usuario en sesión (`g.user`) no tiene uno de los roles especificados,
    la petición es abortada con un error HTTP 403 (Forbidden). Si no hay
    un usuario en sesión, se aborta con 401 (Unauthorized).

    Uso:
        @secure(roles=['admin', 'editor'])
        def mi_vista_protegida():
            return "Contenido secreto"
    """
    if roles is None:
        roles = []

    def decorator(view):
        """El decorador real que envuelve la vista."""
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            """La función que ejecuta la lógica de seguridad."""
            if g.user is None:
                abort(401)  # No autorizado
            if roles and g.user["role"] not in roles:
                abort(403)  # Prohibido
            print(
                f"SEGURIDAD: Acceso concedido al usuario '{g.user['username']}' con rol '{g.user['role']}'."
            )
            return view(**kwargs)

        return wrapped_view

    return decorator


def cache(ttl=60):
    """
    Aspecto de caché para almacenar en memoria el resultado de una vista.

    Este decorador guarda el resultado de una función de vista en un caché
    en memoria durante un tiempo determinado (TTL, Time To Live, en segundos).
    En peticiones subsiguientes, si el caché no ha expirado, devuelve el
    resultado guardado en lugar de ejecutar la vista de nuevo.

    Args:
        ttl (int): El tiempo en segundos que el resultado debe permanecer en caché.

    Uso:
        @cache(ttl=300) # Cachea por 5 minutos
        def vista_costosa():
            # ...cálculos pesados...
            return "resultado"
    """

    def decorator(view):
        """El decorador real que envuelve la vista."""
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            """La lógica de cacheo que envuelve la llamada a la vista."""
            # Crea una clave única basada en el nombre de la vista y sus argumentos
            key = f"{view.__name__}:{kwargs}"
            now = time.time()
            if key in _cache:
                result, timestamp = _cache[key]
                # Verifica si el caché ha expirado
                if now - timestamp < ttl:
                    print(f"CACHE: Hit para la clave '{key}'.")
                    return result
                else:
                    print(f"CACHE: Clave expirada '{key}'.")

            print(f"CACHE: Miss para la clave '{key}'. Cacheando resultado.")
            result = view(**kwargs)
            _cache[key] = (result, now)
            return result

        return wrapped_view

    return decorator


def metrics(view):
    """
    Aspecto de métricas para medir el tiempo de ejecución de una vista.

    Este decorador simple mide el tiempo que tarda una vista en ejecutarse
    desde que se llama hasta que retorna un resultado. Imprime la duración
    en la consola. Es útil para identificar cuellos de botella.

    Uso:
        @metrics
        def mi_vista():
            # ...
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """La función que mide el tiempo."""
        start_time = time.time()

        try:
            result = view(**kwargs)
            return result
        finally:
            # Se ejecuta siempre, incluso si la vista lanza una excepción
            end_time = time.time()
            duration = end_time - start_time
            print(f"METRICAS para '{view.__name__}':")
            print(f"  - Tiempo de ejecución: {duration:.4f}s")

    return wrapped_view


def audit(action=""):
    """
    Aspecto de auditoría para registrar la ejecución de una acción.

    Este decorador registra un mensaje en la consola indicando qué usuario
    realizó una acción determinada. La acción se pasa como argumento al decorador.

    Args:
        action (str): Una descripción de la acción que se está realizando.

    Uso:
        @audit(action='ver_detalles_pedido')
        def ver_pedido(id):
            # ...
    """

    def decorator(view):
        """El decorador real que envuelve la vista."""
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            """La lógica que registra el mensaje de auditoría."""
            user = g.user["username"] if g.user else "Anónimo"
            print(
                f"AUDITORIA: El usuario '{user}' realizó la acción '{action}' con argumentos {kwargs}."
            )
            return view(**kwargs)

        return wrapped_view

    return decorator


def feature_flag(name=""):
    """
    Aspecto de Feature Flag para controlar el acceso a una funcionalidad.

    Verifica en la base de datos si una bandera de funcionalidad (`feature_flag`)
    está activa. Si no lo está, deniega el acceso y muestra un mensaje.
    Esto permite activar o desactivar partes de la aplicación dinámicamente.

    Args:
        name (str): El nombre de la `feature_flag` a verificar en la BBDD.

    Uso:
        @feature_flag(name='editor_promociones')
        def gestionar_promociones():
            # ...
    """

    def decorator(view):
        """El decorador real que envuelve la vista."""
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            """La lógica que consulta la BBDD y controla el acceso."""
            db = get_db()
            flag = db.execute(
                "SELECT is_active FROM feature_flag WHERE name = ?", (name,)
            ).fetchone()

            if flag and flag["is_active"]:
                print(f"FEATURE_FLAG: '{name}' está ON. Acceso concedido.")
                return view(**kwargs)
            else:
                print(f"FEATURE_FLAG: '{name}' está OFF. Acceso denegado.")
                # Podría renderizar una plantilla diferente o abortar
                return "<h3>Esta funcionalidad está desactivada actualmente.</h3>"

        return wrapped_view

    return decorator


def validate_with(schema, methods=("POST",)):
    """
    Aspecto de validación de datos de un formulario usando un esquema de Pydantic.

    Intercepta una petición (por defecto, solo POST) y valida los datos del
    formulario (`request.form`) contra el esquema de Pydantic proporcionado.
    Si la validación es exitosa, los datos validados y casteados se adjuntan
    al objeto `g` de Flask (`g.validated_data`).
    Si la validación falla, muestra mensajes de error al usuario y redirige
    a la misma URL para que pueda corregir los datos.

    Args:
        schema: La clase del modelo Pydantic a usar para la validación.
        methods (tuple): Una tupla de métodos HTTP en los que se debe
                         activar la validación.

    Uso:
        @validate_with(schema=MiEsquemaPydantic)
        def crear_recurso():
            if request.method == 'POST':
                # Si llega aquí, g.validated_data existe y es válido
                datos = g.validated_data
                # ...
    """

    def decorator(view):
        """El decorador real que envuelve la vista."""
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            """La lógica que realiza la validación."""
            if request.method in methods:
                try:
                    data_to_validate = request.form.to_dict()
                    # `model_validate` parsea y valida el diccionario
                    g.validated_data = schema.model_validate(data_to_validate)
                    print(f"VALIDACION: Los datos para '{view.__name__}' son válidos.")
                except ValidationError as e:
                    # Si Pydantic levanta un error, lo manejamos aquí
                    print(f"ERROR_VALIDACION: {e.errors()}")
                    for error in e.errors():
                        field = " ".join(str(loc) for loc in error["loc"])
                        msg = error["msg"]
                        flash(f"Error de validación para '{field}': {msg}")
                    # Redirige de vuelta al formulario para mostrar los errores
                    return redirect(request.url)
            return view(**kwargs)

        return wrapped_view

    return decorator
