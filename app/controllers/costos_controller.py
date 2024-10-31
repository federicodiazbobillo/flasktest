# app/controllers/costos_controller.py
from flask import Blueprint, render_template

bp = Blueprint('costos', __name__, url_prefix='/costos')

@bp.route('/')
def index():
    return render_template('costos.html')