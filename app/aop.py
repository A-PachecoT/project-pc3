import time
import functools
from flask import g, abort, current_app, render_template, request, flash, redirect
from pydantic import ValidationError
from app.db import get_db

# --- In-Memory Cache ---
_cache = {}

# --- AOP Decorators ---


def secure(roles=None):
    """
    Checks if a user has the required role.
    Usage: @secure(roles=['admin'])
    """
    if roles is None:
        roles = []

    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                abort(401)  # Unauthorized
            if roles and g.user["role"] not in roles:
                abort(403)  # Forbidden
            print(
                f"SECURITY: Access granted to user '{g.user['username']}' with role '{g.user['role']}'."
            )
            return view(**kwargs)

        return wrapped_view

    return decorator


def cache(ttl=60):
    """
    Caches the result of a view function for a given TTL (in seconds).
    Usage: @cache(ttl=300)
    """

    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            key = f"{view.__name__}:{kwargs}"
            now = time.time()
            if key in _cache:
                result, timestamp = _cache[key]
                if now - timestamp < ttl:
                    print(f"CACHE: Hit for key '{key}'.")
                    return result
                else:
                    print(f"CACHE: Stale key '{key}'.")

            print(f"CACHE: Miss for key '{key}'. Caching result.")
            result = view(**kwargs)
            _cache[key] = (result, now)
            return result

        return wrapped_view

    return decorator


def metrics(view):
    """
    Measures execution time and call count for a view.
    Usage: @metrics
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        start_time = time.time()

        try:
            result = view(**kwargs)
            return result
        finally:
            end_time = time.time()
            duration = end_time - start_time
            print(f"METRICS for '{view.__name__}':")
            print(f"  - Execution Time: {duration:.4f}s")

    return wrapped_view


def audit(action=""):
    """
    Logs an audit trail for the decorated action.
    Usage: @audit(action='view_order_details')
    """

    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            user = g.user["username"] if g.user else "Anonymous"
            print(
                f"AUDIT: User '{user}' performed action '{action}' with args {kwargs}."
            )
            return view(**kwargs)

        return wrapped_view

    return decorator


def feature_flag(name=""):
    """
    Controls access to a feature based on a flag in the database.
    Usage: @feature_flag('new_feature')
    """

    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            db = get_db()
            flag = db.execute(
                "SELECT is_active FROM feature_flag WHERE name = ?", (name,)
            ).fetchone()

            if flag and flag["is_active"]:
                print(f"FEATURE_FLAG: '{name}' is ON. Access granted.")
                return view(**kwargs)
            else:
                print(f"FEATURE_FLAG: '{name}' is OFF. Access denied.")
                # You could render a different template or abort
                return "<h3>Esta funcionalidad está desactivada actualmente.</h3>"

        return wrapped_view

    return decorator


def validate_with(schema, methods=("POST",)):
    """
    Decorator to validate request form data using a Pydantic schema.
    It attaches the validated data to `g.validated_data`.
    """

    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if request.method in methods:
                try:
                    data_to_validate = request.form.to_dict()
                    g.validated_data = schema.model_validate(data_to_validate)
                    print(f"VALIDATION: Request data for '{view.__name__}' is valid.")
                except ValidationError as e:
                    print(f"VALIDATION_ERROR: {e.errors()}")
                    for error in e.errors():
                        field = " ".join(str(loc) for loc in error["loc"])
                        msg = error["msg"]
                        flash(f"Error de validación para '{field}': {msg}")
                    return redirect(request.url)
            return view(**kwargs)

        return wrapped_view

    return decorator
