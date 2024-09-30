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
    user_id = user.id

    if sell_signals:
        for stock, date in sell_signals:
            stock = stock.strip()
            logger.info(f"Processing stock: {stock} for date: {date}")

            try:
                # Since you already filtered signals for stocks with open positions, no need to check again.

                # Check if there is already an open order for the stock
                orders = trading_client.get_orders(filter=GetOrdersRequest(
                    status=QueryOrderStatus.OPEN,
                    symbol=stock,
                    side=OrderSide.SELL  # Filter for sell orders directly
                ))

                if any(order.status in [OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.PENDING_NEW] for order in orders):
                    logger.info(f"There are open sell orders for {stock}. Skipping...")
                    # Log the failure due to open sell orders
                    BotOperation.objects.create(
                        user=user,
                        stock_symbol=stock,
                        stage="Order Status", 
                        status="Failed",  
                        reason=f"There is already an open sell order for {stock}",
                        timestamp=timezone.now()
                    )
                    continue

                # Generate a unique client order ID
                client_order_id = str(uuid.uuid4())

                # Submit a market order to sell
                trading_client.close_position(
                    symbol_or_asset_id=stock,
                    close_options=ClosePositionRequest(
                        percentage="100",
                        time_in_force=TimeInForce.DAY,
                        client_order_id=client_order_id
                    )
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

                # Timeout settings for waiting for the position to close
                timeout = 120  # seconds
                start_time = time.time()

                # Check position status with timeout and dynamic sleep
                while time.time() - start_time < timeout:
                    # Refresh positions to check if it has been closed
                    positions = trading_client.get_all_positions()
                    position = next((pos for pos in positions if pos.symbol == stock), None)

                    if position is None:
                        logger.info(f"Position for {stock} has been closed.")
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
                        time.sleep(2)  # Retry after a delay if the position is still open

                # Handle timeout case
                if position is not None:
                    logger.error(f"Timeout while waiting for position {stock} to close.")
                    BotOperation.objects.create(
                        user=user,
                        stock_symbol=stock,
                        stage="Order Confirmation", 
                        status="Failed",  
                        reason=f"Timeout while waiting for position {stock} to close",
                        timestamp=timezone.now()
                    )

            except Exception as e:
                logger.error(f"Error executing sell order for {stock}: {type(e).__name__} - {e}")
                # Log any errors during the order execution
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Confirmation", 
                    status="Failed", 
                    reason=f"Error executing sell order for {stock}: {type(e).__name__} - {e}",
                    timestamp=timezone.now()
                )
