import json
import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
import numpy as np
import os
from telegram import Bot
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def send_telegram_message(bot_token, chat_id, message):
    """Send a message to Telegram."""
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Telegram message sent: {message}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")

def read_stock_codes(json_file_path):
    """Read stock codes and thresholds from a JSON file."""
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        if isinstance(data, list):
            # Set default comparison to 'lt' if not specified
            for stock in data:
                stock['comparison'] = stock.get('comparison', 'lt')
            return data
        elif isinstance(data, dict) and 'stocks' in data:
            return [{'name': ticker, 'threshold_type': None, 'threshold_number': None, 'comparison': 'lt'} for ticker in data['stocks']]
        else:
            logger.error(f"Unexpected JSON structure in {json_file_path}")
            return []
    except FileNotFoundError:
        logger.error(f"JSON file {json_file_path} not found.")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in {json_file_path}.")
        return []
    except Exception as e:
        logger.error(f"Error reading JSON file: {str(e)}")
        return []

def calculate_ema(ticker, period, days_back=0):
    """Calculate EMA for a given stock ticker, optionally for a past day."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="60d")
        if hist.empty:
            logger.warning(f"No historical data for {ticker}")
            return None
        closes = hist['Close']
        ema = closes.ewm(span=period, adjust=False).mean()
        return round(ema[-1 - days_back], 2) if len(ema) > days_back else None
    except Exception as e:
        logger.error(f"Error calculating EMA for {ticker}: {str(e)}")
        return None

def get_previous_day_close(ticker):
    """Get the previous day's closing price."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) < 2:
            logger.warning(f"Insufficient historical data for {ticker}")
            return None
        return round(hist['Close'][-2], 2)  # Previous day's close
    except Exception as e:
        logger.error(f"Error fetching previous day close for {ticker}: {str(e)}")
        return None

def get_current_day_close(ticker):
    """Get the current day's closing price."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if hist.empty:
            logger.warning(f"No historical data for {ticker}")
            return None
        return round(hist['Close'][-1], 2)  # Current day's close
    except Exception as e:
        logger.error(f"Error fetching current day close for {ticker}: {str(e)}")
        return None

def get_ttm_pe_pb_ratio(ticker):
    """Calculate P/E and P/B ratios based on TTM EPS and book value."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('regularMarketPrice', None)
        ttm_eps = info.get('trailingEps', None)
        pe_ratio = info.get('trailingPE', None)
        book_value = info.get('bookValue', None)
        pb_ratio = info.get('priceToBook', None)
        
        if current_price is None or ttm_eps is None or ttm_eps == 0:
            logger.warning(f"Missing price or valid TTM EPS for {ticker}")
            calculated_pe_ratio = None
        else:
            calculated_pe_ratio = current_price / ttm_eps
        
        if current_price is None or book_value is None or book_value == 0:
            logger.warning(f"Missing price or valid book value for {ticker}")
            calculated_pb_ratio = None
        else:
            calculated_pb_ratio = current_price / book_value
        
        return (
            pe_ratio,
            round(calculated_pe_ratio, 2) if calculated_pe_ratio is not None else None,
            pb_ratio,
            round(calculated_pb_ratio, 2) if calculated_pb_ratio is not None else None,
            round(current_price, 2) if current_price is not None else None,
            round(ttm_eps, 2) if ttm_eps is not None else None,
            round(book_value, 2) if book_value is not None else None
        )
    
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        return None, None, None, None, None, None, None

