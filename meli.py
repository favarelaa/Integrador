import requests
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or "TU_ACCESS_TOKEN"

def actualizar_precio(item_id, precio):
    url = f"https://api.mercadolibre.com/items/{item_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {"price": precio}
    response = requests.put(url, json=payload, headers=headers)
    return response.json()

def actualizar_stock(item_id, stock):
    url = f"https://api.mercadolibre.com/inventory/items/{item_id}/stock"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {"available_quantity": stock}
    response = requests.put(url, json=payload, headers=headers)
    return response.json()
