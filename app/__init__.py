# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Inicializar SQLAlchemy con la app
    db.init_app(app)

    # Registrar blueprints
    from .controllers import (
        home_controller,
        dashboard_controller,
        costos_controller,
        cuentas_corrientes_controller,
        envios_controller,
        ver_guias_controller
    )

    app.register_blueprint(home_controller.bp)
    app.register_blueprint(dashboard_controller.bp)
    app.register_blueprint(costos_controller.bp)
    app.register_blueprint(cuentas_corrientes_controller.bp)
    app.register_blueprint(envios_controller.bp)
    app.register_blueprint(ver_guias_controller.bp)


    return app
