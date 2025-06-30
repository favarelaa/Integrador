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
from meli import actualizar_precio, actualizar_stock


app = FastAPI()

@app.get('/')
def read_root():
    return {"message": 'API para actualizar precios y stock desde Excel'}


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

@app.get("/callback")
def recibir_code(request: Request):
    code = request.query_params.get("code")
    return {"authorization_code": code}

@app.post("/notificaciones")
async def recibir_notificacion(request: Request):
    body = await request.json()
    print("📬 Notificación recibida:", body)
    return {"status": "ok"}

