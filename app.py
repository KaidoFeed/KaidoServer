from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# --- Fetch crypto prices
def fetch_crypto_price(symbol):
    url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['data']['amount']
    else:
        return None

# --- Flask route
@app.route('/')
def index():
    return render_template('index.html')

# --- Background task
def background_price_fetcher():
    symbols = ['BTC', 'ETH', 'LTC']  # Add more if you want
    while True:
        prices = {}
        for symbol in symbols:
            price = fetch_crypto_price(symbol)
            if price:
                prices[symbol] = price
        socketio.emit('crypto_prices', prices)
        eventlet.sleep(10)  # Fetch every 10 seconds

# --- Start background task
@socketio.on('connect')
def on_connect():
    print('Client connected!')
    socketio.start_background_task(background_price_fetcher)

# --- Run app
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=10000)
