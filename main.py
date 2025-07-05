#py -m venv venv
#cd ./venv
#cd ./Scripts
#.\activate
#cd ..
#cd ..
#pip install fastapi uvicorn
#uvicorn main:app --reload --port 8001
from fastapi import FastAPI, Request
import requests
import pandas as pd
from meli import actualizar_precio, actualizar_stock  # Asegúrate de tener este archivo
import os
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

@app.get("/obtener-token")
def obtener_token(code: str):
    client_id = "2659704398649482"
    client_secret = os.getenv("CLIENT_SECRET")
    redirect_uri = "https://easyadmin-0437.onrender.com/callback" 
    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)

    return {
        "status": response.status_code,
        "token": response.json()
    }


@app.get("/")
def read_root():
    return {"message": "API para actualizar precios y stock desde Excel"}

# ✅ Ver detalles de la app en MELI
@app.get("/ver-app")
def ver_datos_app():
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or 'TU_ACCESS_TOKEN_AQUI'
    APP_ID = "2659704398649482"
    url = f"https://api.mercadolibre.com/applications/{APP_ID}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(url, headers=headers)
    return {
        "status": response.status_code,
        "data": response.json()
    }

# ✅ Actualización desde archivo Excel
@app.post("/actualizar-desde-excel")
def actualizar_desde_excel():
    df = pd.read_excel("data/productos.xlsx", sheet_name=0)

    resultados = []
    for _, row in df.iterrows():
        item_id = row["item_id"]
        precio = row["precio"]
        stock = row["stock"]

        r1 = actualizar_precio(item_id, precio)
        r2 = actualizar_stock(item_id, stock)

        resultados.append({
            "item_id": item_id,
            "precio_resultado": r1,
            "stock_resultado": r2
        })

    return resultados

# ✅ Callback de autorización
@app.get("/callback")
def recibir_code(request: Request):
    code = request.query_params.get("code")
    print("📥 Authorization Code recibido:", code)
    return {"authorization_code": code}

# ✅ Notificaciones desde MELI
@app.post("/notificaciones")
async def recibir_notificacion(request: Request):
    body = await request.json()
    print("📬 Notificación recibida:", body)
    return {"status": "ok"}



@app.get("/refresh-token")
def refresh_token():
    client_id = "2659704398649482"
    client_secret = os.getenv("CLIENT_SECRET")
    refresh_token = "TG-6869954d228c0b00017d4db0-816130048"

    url = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    
    return {
        "status": response.status_code,
        "data": response.json()
    }

