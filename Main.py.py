from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

# Load environment variables (set these in Render)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
WEBHOOK_PASSPHRASE = os.getenv("WEBHOOK_PASSPHRASE")

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    if data['passphrase'] != WEBHOOK_PASSPHRASE:
        return jsonify({"error": "Invalid passphrase"}), 403

    symbol = data['ticker'].upper()
    action = data['action'].lower()

    if action == "buy":
        try:
            usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
            price = float(client.get_symbol_ticker(symbol=symbol)['price'])
            amount_to_spend = usdt_balance * 0.10
            quantity = round(amount_to_spend / price, 6)

            order = client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )

            return jsonify({"message": f"Buy order placed for {quantity} {symbol} at ${price}"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif action == "sell":
        try:
            asset = symbol.replace("USDT", "")
            asset_balance = float(client.get_asset_balance(asset=asset)['free'])

            order = client.order_market_sell(
                symbol=symbol,
                quantity=round(asset_balance, 6)
            )

            return jsonify({"message": f"Sell order placed for {asset_balance} {symbol}"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid action"}), 400

if __name__ == '__main__':
    app.run()
