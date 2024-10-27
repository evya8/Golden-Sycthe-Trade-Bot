import logging
from datetime import datetime, timedelta
from django.utils import timezone
import time
import pandas as pd
import yfinance as yf
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
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
        self.trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
        self.volume_threshold = 1000000
        self.beta_threshold = 1.5
        self.bid_ask_spread_threshold = 0.05
        self.user = user
        self.user_id = user.id
        self.filter_symbol = filter_symbol if isinstance(filter_symbol, list) else []
        self.filter_sector = filter_sector if isinstance(filter_sector, list) else []
        self.open_positions = self.get_open_positions()  # Fetch open positions during initialization

        # Ensure all filtering options go through to indicator check
        self.filtered_stocks = self.screen_stocks()
        self.check_signals()  # Call to check signals with filtered stocks

    def get_open_positions(self):
        """Fetches all open positions from Alpaca."""
        try:
            positions = self.trading_client.get_all_positions()
            open_position_symbols = [position.symbol for position in positions]
            logger.info(f"Open positions: {open_position_symbols}")
            return open_position_symbols
        except Exception as e:
            logger.error(f"Error fetching open positions: {e}")
            return []

    def screen_stocks(self):
        """Filter stocks based on user-provided symbols, sectors, or all available stocks."""
        filtered_stocks = pd.DataFrame()

        # Case 1: User provided specific symbols
        if self.filter_symbol:
            logger.info(f"Using provided symbols: {self.filter_symbol}")
            self.log_user_filtered_stocks(self.filter_symbol, "Selected Symbols")
            # Skip screening, go directly to the indicator check
            return self.filter_symbol

        # Case 2: User provided sectors
        elif self.filter_sector:
            logger.info(f"Using symbols from provided sector: {self.filter_sector}")
            symbols_in_sector = list(TradeSymbols.objects.filter(sector__in=self.filter_sector).values_list('symbol', flat=True))
            if symbols_in_sector:
                logger.info(f"Screening symbols from sectors: {self.filter_sector}")
                symbols_to_screen = symbols_in_sector
            else:
                logger.error(f"No symbols found in the selected sectors {self.filter_sector} for user {self.user_id}")
                symbols_to_screen = []

        # Case 3: No user filters, use all symbols
        else:
            symbols_to_screen = self.get_all_symbols()

        # Fetch and filter data for symbols to screen
        filtered_stocks = self.fetch_and_filter_stock_data(symbols_to_screen)

        # Log results based on filtering outcome for sectors or no filters
        if not filtered_stocks.empty:
            # Log only the stocks that passed the screening
            for stock in filtered_stocks.index:
                BotOperation.objects.create(
                    user=self.user,
                    stock_symbol=stock,
                    stage="First Screen",
                    status="Passed",
                    reason="Passed Initial Screening",
                    timestamp=timezone.now()
                )
        else:
            # If no stocks passed the screening, log a single failure entry
            if self.filter_sector:
                logger.info(f"No stocks from selected sectors passed the first screening for user {self.user_id}")
                BotOperation.objects.create(
                    user=self.user,
                    stock_symbol="N/A",
                    stage="First Screen",
                    status="Failed",
                    reason="No Stocks from Selected Sectors Passed Screening",
                    timestamp=timezone.now()
                )
            else:
                logger.info(f"No stocks passed the first screening for user {self.user_id}")
                BotOperation.objects.create(
                    user=self.user,
                    stock_symbol="N/A",
                    stage="First Screen",
                    status="Failed",
                    reason="No Stocks Found Suitable For Strategy",
                    timestamp=timezone.now()
                )

        logger.info("Filtered stocks:")
        logger.info(filtered_stocks.to_string())

        return filtered_stocks.index.tolist()


    def get_all_symbols(self):
        """Fetch all available symbols from the TradeSymbols table."""
        all_symbols = list(TradeSymbols.objects.values_list('symbol', flat=True))
        if not all_symbols:
            logger.info(f"No symbols found in the TradeSymbols table for user {self.user_id}")
        return all_symbols

    def fetch_and_filter_stock_data(self, symbols):
        """Fetch stock data and filter based on criteria."""
        symbol_chunks = list(self.split_list(symbols, 100))
        filtered_stocks = pd.DataFrame()

        for chunk in symbol_chunks:
            logger.info(f"Processing chunk: {chunk[:5]}...")
            chunk_data = self.fetch_stock_data(chunk)
            criteria = (
                (chunk_data['average_volume'] > self.volume_threshold) &
                (chunk_data['beta'] > self.beta_threshold) &
                (chunk_data['bid_ask_spread'] < self.bid_ask_spread_threshold)
            )
            filtered_chunk = chunk_data[criteria]
            filtered_stocks = pd.concat([filtered_stocks, filtered_chunk])

        return filtered_stocks

    def fetch_stock_data(self, symbols, retries=3):
        """Fetch stock data using yfinance."""
        data = {}
        for symbol in symbols:
            for attempt in range(retries):
                stock = yf.Ticker(symbol)
                try:
                    info = stock.info
                    bid = info.get('bid')
                    ask = info.get('ask')
                    bid_ask_spread = (ask - bid) if (ask is not None and bid is not None) else None
                    if bid is None or ask is None:
                        if attempt < retries - 1:
                            logger.warning(f"Retrying {symbol} ({attempt+1}/{retries})")
                            time.sleep(3)
                            continue
                        logger.error(f"Bid or ask price is missing for {symbol}. Skipping this stock.")
                        break
                    data[symbol] = {
                        'average_volume': info.get('averageVolume'),
                        'beta': info.get('beta'),
                        'bid': bid,
                        'ask': ask,
                        'bid_ask_spread': bid_ask_spread
                    }
                    time.sleep(2)
                    break
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    break
        return pd.DataFrame.from_dict(data, orient='index')

    def split_list(self, lst, chunk_size):
        """Split a list into chunks of a specified size."""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    def log_user_filtered_stocks(self, stocks, reason):
        """Logs the stocks chosen by the user with the provided reason."""
        if not stocks:
            logger.error(f"No stocks found for the given filter {reason} for user {self.user_id}")
        for stock in stocks:
            BotOperation.objects.create(
                user=self.user,
                stock_symbol=stock,
                stage="First Screen",
                status="Passed",
                reason=reason,
                timestamp=timezone.now()
            )
        logger.info(f"User-chosen stocks ({reason}): {stocks}")
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
        time.sleep(1)
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
        time.sleep(1)
        return bars_weekly

    def calculate_signals(self, stock: str, bars_daily: pd.DataFrame, bars_weekly: pd.DataFrame) -> tuple[bool, bool]:
        """
        Calculate buy and sell signals based on Stochastic Oscillator.
        Buy signal: %K above 32 and %K above %D.
        Sell signal: %K below 80 and %K below %D.
        """
        try:
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
            stoch_buy_signal = stoch_buy_signal.reindex(bars_daily.index, method='ffill').fillna(False)

            stoch_sell_signal = (stoch_k < 80) & (stoch_k < stoch_d)
            stoch_sell_signal = stoch_sell_signal.reindex(bars_daily.index, method='ffill').fillna(False)

            prev_day = bars_daily.index[-1]
            buy_signal = stoch_buy_signal.loc[prev_day]
            sell_signal = stoch_sell_signal.loc[prev_day]

            return buy_signal, sell_signal

        except Exception as e:
            logger.error(f"Error calculating signals for {stock}: {e}")
            return False, False

    def check_signals(self):
        """Check buy and sell signals for the filtered stocks, but only generate sell signals for stocks with open positions."""
        start_date_daily = timezone.now() - timedelta(days=200)
        start_date_weekly = timezone.now() - timedelta(days=200)
        end_date = timezone.now() - timedelta(days=1)

        buy_signals = []
        sell_signals = []

        for stock in self.filtered_stocks:
            logger.info(f"Processing stock: {stock}")

            try:
                bars_daily = self.fetch_daily_data(stock, start_date_daily, end_date)
                time.sleep(1)
                bars_weekly = self.fetch_weekly_data(stock, start_date_weekly, end_date)
                time.sleep(1)

                buy_signal, sell_signal = self.calculate_signals(stock, bars_daily, bars_weekly)

                # Scenario 1 & 2: No Buy Signal after passing First Screen
                if not buy_signal:
                    logger.info(f"No Buy Signal From Indicator for {stock}")
                    BotOperation.objects.create(
                        user=self.user,
                        stock_symbol=stock,
                        stage="Indicator",
                        status="Failed",
                        reason="No Buy Signal From Indicator",
                        timestamp=timezone.now()
                    )

                if buy_signal:
                    if stock in self.open_positions:
                        logger.info(f"There is already a position for {stock}. Skipping buy order.")
                    else:
                        logger.info(f"Buy signal for {stock} on {bars_daily.index[-1]}")
                        buy_signals.append((stock, bars_daily.index[-1]))
                        BotOperation.objects.create(
                            user=self.user,
                            stock_symbol=stock,
                            stage="Indicator",
                            status="Passed",
                            reason="Indicator Generated Buy Signal",
                            timestamp=timezone.now()
                        )
                    time.sleep(1)

                # Scenario 3: No Sell Signal for open positions
                if stock in self.open_positions and not sell_signal:
                    logger.info(f"No Sell Signal From Indicator for {stock}")
                    BotOperation.objects.create(
                        user=self.user,
                        stock_symbol=stock,
                        stage="Indicator",
                        status="Failed",
                        reason="No Sell Signal From Indicator",
                        timestamp=timezone.now()
                    )
                elif sell_signal and stock in self.open_positions:
                    logger.info(f"Sell signal for {stock} on {bars_daily.index[-1]}")
                    sell_signals.append((stock, bars_daily.index[-1]))
                    BotOperation.objects.create(
                        user=self.user,
                        stock_symbol=stock,
                        stage="Indicator",
                        status="Passed",
                        reason="Indicator Generated Sell Signal",
                        timestamp=timezone.now()
                    )

            except Exception as e:
                logger.error(f"Error processing stock {stock}: {e}")


        return buy_signals, sell_signals
