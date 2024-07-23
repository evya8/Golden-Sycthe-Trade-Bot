import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import vectorbt as vbt
from .config import API_KEY, API_SECRET

class StochasticMomentumStrategy:
    def __init__(self):
        self.client = StockHistoricalDataClient(API_KEY, API_SECRET)
        self.volume_threshold = 1000000
        self.beta_threshold = 1.5
        self.bid_ask_spread_threshold = 0.05
        self.filtered_stocks = self.screen_stocks()

    def screen_stocks(self):
        # Function to get symbols from the CSV file
        def get_symbols_from_csv():
            df = pd.read_csv('stock_symbols.csv')
            symbols = df['Symbol'].tolist()
            return symbols
        
        # Function to fetch detailed stock data
        def fetch_stock_data(symbols):
            data = {}
            for symbol in symbols:
                stock = yf.Ticker(symbol)
                try:
                    info = stock.info
                    bid = info.get('bid')
                    ask = info.get('ask')
                    if bid is not None and ask is not None:
                        bid_ask_spread = ask - bid
                    else:
                        bid_ask_spread = None
                    data[symbol] = {
                        'average_volume': info.get('averageVolume'),
                        'beta': info.get('beta'),
                        'bid': bid,
                        'ask': ask,
                        'bid_ask_spread': bid_ask_spread
                    }
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
                    continue
            return pd.DataFrame.from_dict(data, orient='index')

        # Function to split list into chunks
        def split_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                yield lst[i:i + chunk_size]

        # Split the list of symbols into chunks of 150
        symbol_chunks = list(split_list(get_symbols_from_csv(), 150))

        # Initialize an empty DataFrame to hold the filtered results
        filtered_stocks = pd.DataFrame()

        # Process each chunk
        for chunk in symbol_chunks:
            print(f"Processing chunk: {chunk[:5]}...")  # Print first 5 symbols in the chunk for reference
            chunk_data = fetch_stock_data(chunk)
            
            # Apply screening criteria
            criteria = (
                (chunk_data['average_volume'] > self.volume_threshold) & 
                (chunk_data['beta'] > self.beta_threshold) & 
                (chunk_data['bid_ask_spread'] < self.bid_ask_spread_threshold)
            )
            filtered_chunk = chunk_data[criteria]
            
            # Append filtered results to the final DataFrame
            filtered_stocks = pd.concat([filtered_stocks, filtered_chunk])

            # Drop duplicates based on the index (which is 'Stock' in this case)
            filtered_stocks = filtered_stocks[~filtered_stocks.index.duplicated()]

            # Sort the final DataFrame by average volume in descending order
            filtered_stocks = filtered_stocks.sort_values(by=['Average_Volume', 'Beta'], ascending=[False, False])

        print("Filtered stocks are:")
        print(filtered_stocks)

        return filtered_stocks.index.tolist()

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
        start_date_daily = datetime.now() - timedelta(days=200)
        start_date_weekly = datetime.now() - timedelta(days=200)
        end_date = datetime.now() - timedelta(days=1)

        buy_signals = []
        sell_signals = []
        
        for stock in self.filtered_stocks:
            logging.info(f"Processing stock: {stock}")

            try:
                bars_daily = self.fetch_daily_data(stock, start_date_daily, end_date)
                bars_weekly = self.fetch_weekly_data(stock, start_date_weekly, end_date)
                buy_signal, sell_signal = self.calculate_signals(stock, bars_daily, bars_weekly)

                if buy_signal:
                    logging.info(f"Buy signal for {stock} on {bars_daily.index[-1]}")
                    buy_signals.append((stock, bars_daily.index[-1]))
                
                if sell_signal:
                    logging.info(f"Sell signal for {stock} on {bars_daily.index[-1]}")
                    sell_signals.append((stock, bars_daily.index[-1]))
            
            except Exception as e:
                logging.error(f"Error processing stock {stock}: {e}")
        
        if not buy_signals and not sell_signals:
            logging.info("No buy or sell signals for any stock.")
        
        return buy_signals, sell_signals
