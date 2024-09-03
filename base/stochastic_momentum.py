import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import vectorbt as vbt
from .models import BotOperation, User , UserSetting, TradeSymbols
from django.contrib.auth import get_user_model

# Configure logging
class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            user = get_user_model().objects.get(username=record.username)
            log_entry = BotOperation(
                user=user,
                operation_type=record.levelname,
                details=record.getMessage(),
                timestamp=datetime.fromtimestamp(record.created)
            )
            log_entry.save()
        except User.DoesNotExist:
            pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(DatabaseLogHandler())

class StochasticMomentumStrategy:
    def __init__(self, user, API_KEY, API_SECRET):
        self.client = StockHistoricalDataClient(API_KEY, API_SECRET)
        self.volume_threshold = 1000000
        self.beta_threshold = 1.5
        self.bid_ask_spread_threshold = 0.05
        self.user = user  # Ensure user is passed and stored
        self.filtered_stocks = self.screen_stocks()

    def screen_stocks(self):
        def get_symbols():
            # Fetch symbols from the database
            symbols = list(TradeSymbols.objects.values_list('symbol', flat=True))
            try:
                # Get the user's settings
                user_setting = UserSetting.objects.get(user=self.user)

                # Check if user has set specific symbols
                user_symbols = user_setting.get_filter_symbol()
                if user_symbols:
                    logger.info(f"Using user-selected symbols: {user_symbols}", extra={'username': self.user.username})
                    return user_symbols

                # Check if user has set a sector filter
                user_sector = user_setting.filter_sector
                if user_sector:
                    logger.info(f"Using symbols from user-selected sector: {user_sector}", extra={'username': self.user.username})
                    symbols_in_sector = list(TradeSymbols.objects.filter(sector=user_sector).values_list('symbol', flat=True))
                    return symbols_in_sector

            except UserSetting.DoesNotExist:
                pass

            # If no user filters, return default symbols
            return symbols

        def fetch_stock_data(symbols):
            data = {}
            for symbol in symbols:
                stock = yf.Ticker(symbol)
                try:
                    info = stock.info
                    bid = info.get('bid')
                    ask = info.get('ask')
                    bid_ask_spread = (ask - bid) if (bid is not None and ask is not None) else None
                    data[symbol] = {
                        'average_volume': info.get('averageVolume'),
                        'beta': info.get('beta'),
                        'bid': bid,
                        'ask': ask,
                        'bid_ask_spread': bid_ask_spread
                    }
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}", extra={'username': self.user.username})
                    continue
            return pd.DataFrame.from_dict(data, orient='index')
        
         # Function to split list into chunks
        def split_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]

        symbol_chunks = list(split_list(get_symbols(), 100))
        filtered_stocks = pd.DataFrame()

        for chunk in symbol_chunks:
            logger.info(f"Processing chunk: {chunk[:5]}...", extra={'username': self.user.username})
            chunk_data = fetch_stock_data(chunk)
            criteria = (
                (chunk_data['average_volume'] > self.volume_threshold) &
                (chunk_data['beta'] > self.beta_threshold) &
                (chunk_data['bid_ask_spread'] < self.bid_ask_spread_threshold)
            )
            filtered_chunk = chunk_data[criteria]
            filtered_stocks = pd.concat([filtered_stocks, filtered_chunk])

        # Log the stocks that passed the first screening stage
        for stock in filtered_stocks.index:
            BotOperation.objects.create(
                user=self.user,
                stock_symbol=stock,
                stage="First Screen",  # Stage: First Screen
                status="Passed",  # Status: Passed the screening
                reason="Passed initial screening",
                timestamp=datetime.now()
            )

        return filtered_stocks.index.tolist()

    def check_signals(self):
        start_date_daily = datetime.now() - timedelta(days=200)
        start_date_weekly = datetime.now() - timedelta(days=200)
        end_date = datetime.now() - timedelta(days=1)

        buy_signals = []
        sell_signals = []

        for stock in self.filtered_stocks:
            logger.info(f"Processing stock: {stock}", extra={'username': self.user.username})

            try:
                bars_daily = self.fetch_daily_data(stock, start_date_daily, end_date)
                bars_weekly = self.fetch_weekly_data(stock, start_date_weekly, end_date)
                buy_signal, sell_signal = self.calculate_signals(stock, bars_daily, bars_weekly)

                if buy_signal:
                    logger.info(f"Buy signal for {stock} on {bars_daily.index[-1]}", extra={'username': self.user.username})
                    buy_signals.append((stock, bars_daily.index[-1]))
                    BotOperation.objects.create(
                        user=self.user,
                        stock_symbol=stock,
                        stage="Indicator",  # Stage: Indicator
                        status="Buy Signal",  # Status: Buy signal generated
                        reason="Stochastic Oscillator buy signal generated",
                        timestamp=datetime.now()
                    )

                if sell_signal:
                    logger.info(f"Sell signal for {stock} on {bars_daily.index[-1]}", extra={'username': self.user.username})
                    sell_signals.append((stock, bars_daily.index[-1]))
                    BotOperation.objects.create(
                        user=self.user,
                        stock_symbol=stock,
                        stage="Indicator",  # Stage: Indicator
                        status="Sell Signal",  # Status: Sell signal generated
                        reason="Stochastic Oscillator sell signal generated",
                        timestamp=datetime.now()
                    )

            except Exception as e:
                logger.error(f"Error processing stock {stock}: {e}", extra={'username': self.user.username})

        return buy_signals, sell_signals