async def calculate_pe_ratios(json_file_path):
    """Calculate TTM P/E, P/B ratios, and EMA, check thresholds, and send alerts."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.warning("Telegram bot token or chat ID not set. Alerts will only be printed.")

    stocks = read_stock_codes(json_file_path)
    if not stocks:
        logger.error("No stock data to process.")
        return

    results = []
    for stock in stocks:
        ticker = stock.get('name')
        threshold_type = stock.get('threshold_type')
        threshold_number = float(stock.get('threshold_number', 0)) if stock.get('threshold_number') is not None else None
        comparison = stock.get('comparison', 'lt')
        
        if not ticker:
            logger.warning(f"Invalid stock data: {stock}")
            continue

        logger.info(f"Processing {ticker}")
        pe_ratio, calculated_pe_ratio, pb_ratio, calculated_pb_ratio, current_price, ttm_eps, book_value = get_ttm_pe_pb_ratio(ticker)
        prev_day_close = get_previous_day_close(ticker)
        current_day_close = get_current_day_close(ticker)
        threshold_ema = None
        prev_day_ema = None

        # Calculate EMA based on threshold_type
        if threshold_type == "EMA" and threshold_number is not None:
            ema_period = int(threshold_number)  # Use threshold_number as EMA period
            threshold_ema = calculate_ema(ticker, ema_period)
            prev_day_ema = calculate_ema(ticker, ema_period, days_back=1)
        else:
            ema_period = 20  # Default for non-EMA thresholds
            threshold_ema = calculate_ema(ticker, ema_period)

        # Check thresholds and generate alerts
        alert_message = None
        if threshold_type == "PE" and calculated_pe_ratio is not None and threshold_number is not None:
            if (comparison == "lt" and calculated_pe_ratio < threshold_number) or \
               (comparison == "gt" and calculated_pe_ratio > threshold_number):
                alert_message = f"ALERT: {ticker} P/E ratio ({calculated_pe_ratio}) is {comparison} threshold ({threshold_number})!"
        elif threshold_type == "PB" and calculated_pb_ratio is not None and threshold_number is not None:
            if (comparison == "lt" and calculated_pb_ratio < threshold_number) or \
               (comparison == "gt" and calculated_pb_ratio > threshold_number):
                alert_message = f"ALERT: {ticker} P/B ratio ({calculated_pb_ratio}) is {comparison} threshold ({threshold_number})!"
        elif threshold_type == "EMA" and threshold_ema is not None:
            if comparison == "gt" and current_price is not None and current_price > threshold_ema:
                alert_message = f"ALERT: {ticker} Current price ({current_price}) is above {int(threshold_number)}-day EMA ({threshold_ema})!"
            elif comparison == "lt" and prev_day_close is not None and prev_day_ema is not None and current_day_close is not None:
                if prev_day_close > current_day_close and prev_day_ema > threshold_ema:
                    alert_message = f"ALERT: {ticker} EMA conditions met: Previous close ({prev_day_close}) > Current close ({current_day_close}), Previous {int(threshold_number)}-day EMA ({prev_day_ema}) > Current {int(threshold_number)}-day EMA ({threshold_ema})!"

        # Send alert to Telegram and print
        if alert_message:
            print(alert_message)
            if bot_token and chat_id:
                await send_telegram_message(bot_token, chat_id, alert_message)

        results.append({
            'ticker': ticker,
            'current_price': current_price if current_price is not None else 'N/A',
            'ttm_eps': ttm_eps if ttm_eps is not None else 'N/A',
            'pe_ratio': pe_ratio if pe_ratio is not None else 'N/A',
            'calculated_pe_ratio': calculated_pe_ratio if calculated_pe_ratio is not None else 'N/A',
            'book_value': book_value if book_value is not None else 'N/A',
            'pb_ratio': pb_ratio if pb_ratio is not None else 'N/A',
            'calculated_pb_ratio': calculated_pb_ratio if calculated_pb_ratio is not None else 'N/A',
            'ema': threshold_ema if threshold_ema is not None else 'N/A',
            'prev_day_close': prev_day_close if prev_day_close is not None else 'N/A',
            'current_day_close': current_day_close if current_day_close is not None else 'N/A',
            'prev_day_ema': prev_day_ema if prev_day_ema is not None else 'N/A',
            'threshold_ema': threshold_ema if threshold_ema is not None else 'N/A',
            'threshold_type': threshold_type if threshold_type is not None else 'N/A',
            'threshold_number': threshold_number if threshold_number is not None else 'N/A',
            'comparison': comparison
        })

    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    output_file = f'pe_pb_ema_ratios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    #df.to_csv(output_file, index=False)
    logger.info(f"Results saved to {output_file}")

    # Print results
    print("\nP/E, P/B, and EMA Results:")
    print(df)

if __name__ == "__main__":
    json_file_path = 'nse_stocks.json'
    asyncio.run(calculate_pe_ratios(json_file_path))
