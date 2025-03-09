from bot import get_recent_data, price
import sqlite3

def test_get_data_for_all_symbols():
    symbols = ['SPY', 'AAPL', 'GOOGL']
    print("Testing access to market data for all symbols:")
    
    # Check database
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, COUNT(*) FROM prices GROUP BY symbol")
    counts = cursor.fetchall()
    print("\nSymbol counts in database:")
    for symbol, count in counts:
        print(f"{symbol}: {count} records")
    conn.close()
    
    # Test get_recent_data function
    print("\nTesting get_recent_data function:")
    for symbol in symbols:
        data = get_recent_data(symbol, 1)
        if data:
            print(f"{symbol} latest price: ${data[0]:.2f}")
        else:
            print(f"No data found for {symbol}")

if __name__ == "__main__":
    test_get_data_for_all_symbols() 