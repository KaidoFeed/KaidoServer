import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import requests
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)

# List of cryptocurrency symbols to fetch
SYMBOLS = ["BTC", "ETH", "SOL", "DOGE", "LTC", "XRP", "ADA", "SHIB"]

thread = None  # Background thread reference

def fetch_prices():
    """Background thread function to fetch crypto prices and emit via Socket.IO."""
    session = requests.Session()
    while True:
        prices = {}
        for symbol in SYMBOLS:
            try:
                url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
                response = session.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                prices[symbol] = data.get("data", {}).get("amount")
            except Exception as e:
                logging.error(f"Error fetching price for {symbol}: {e}")
                prices[symbol] = "N/A"
        # Emit the prices to all connected clients
        socketio.emit('update_prices', prices)
        # Pause for 5 seconds before the next fetch
        socketio.sleep(5)

@socketio.on('connect')
def handle_connect():
    """Event handler for new client connections."""
    global thread
    if thread is None:
        # Start the background price fetching thread
        thread = socketio.start_background_task(fetch_prices)

@app.route('/')
def index():
    """Serve the index HTML to the client."""
    try:
        # Attempt to render from templates folder
        return render_template('index.html')
    except:
        # Fallback: serve index.html from current directory
        return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    # Determine port and host for running the app (necessary for Render)
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
