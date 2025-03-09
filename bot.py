from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
import logging

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token from BotFather
TOKEN = '7755315464:AAHGWg9y_GazGvWjjA2rqsEIgK0wz_Yf8q8'

def get_recent_data(symbol, limit):
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT close FROM prices WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?', (symbol, limit))
    data = [row[0] for row in cursor.fetchall()]
    conn.close()
    return data[::-1]

def calculate_sma(data, period):
    if len(data) < period:
        return None
    return sum(data[-period:]) / period

def calculate_ema(data, period):
    if len(data) < period:
        return None
    sma = calculate_sma(data[:period], period)
    multiplier = 2 / (period + 1)
    ema = sma
    for price in data[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def get_user_symbols(user_id):
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT symbol FROM user_symbols WHERE user_id = ?', (user_id,))
    symbols = [row[0] for row in cursor.fetchall()]
    conn.close()
    return symbols

def add_user_symbol(user_id, symbol):
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO user_symbols (user_id, symbol) VALUES (?, ?)', (user_id, symbol.upper()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Symbol already exists for the user
    conn.close()

def remove_user_symbol(user_id, symbol):
    conn = sqlite3.connect('market_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_symbols WHERE user_id = ? AND symbol = ?', (user_id, symbol.upper()))
    conn.commit()
    conn.close()

# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your trading assistant bot. Use /add_symbol <symbol> to add symbols to your report.')

def add_symbol(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Please provide a symbol (e.g., /add_symbol AAPL)')
        return
    symbol = context.args[0].upper()
    user_id = update.message.from_user.id
    add_user_symbol(user_id, symbol)
    update.message.reply_text(f'Added {symbol} to your report.')

def remove_symbol(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Please provide a symbol (e.g., /remove_symbol AAPL)')
        return
    symbol = context.args[0].upper()
    user_id = update.message.from_user.id
    remove_user_symbol(user_id, symbol)
    update.message.reply_text(f'Removed {symbol} from your report.')

def report(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.message.from_user.id
        symbols = get_user_symbols(user_id)
        if not symbols:
            update.message.reply_text('You have no symbols in your report. Use /add_symbol to add some.')
            return
        message = "Daily Report:\n"
        for symbol in symbols:
            data = get_recent_data(symbol, 10)
            if not data:
                message += f"{symbol}: Not enough data yet!\n"
                continue
            current_price = data[-1]
            sma = calculate_sma(data, 5)
            ema = calculate_ema(data, 5)
            
            # Add null checks for SMA and EMA
            sma_text = f"${sma:.2f}" if sma is not None else "Insufficient data"
            ema_text = f"${ema:.2f}" if ema is not None else "Insufficient data"
            
            message += f"{symbol}:\nCurrent Price: ${current_price:.2f}\nSMA (5): {sma_text}\nEMA (5): {ema_text}\n\n"
        update.message.reply_text(message)
    except Exception as e:
        update.message.reply_text(f"An error occurred while generating your report: {str(e)}")

def price(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text('Please provide an asset (e.g., /price SPY)')
        return
    symbol = context.args[0].upper()
    data = get_recent_data(symbol, 1)
    if not data:
        update.message.reply_text(f'No data for {symbol} yet!')
        return
    update.message.reply_text(f'Current price of {symbol}: ${data[0]:.2f}')

# Main function to set up and run the bot
def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_symbol", add_symbol))
    dispatcher.add_handler(CommandHandler("remove_symbol", remove_symbol))
    dispatcher.add_handler(CommandHandler("report", report))
    dispatcher.add_handler(CommandHandler("price", price))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()