from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import vectorbt as vbt
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.io as pio
import json
from .models import UserSetting 

# Fetch user settings including API keys, capital, etc.
def get_user_settings(user_id):
    try:
        print(f"Fetching user settings for user_id: {user_id}")
        user_settings = UserSetting.objects.get(user_id=user_id)

        print(f"User settings fetched: {user_settings}")
        return {
            'api_key': user_settings.alpaca_api_key,
            'api_secret': user_settings.alpaca_api_secret,
        }
    except Exception as e:
        print(f"Error fetching user settings: {e}")
        return None

# Function to safely handle float values for JSON serialization
def safe_float_conversion(value):
    """Convert values to JSON-safe floats or None."""
    if isinstance(value, (int, float)):
        if np.isnan(value) or np.isinf(value):
            return None
        return value
    return None

def run_backtest(user_id, trade_frequency, symbol, start_date, end_date, total_capital):
    print(f"Starting backtest with params: user_id={user_id}, trade_frequency={trade_frequency}, symbol={symbol}, start_date={start_date}, end_date={end_date}, total_capital={total_capital}")

    # Convert start_date and end_date from string to datetime if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    user_settings = get_user_settings(user_id)
    
    if user_settings is None:
        return {'error': 'User settings not found'}
    
    API_KEY = user_settings['api_key']
    API_SECRET = user_settings['api_secret']
    
    # Initialize Alpaca client with user's API keys
    print(f"Initializing Alpaca client with API_KEY: {API_KEY}")
    client = StockHistoricalDataClient(API_KEY, API_SECRET)
    
    # Determine TimeFrame and data resolution based on trade_frequency
    print(f"Determining timeframes based on trade_frequency: {trade_frequency}")
    if trade_frequency == 'weekly':
        timeframe1 = TimeFrame.Week
        timeframe2 = TimeFrame.Day
        max_duration = pd.Timedelta(days=5*365)  # 5 years
    elif trade_frequency == 'daily':
        timeframe1 = TimeFrame.Day
        timeframe2 = TimeFrame.Hour
        max_duration = pd.Timedelta(days=3*365)  # 3 years
    elif trade_frequency == 'hourly':
        timeframe1 = TimeFrame.Hour
        timeframe2 = TimeFrame.Minute
        max_duration = pd.Timedelta(days=365)  # 1 year
    
    # Ensure the selected start date is within allowed duration
    print(f"Checking if date range is valid: start_date={start_date}, end_date={end_date}, max_duration={max_duration}")
    if (end_date - start_date) > max_duration:
        print("Date range exceeds allowed duration.")
        return {'error': 'Date range exceeds allowed duration'}
    
    # Fetch data based on the determined timeframes
    def fetch_timeframe(stock, start_date, end_date, timeframe):
        print(f"Fetching data for stock={stock}, timeframe={timeframe}, start_date={start_date}, end_date={end_date}")
        request_params = StockBarsRequest(
            symbol_or_symbols=stock,
            timeframe=timeframe,
            start=start_date,
            end=end_date,
            adjustment='all'
        )
        bars = client.get_stock_bars(request_params).df.reset_index(level='symbol', drop=True)
        print(f"Fetched data for {stock}: {bars.head()}")
        return bars
    
    bars_long = fetch_timeframe(symbol, start_date, end_date, timeframe1)
    bars_short = fetch_timeframe(symbol, start_date, end_date, timeframe2)

    # Stochastic Oscillator signals on bars_long (higher timeframe)
    print("Running Stochastic Oscillator on bars_long")
    stoch = vbt.STOCH.run(
        high=bars_long['high'], 
        low=bars_long['low'], 
        close=bars_long['close'],
        k_window=10, 
        d_window=3, 
        d_ewm=False  
    )
    
    # Buy and sell signals
    stoch_k = stoch.percent_k
    stoch_d = stoch.percent_d
        
    stoch_buy_signal = (stoch_k > 32) & (stoch_k > stoch_d)
    stoch_buy_signal = stoch_buy_signal.reindex(bars_short.index, method='ffill').fillna(False)
        
    stoch_sell_signal = (stoch_k < 80) & (stoch_k < stoch_d)
    stoch_sell_signal = stoch_sell_signal.reindex(bars_short.index, method='ffill').fillna(False)

    # Backtest and analyze using VectorBT
    print(f"Running backtest with VectorBT for {symbol}")
    portfolio = vbt.Portfolio.from_signals(
        close=bars_short['close'],  # Use entire bars_short for close prices
        entries=stoch_buy_signal,   # Use all buy signals over the time period
        exits=stoch_sell_signal,    # Use all sell signals over the time period
        init_cash=total_capital,    # Use provided total_capital
    )

    # Performance analysis
    print(f"Performance stats for {symbol}:")
    performance_stats = portfolio.stats()
    print(performance_stats)

    # Convert Timestamps to strings for JSON serialization
    equity_curve = portfolio.value().to_dict()
    equity_curve_str = {str(key): safe_float_conversion(value) for key, value in equity_curve.items()}

    # Ensure all stats are JSON-safe
    stats_dict = performance_stats.to_dict()
    safe_stats = {key: safe_float_conversion(value) for key, value in stats_dict.items()}

    # Convert Plotly figure to JSON
    portfolio_fig = portfolio.plot()
    plotly_json = json.loads(pio.to_json(portfolio_fig))

    # Return backtest stats, equity curve, and Plotly JSON data
    return {
        'stats': safe_stats,
        'equity_curve': equity_curve_str,  # Return the equity curve with stringified timestamps
        'plot_data': plotly_json,          # Send Plotly chart data as JSON
        'entries': int(stoch_buy_signal.sum()),  # Ensure signals are integers
        'exits': int(stoch_sell_signal.sum())    # Ensure signals are integers
    }
