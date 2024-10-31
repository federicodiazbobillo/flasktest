from flask import Blueprint, render_template

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route("/")
def index():
    from app.models.meli_access import MeliAccess  # Importación retrasada para evitar importación circular
    token_status = "Token activo" if MeliAccess.is_token_active() else "Token inactivo"
    return render_template('home.html', token_status=token_status)
