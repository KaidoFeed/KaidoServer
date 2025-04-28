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

# Replace with your KaidoServer endpoint
KAIDO_SERVER_URL = "https://kaidoserver-25i1.onrender.com"

# Crypto symbols you want to track
TRACKED_SYMBOLS = ["DOGE", "SOL", "ETH", "BTC"]

live_prices = {}

def fetch_live_prices():
    """Fetch live prices from KaidoServer and update live_prices dict."""
    global live_prices
    try:
        response = requests.get(KAIDO_SERVER_URL)
        if response.status_code == 200:
            data = response.json()
            updated_prices = {}
            for symbol in TRACKED_SYMBOLS:
                if symbol in data:
                    updated_prices[symbol] = data[symbol]
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
