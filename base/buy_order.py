from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderStatus
import uuid
import pytz
from datetime import datetime
import time
import logging
from .config import API_KEY, API_SECRET, BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_market_open():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open_time <= now <= market_close_time

def execute_buy_orders(buy_signals, API_KEY, API_SECRET):
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

    if buy_signals:
        account = trading_client.get_account()
        buying_power = float(account.buying_power)
        total_equity = float(account.equity)
        logging.info(f"User's buying power: {buying_power}. User's total equity: {account.equity}")

        for stock, date in buy_signals:
            stock = stock.strip()  # Ensure there are no leading/trailing whitespaces
            logging.info(f"Processing stock: {stock} for date: {date}")

            try:
                # Check if there is already an open order for the stock
                orders = trading_client.get_orders(filter=GetOrdersRequest(
                                                    status=QueryOrderStatus.ALL,
                                                    symbol=stock,
                                                    side=OrderSide.BUY))
                
                if any(order.symbol == stock and order.side == OrderSide.BUY and order.status == OrderStatus.NEW for order in orders):
                    logging.info(f"There are open orders for {stock}. Skipping...")
                    continue

                # Check if there is already an open position for the stock
                positions = trading_client.get_all_positions()
                if any(position.symbol == stock for position in positions):
                    logging.info(f"There is already a position for {stock}. Skipping")
                    continue

                # Calculate position size
                amount = round(total_equity * 0.01, 2) # position size to be selected by user

                # Check if there's still enough buying power
                if buying_power < amount :
                    logging.info(f"Not enough buying power to continue. Current buying power: {buying_power}")
                    break

                # Generate a unique client order ID
                client_order_id = str(uuid.uuid4())

                # Submit a market order to buy
                trading_client.submit_order(order_data=MarketOrderRequest(
                                            symbol=stock,
                                            notional=amount,
                                            side=OrderSide.BUY,
                                            time_in_force=TimeInForce.DAY,
                                            client_order_id=client_order_id))
                
                logging.info(f"Market order (ID-{client_order_id}) was submitted to buy ${amount} worth of {stock}.")
                time.sleep(2)

                         # Get Order Status
                market_open = is_market_open()
                while True:
                    order = trading_client.get_order_by_client_id(client_order_id)
                    if order.status == OrderStatus.FILLED:
                        logging.info(f"Order for {stock} has been filled.")
                        break
                    elif order.status in [OrderStatus.CANCELED, OrderStatus.REJECTED]:
                        logging.warning(f"Order for {stock} was {order.status}.")
                        break
                    elif order.status in [OrderStatus.ACCEPTED, OrderStatus.PENDING_NEW, OrderStatus.NEW]:
                        logging.info(f"Order for {stock} awaiting execution : {order.status}")
                        if not market_open:
                            break
                    time.sleep(2) 
                    

            except Exception as e:
                logging.error(f"Error executing buy order for {stock}: {e}")
