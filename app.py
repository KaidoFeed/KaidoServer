import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import requests
import time
import threading

# Create the Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Coinbase API endpoint
COINBASE_URL = "https://api.coinbase.com/v2/prices/{}-USD/spot"

# Crypto symbols you want to track
TRACKED_SYMBOLS = ["BTC", "ETH", "SOL", "DOGE", "LTC", "XRP", "ADA", "SHIB"]

live_prices = {}

def fetch_live_prices():
    """Fetch live prices from Coinbase and update live_prices dict."""
    global live_prices
    try:
        updated_prices = {}
        for symbol in TRACKED_SYMBOLS:
            response = requests.get(COINBASE_URL.format(symbol))
            if response.status_code == 200:
                data = response.json()
                price = data["data"]["amount"]
                updated_prices[symbol] = float(price)
        live_prices = updated_prices
        socketio.emit('update_prices', live_prices)
    except Exception as e:
        print(f"Error fetching prices: {e}")

def background_task():
    """Background task to fetch live prices every 5 seconds."""
    while True:
        fetch_live_prices()
        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

# Start background fetcher
threading.Thread(target=background_task, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
