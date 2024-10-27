import yfinance as yf

# Define the list of stock symbols you want to fetch data for
symbols = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN']

# Fetch data for each symbol using yfinance
for symbol in symbols:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")  # Fetch 1 day historical data
        
        # Use historical data to fetch volume
        volume = hist['Volume'].iloc[-1] if not hist.empty else None
        
        # Fetch beta from `info`
        beta = stock.info.get('beta')
        
        # Print out volume and beta
        print(f"Symbol: {symbol}")
        print(f"  Volume: {volume}")
        print(f"  Beta: {beta}")
        print("-" * 40)
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
