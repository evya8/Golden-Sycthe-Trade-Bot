from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest, ClosePositionRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderStatus
import logging
import uuid
import pytz
from datetime import datetime
import time
from .config import API_KEY, API_SECRET, BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_market_open():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open_time <= now <= market_close_time

def execute_sell_orders(sell_signals, API_KEY, API_SECRET):
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

    if sell_signals:
        for stock, date in sell_signals:
            stock = stock.strip()  # Ensure there are no leading/trailing whitespaces
            logging.info(f"Processing stock: {stock} for date: {date}")

            try:
                # Check if there is already an open position for the stock
                positions = trading_client.get_all_positions()
                position = next((pos for pos in positions if pos.symbol == stock), None)
                
                if position is None:
                    logging.info(f"No position found for {stock}. Skipping...")
                    continue

                logging.info(f"Found a position of {position.qty} for {stock}")

                # Check if there is already an open order for the stock
                orders = trading_client.get_orders(filter=GetOrdersRequest(
                                                   status=QueryOrderStatus.OPEN,
                                                   symbol=stock,
                                                   side=OrderSide.SELL))
                    
                if any(order.symbol == stock and order.side == OrderSide.SELL and order.status in [OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.PENDING_NEW] for order in orders):
                    logging.info(f"There are open orders for {stock}. Skipping...")
                    continue

                # Generate a unique client order ID
                client_order_id = str(uuid.uuid4())

                # Submit a market order to sell
                trading_client.close_position(
                                            symbol_or_asset_id = stock,
                                            close_options = ClosePositionRequest(
                                            percentage = "100",
                                            time_in_force=TimeInForce.DAY,
                                            client_order_id = client_order_id))
                    
                logging.info(f"Closing position of {stock}, Order ID-{client_order_id}.")
                time.sleep(3)

                                 # Check Position Status
                market_open = is_market_open()
                while True:
                    positions = trading_client.get_all_positions()
                    position = next((pos for pos in positions if pos.symbol == stock), None)
                
                    if position is None:
                        logging.info(f"Position for {stock} has been closed")
                        break
                    elif not market_open:
                        logging.info(f"Market is closed, position status for {stock} is still open")
                        break
                    else:
                        logging.info(f"Waiting for position {stock} to close...")
                        time.sleep(2)
                    
            except Exception as e:
                logging.error(f"Error executing sell order for {stock}: {e}")
