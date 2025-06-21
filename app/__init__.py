import os
from flask import Flask, redirect, url_for


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "project.sqlite"),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize the database
    from . import db

    db.init_app(app)

    # Register blueprints
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

    # A simple root route to redirect to login
    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app
