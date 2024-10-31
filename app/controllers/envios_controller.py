# app/controllers/envios_controller.py
from flask import Blueprint, render_template

bp = Blueprint('envios', __name__, url_prefix='/envios')

@bp.route('/')
def index():
    return render_template('envios.html')