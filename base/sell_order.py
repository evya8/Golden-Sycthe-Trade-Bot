from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest, ClosePositionRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderStatus
import logging
import uuid
import pytz
from datetime import datetime
import time
from .models import BotOperation, User
from django.contrib.auth import get_user_model

# Configure logging
class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            user = User.objects.get(username=record.username)
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
                while True:
                    positions = trading_client.get_all_positions()
                    position = next((pos for pos in positions if pos.symbol == stock), None)
                
                    if position is None:
                        logging.info(f"Position for {stock} has been closed")
                        break
                    else:
                        logging.info(f"Waiting for position {stock} to close...")
                        time.sleep(2)
                    
            except Exception as e:
                logging.error(f"Error executing sell order for {stock}: {e}")
