#py -m venv venv
#cd ./venv
#cd ./Scripts
#.\activate
#cd ..
#cd ..
#pip install fastapi uvicorn
#uvicorn main:app --reload --port 8001
#https://auth.mercadolibre.com/authorization?response_type=code&client_id=2659704398649482&redirect_uri=https://easyadmin-0437.onrender.com/callback

from fastapi import FastAPI, Request
import requests
import pandas as pd
from meli import actualizar_precio, actualizar_stock  # Asegúrate de tener este archivo
import os
from dotenv import load_dotenv
from fastapi import Query
load_dotenv()


app = FastAPI()

# ✅ Callback de autorización
@app.get("/callback")
def recibir_code(request: Request):
    code = request.query_params.get("code")
    print("📥 Authorization Code recibido:", code)
    return {"authorization_code_XD": code}

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



@app.get("/refresh-token")
def refresh_token():
    client_id = "2659704398649482"
    client_secret = os.getenv("CLIENT_SECRET")
    refresh_token = "TG-6869ef49f538180001c8fe99-816130048"

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


@app.get("/")
def read_root():
    return {"message": "API para actualizar precios y stock desde Excel"}

# ✅ Ver detalles de la app en MELI
@app.get("/ver-app")
def ver_datos_app():
    ACCESS_TOKEN = "APP_USR-2659704398649482-070523-3750f6563d9cb97a06eb3070da98ce9a-816130048"
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



# ✅ Notificaciones desde MELI
@app.post("/notificaciones")
async def recibir_notificacion(request: Request):
    body = await request.json()
    print("📬 Notificación recibida:", body)
    return {"status": "ok"}


@app.get("/mis-productos-simple")
def ver_productos():
    access_token = "APP_USR-2659704398649482-070523-3750f6563d9cb97a06eb3070da98ce9a-816130048"
    user_id = 816130048
    url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    return response.json()




@app.get("/mis-productos")
def ver_productos():
    access_token = "APP_USR-2659704398649482-070523-3750f6563d9cb97a06eb3070da98ce9a-816130048"
    user_id = 816130048

    # Paso 1: Obtener lista de items del vendedor
    url_items = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url_items, headers=headers)
    item_ids = response.json().get("results", [])

    productos = []

    # Paso 2: Obtener detalle de cada item
    for item_id in item_ids:
        url_detalle = f"https://api.mercadolibre.com/items/{item_id}"
        r = requests.get(url_detalle, headers=headers)

        if r.status_code == 200:
            data = r.json()
            producto = {
                "item_id": data.get("id"),
                "sku": data.get("seller_custom_field"),  # Esto es el SKU
                "titulo": data.get("title"),
                "precio": data.get("price"),
                "stock": data.get("available_quantity")
            }
            productos.append(producto)

    return productos

import pandas as pd

from fastapi.responses import StreamingResponse
import pandas as pd
import io
import requests

@app.get("/mis-productos/excel")
def descargar_productos_excel():
    access_token = "APP_USR-2659704398649482-070523-3750f6563d9cb97a06eb3070da98ce9a-816130048"
    user_id = 816130048

    url_items = f"https://api.mercadolibre.com/users/{user_id}/items/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url_items, headers=headers)
    item_ids = response.json().get("results", [])

    productos = []

    for item_id in item_ids:
        url_detalle = f"https://api.mercadolibre.com/items/{item_id}"
        r = requests.get(url_detalle, headers=headers)
        if r.status_code == 200:
            data = r.json()
            productos.append({
                "Item ID": data.get("id"),
                "SKU": data.get("seller_custom_field"),
                "Título": data.get("title"),
                "Precio": data.get("price"),
                "Stock": data.get("available_quantity")
            })

    df = pd.DataFrame(productos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Productos")

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=productos_meli.xlsx"}
    )
