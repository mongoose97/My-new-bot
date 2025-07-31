import json
from flask import Flask, request
import requests
import os
import time

app = Flask(__name__)

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

def place_order(symbol, side, quantity):
    url = "https://api.binance.com/api/v3/order/test"  # Use '/order' to place real orders
    headers = {
        "X-MBX-APIKEY": BINANCE_API_KEY
    }
    payload = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": int(time.time() * 1000)
    }
    response = requests.post(url, headers=headers, params=payload)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data["passphrase"] != os.getenv("WEBHOOK_PASSPHRASE"):
        return {"code": "error", "message": "Invalid passphrase"}, 403

    symbol = data["ticker"]
    action = data["strategy"]["order_action"]
    quantity = float(os.getenv("TRADE_AMOUNT", "10"))

    response = place_order(symbol=symbol, side=action, quantity=quantity)
    return {"code": "success", "response": response}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)