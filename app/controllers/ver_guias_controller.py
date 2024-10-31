from flask import Blueprint, render_template

bp = Blueprint('ver_guias', __name__, url_prefix='/ver_guias')

@bp.route('/')
def index():
    return render_template('ver_guias.html')