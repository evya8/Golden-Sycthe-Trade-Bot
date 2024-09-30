from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest, ClosePositionRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderStatus
from django.utils import timezone
import logging
import uuid
import time
from .models import BotOperation

# Subclass logging.Formatter to use UTC
class UTCFormatter(logging.Formatter):
    converter = time.gmtime  # Force UTC for log timestamps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Update the logger to use UTCFormatter
for handler in logger.handlers:
    handler.setFormatter(UTCFormatter('%(asctime)s - %(levelname)s - %(message)s'))


def execute_sell_orders(user, sell_signals, API_KEY, API_SECRET):
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
    user_id=user.id

    if sell_signals:
        for stock, date in sell_signals:
            stock = stock.strip()
            logger.info(f"Processing stock: {stock} for date: {date}")

            try:
                # Check if there is already an open position for the stock
                positions = trading_client.get_all_positions()
                position = next((pos for pos in positions if pos.symbol == stock), None)
                time.sleep(2)

                if position is None:
                    logger.info(f"No position found for {stock}. Skipping...")
                    # Log the failure due to no position
                    BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Status", 
                    status="Failed",  
                    reason=f"There is no position for {stock}",
                    timestamp=timezone.now()
                    )
                    continue

                logger.info(f"Found a position of {position.qty} for {stock}")

                # Check if there is already an open order for the stock
                orders = trading_client.get_orders(filter=GetOrdersRequest(
                                                   status=QueryOrderStatus.OPEN,
                                                   symbol=stock,
                                                   side=OrderSide.SELL))
                time.sleep(2)
                    
                if any(order.symbol == stock and order.side == OrderSide.SELL and order.status in [OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.PENDING_NEW] for order in orders):
                    logger.info(f"There are open orders for {stock}. Skipping...")
                    # Log the failure due to open orders
                    BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Status", 
                    status="Failed",  
                    reason=f"There is already open sell order for {stock}",
                    timestamp=timezone.now()
                    )
                    time.sleep(2)
                    continue

                # Generate a unique client order ID
                client_order_id = str(uuid.uuid4())

                # Submit a market order to sell
                trading_client.close_position(
                    symbol_or_asset_id=stock,
                    close_options=ClosePositionRequest(
                        percentage="100",
                        time_in_force=TimeInForce.DAY,
                        client_order_id=client_order_id)
                )

                logger.info(f"Closing position of {stock}, Order ID-{client_order_id}.")
                # Log the order submission
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Status", 
                    status="Passed",  
                    reason=f"Sell order submitted for {stock}",
                    timestamp=timezone.now()
                )
                time.sleep(2)

                # Check Position Status
                while True:
                    positions = trading_client.get_all_positions()
                    position = next((pos for pos in positions if pos.symbol == stock), None)

                    if position is None:
                        logger.info(f"Position for {stock} has been closed")
                        # Log the order fulfillment
                        BotOperation.objects.create(
                            user=user,
                            stock_symbol=stock,
                            stage="Order Confirmation",  # Stage: Order Confirmation
                            status="Filled",  # Status: Order filled
                            reason=f"Sell order filled for {stock}",
                            timestamp=timezone.now()
                        )
                        break
                    else:
                        logger.info(f"Waiting for position {stock} to close...")
                        time.sleep(2)

            except Exception as e:
                logger.error(f"Error executing sell order for {stock}: {e}")
                # Log any errors during the order execution
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Confirmation",  # Stage: Order Confirmation
                    status="Failed", 
                    reason=f"Error executing sell order for {stock}: {e}",
                    timestamp=timezone.now()
                )
