import requests
from datetime import datetime, timedelta
from app.models.meli_access import MeliAccess
from app import db

def renew_token():
    # Get current access data
    meli_access = MeliAccess.query.first()
    if not meli_access:
        print("No access data found for MercadoLibre API.")
        return

    url = "https://api.mercadolibre.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "client_id": meli_access.app_id,
        "client_secret": meli_access.secret_key,
        "refresh_token": meli_access.refresh_token
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        # Update the token in the database
        new_data = response.json()
        meli_access.refresh_token = new_data["refresh_token"]
        db.session.commit()
        print("Token successfully updated.")
    else:
        print("Failed to update token:", response.status_code, response.text)
