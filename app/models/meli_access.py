# app/models/meli_access.py
from app import db

class MeliAccess(db.Model):
    __tablename__ = 'meli_access'
    app_id = db.Column(db.BigInteger, primary_key=True)
    secret_key = db.Column(db.String(50), nullable=False)
    refresh_token = db.Column(db.String(50), nullable=False)

    @staticmethod
    def is_token_active():
        # Ejemplo: verifica si el token existe o cumple alguna condición para estar "activo"
        token = MeliAccess.query.first()
        return bool(token and token.refresh_token)
