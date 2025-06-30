import os
import requests
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def actualizar_precio(item_id, nuevo_precio):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    body = { "price": nuevo_precio }
    res = requests.put(url, headers=HEADERS, json=body)
    return res.json()

def actualizar_stock(item_id, nuevo_stock):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    body = { "available_quantity": nuevo_stock }
    res = requests.put(url, headers=HEADERS, json=body)
    return res.json()
