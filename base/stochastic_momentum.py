import logging
from datetime import datetime, timedelta
from django.utils import timezone
import time
import pandas as pd
import yfinance as yf
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import vectorbt as vbt
from .models import BotOperation, TradeSymbols

# Subclass logging.Formatter to use UTC
class UTCFormatter(logging.Formatter):
    converter = time.gmtime  # Force UTC for log timestamps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Update the logger to use UTCFormatter
for handler in logger.handlers:
    handler.setFormatter(UTCFormatter('%(asctime)s - %(levelname)s - %(message)s'))


class StochasticMomentumStrategy:
    def __init__(self, user, API_KEY, API_SECRET, filter_symbol=None, filter_sector=None):
        self.client = StockHistoricalDataClient(API_KEY, API_SECRET)
        self.volume_threshold = 1000000
        self.beta_threshold = 1.5
        self.bid_ask_spread_threshold = 0.05
        self.user = user
        self.filter_symbol = filter_symbol if isinstance(filter_symbol, list) else []
        self.filter_sector = filter_sector if isinstance(filter_sector, list) else []
        self.filtered_stocks = self.screen_stocks()

    def screen_stocks(self):
        logger.info(f"Filter symbols: {self.filter_symbol}, Filter sectors: {self.filter_sector}", extra={'username': self.user.username})

        if self.filter_symbol:
            logger.info(f"Using provided symbols: {self.filter_symbol}", extra={'username': self.user.username})
            self.log_user_filtered_stocks(self.filter_symbol, "User Selected Symbols")
            return self.filter_symbol  # Skip additional logging here

        if self.filter_sector:
            logger.info(f"Using symbols from provided sector: {self.filter_sector}", extra={'username': self.user.username})
            symbols_in_sector = list(TradeSymbols.objects.filter(sector=self.filter_sector).values_list('symbol', flat=True))
            if not symbols_in_sector:
                logger.error(f"No symbols found in the sector {self.filter_sector} for user {self.user.id}")
            self.log_user_filtered_stocks(symbols_in_sector, "User Selected Sectors")
            return symbols_in_sector  # Skip additional logging here

        # If no filters are provided, perform the screening
        def get_symbols():
            symbols = list(TradeSymbols.objects.values_list('symbol', flat=True))
            if not symbols:
                logger.error(f"No symbols found in the TradeSymbols table for user {self.user.id}")
            return symbols

        def fetch_stock_data(symbols):
            data = {}
            for symbol in symbols:
                stock = yf.Ticker(symbol)
                try:
                    info = stock.info
                    bid = info.get('bid')
                    ask = info.get('ask')
                    bid_ask_spread = (ask - bid) if (ask is not None and bid is not None) else None
                    if bid is None or ask is None:
                        logger.error(f"Bid or ask price is missing for {symbol}. Skipping this stock.", extra={'username': self.user.username})
                        continue
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
        if not filtered_stocks.empty:
            for stock in filtered_stocks.index:
                BotOperation.objects.create(
                    user=self.user,
                    stock_symbol=stock,
                    stage="First Screen",
                    status="Passed",
                    reason="Passed initial screening",
                    timestamp=timezone.now()
                )
        else:
            # Log if no stocks passed after all chunks have been processed
            logger.info(f"No stocks passed the first screening for user {self.user.id}", extra={'username': self.user.username})
            BotOperation.objects.create(
                user=self.user,
                stock_symbol="None",
                stage="First Screen",
                status="Failed",
                reason="No stocks found suitable for strategy",
                timestamp=timezone.now()
            )

        logger.info("Filtered stocks:", extra={'username': self.user.username})
        logger.info(filtered_stocks.to_string(), extra={'username': self.user.username})

        return filtered_stocks.index.tolist()

    def log_user_filtered_stocks(self, stocks, reason):
        """Logs the stocks chosen by the user with the provided reason."""
        if not stocks:
            logger.error(f"No stocks found for the given filter {reason} for user {self.user.id}")
        for stock in stocks:
            BotOperation.objects.create(
                user=self.user,
                stock_symbol=stock,
                stage="First Screen",
                status="Passed",
                reason=reason,
                timestamp=timezone.now()
            )
        logger.info(f"User-chosen stocks ({reason}): {stocks}", extra={'username': self.user.username})

    def fetch_daily_data(self, stock: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch daily stock data."""
        request_params = StockBarsRequest(
            symbol_or_symbols=stock,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date,
            adjustment='all'
        )
        bars_daily = self.client.get_stock_bars(request_params).df.reset_index(level='symbol', drop=True)
        return bars_daily

    def fetch_weekly_data(self, stock: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch weekly stock data."""
        request_params = StockBarsRequest(
            symbol_or_symbols=stock,
            timeframe=TimeFrame.Week,
            start=start_date,
            end=end_date,
            adjustment='all'
        )
        bars_weekly = self.client.get_stock_bars(request_params).df.reset_index(level='symbol', drop=True)
        return bars_weekly

    def calculate_signals(self, stock: str, bars_daily: pd.DataFrame, bars_weekly: pd.DataFrame) -> tuple[bool, bool]:
        """Calculate buy and sell signals based on Stochastic Oscillator."""
        stoch = vbt.STOCH.run(
            high=bars_weekly['high'], 
            low=bars_weekly['low'], 
            close=bars_weekly['close'],
            k_window=10, 
            d_window=3, 
            d_ewm=False  
        )

        stoch_k = stoch.percent_k
        stoch_d = stoch.percent_d
        
        stoch_buy_signal = (stoch_k > 32) & (stoch_k > stoch_d)
        stoch_buy_signal = stoch_buy_signal.reindex(bars_daily.index, method='ffill').fillna(False).infer_objects(copy=False)
        
        stoch_sell_signal = (stoch_k < 80) & (stoch_k < stoch_d)
        stoch_sell_signal = stoch_sell_signal.reindex(bars_daily.index, method='ffill').fillna(False).infer_objects(copy=False)

        prev_day = bars_daily.index[-1]
        buy_signal = stoch_buy_signal.loc[prev_day]
        sell_signal = stoch_sell_signal.loc[prev_day]

        return buy_signal, sell_signal

    def check_signals(self) -> tuple[list[tuple[str, datetime]], list[tuple[str, datetime]]]:
        """Check buy and sell signals for the filtered stocks."""
        start_date_daily = timezone.now() - timedelta(days=200)
        start_date_weekly = timezone.now() - timedelta(days=200)
        end_date = timezone.now() - timedelta(days=1)

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
                        status="Passed",  
                        reason="Stochastic Oscillator buy signal generated",
                        timestamp=timezone.now()
                    )

                if sell_signal:
                    logger.info(f"Sell signal for {stock} on {bars_daily.index[-1]}", extra={'username': self.user.username})
                    sell_signals.append((stock, bars_daily.index[-1]))
                    BotOperation.objects.create(
                        user=self.user,
                        stock_symbol=stock,
                        stage="Indicator",  # Stage: Indicator
                        status="Passed",  
                        reason="Stochastic Oscillator sell signal generated",
                        timestamp=timezone.now()
                    )

                # Log if no buy or sell signal is generated
                if not buy_signal and not sell_signal:
                    logger.info(f"No signals generated for {stock}", extra={'username': self.user.username})
                    BotOperation.objects.create(
                        user=self.user,
                        stock_symbol=stock,
                        stage="Indicator",
                        status="Failed",  
                        reason="No buy/sell signal generated",
                        timestamp=timezone.now()
                    )

            except Exception as e:
                logger.error(f"Error processing stock {stock}: {e}", extra={'username': self.user.username})

        return buy_signals, sell_signals
