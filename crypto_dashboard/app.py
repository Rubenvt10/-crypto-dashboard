from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

# --- Simulated stock data source ---
sample_stocks = [
    ('AAPL', 'Apple Inc.'), ('GOOGL', 'Alphabet Inc.'), ('AMZN', 'Amazon.com Inc.'),
    ('MSFT', 'Microsoft Corp.'), ('TSLA', 'Tesla Inc.'), ('NVDA', 'NVIDIA Corp.'),
    ('META', 'Meta Platforms Inc.'), ('NFLX', 'Netflix Inc.'), ('DIS', 'Walt Disney Co.'),
    ('INTC', 'Intel Corp.'), ('BABA', 'Alibaba Group'), ('ORCL', 'Oracle Corp.'),
    ('AMD', 'Advanced Micro Devices'), ('ADBE', 'Adobe Inc.'), ('CRM', 'Salesforce Inc.'),
    ('PYPL', 'PayPal Holdings'), ('UBER', 'Uber Technologies'), ('SQ', 'Block Inc.'),
    ('SHOP', 'Shopify Inc.'), ('TWLO', 'Twilio Inc.'), ('PLTR', 'Palantir'),
    ('COIN', 'Coinbase'), ('ROKU', 'Roku Inc.'), ('ZM', 'Zoom Video'),
    ('SPOT', 'Spotify'), ('SNAP', 'Snap Inc.'), ('LYFT', 'Lyft Inc.'),
    ('ETSY', 'Etsy Inc.'), ('NIO', 'NIO Inc.'), ('SOFI', 'SoFi Technologies')
]

def get_stock_data():
    stock_data = []
    for symbol, name in sample_stocks:
        price = round(random.uniform(50, 800), 2)
        change = round(random.uniform(-5, 5), 2)
        stock_data.append({
            'name': name,
            'symbol': symbol,
            'current_price': price,
            'market_cap': round(random.uniform(10, 1000), 2) * 1e9,
            'price_change_percentage_24h': change,
            'description': f"{name} is a major public company traded under {symbol}.",
            'image': f"https://logo.clearbit.com/{symbol.lower()}.com"
        })
    return stock_data

def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1,
        'sparkline': 'false'
    }
    res = requests.get(url, params=params)
    return res.json()

@app.route('/')
def index():
    mode = request.args.get('mode', 'crypto')
    data = get_stock_data() if mode == 'stocks' else get_crypto_data()
    return render_template('index.html', coins=data, mode=mode)

@app.route('/<mode>/<symbol>')
def detail(mode, symbol):
    if mode == 'stocks':
        data = get_stock_data()
        coin = next((item for item in data if item['symbol'].lower() == symbol.lower()), None)
    else:
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}"
        res = requests.get(url)
        if res.status_code != 200:
            return "Not found", 404
        data = res.json()
        coin = {
            'name': data['name'],
            'symbol': data['symbol'],
            'current_price': data['market_data']['current_price']['usd'],
            'market_cap': data['market_data']['market_cap']['usd'],
            'price_change_percentage_24h': data['market_data']['price_change_percentage_24h'],
            'description': data['description']['en'][:500] + '...',
            'image': data['image']['large']
        }
    return render_template('detail.html', coin=coin, mode=mode)

@app.route('/history/<mode>/<symbol>')
def history_data(mode, symbol):
    if mode == 'stocks':
        prices = [round(random.uniform(100, 500), 2) for _ in range(7)]
    else:
        url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
        params = {'vs_currency': 'usd', 'days': 7}
        res = requests.get(url, params=params)
        data = res.json()
        prices = [round(point[1], 2) for point in data['prices']]
    return jsonify({'prices': prices, 'labels': list(range(1, len(prices)+1))})

if __name__ == '__main__':
    app.run(debug=True)
