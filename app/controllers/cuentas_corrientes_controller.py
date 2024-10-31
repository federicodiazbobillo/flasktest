# app/controllers/cuentas_corrientes_controller.py
from flask import Blueprint, render_template

bp = Blueprint('cuentas_corrientes', __name__, url_prefix='/cuentas_corrientes')

@bp.route('/')
def index():
    return render_template('cuentas_corrientes.html')