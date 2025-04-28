import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import requests
import time
import threading

# Create Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Cryptos to track
TRACKED_SYMBOLS = ["BTC", "ETH", "SOL", "DOGE", "LTC", "XRP", "ADA", "SHIB"]

# Mapping for Coinbase API
COINBASE_MAPPING = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "DOGE": "DOGE-USD",
    "LTC": "LTC-USD",
    "XRP": "XRP-USD",
    "ADA": "ADA-USD",
    "SHIB": "SHIB-USD",
}

live_prices = {}

def fetch_live_prices():
    """Fetch live prices from Coinbase API."""
    global live_prices
    updated_prices = {}

    for symbol, pair in COINBASE_MAPPING.items():
        try:
            url = f"https://api.coinbase.com/v2/prices/{pair}/spot"
            response = requests.get(url)
            if response.status_code == 200:
                price = float(response.json()['data']['amount'])
                updated_prices[symbol] = price
            else:
                print(f"Error fetching {symbol}: {response.status_code}")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    if updated_prices:
        live_prices.update(updated_prices)
        socketio.emit('update_prices', live_prices)

def background_task():
    """Background task fetching live prices every 5 seconds."""
    while True:
        fetch_live_prices()
        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

# Start background fetch
threading.Thread(target=background_task, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
