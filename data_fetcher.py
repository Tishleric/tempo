import requests
import sqlite3
import time

API_KEY = 'MSISMONLFSNDPWWG'

# Read symbols from symbols.txt
def get_symbols():
    with open('symbols.txt', 'r') as file:
        symbols = [line.strip() for line in file.readlines()]
    return symbols

# Fetch data from Alpha Vantage for a given symbol
def fetch_market_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={API_KEY}'
    response = requests.get(url).json()
    time_series = response.get('Time Series (1min)', {})
    if not time_series:
        print(f"No data for {symbol}")
        return None
    latest_time = max(time_series.keys())
    latest_data = time_series[latest_time]
    return {
        'timestamp': latest_time,
        'close': float(latest_data['4. close']),
        'symbol': symbol
    }

# Set up SQLite database
def setup_database():
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            close REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_symbols (
            user_id INTEGER,
            symbol TEXT,
            PRIMARY KEY (user_id, symbol)
        )
    ''')
    conn.commit()
    conn.close()

# Insert data into database
def save_data(data):
    if data is None:
        return
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO prices (timestamp, symbol, close) VALUES (?, ?, ?)',
                   (data['timestamp'], data['symbol'], data['close']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    symbols = get_symbols()
    for symbol in symbols:
        data = fetch_market_data(symbol)
        save_data(data)
        if data:
            print(f"Saved: {data}")
        time.sleep(1)  # Avoid hitting API rate limits 