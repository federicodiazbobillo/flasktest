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

    # Inyectar el estado del token en todas las plantillas
    @app.context_processor
    def inject_token_status():
        # Importar aquí para evitar problemas de importación circular
        from app.models.meli_access import MeliAccess  
        token_status = "Token activo" if MeliAccess.is_token_active() else "Token inactivo"
        return dict(token_status=token_status)

    return app
