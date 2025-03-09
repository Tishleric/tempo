import sqlite3

# Fetch recent data from database
def get_recent_data(symbol, limit):
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT close FROM prices WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?', (symbol, limit))
    data = [row[0] for row in cursor.fetchall()]
    conn.close()
    return data[::-1]  # Reverse to chronological order

# Simple Moving Average
def calculate_sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

# Exponential Moving Average
def calculate_ema(data, period):
    if len(data) < period:
        return None
    sma = calculate_sma(data[:period], period)
    multiplier = 2 / (period + 1)
    ema = sma
    for price in data[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

if __name__ == '__main__':
    data = get_recent_data('SPY', 10)  # Last 10 prices
    if data:
        sma = calculate_sma(data, 5)
        ema = calculate_ema(data, 5)
        print(f"SMA (5): {sma:.2f}")
        print(f"EMA (5): {ema:.2f}") 