from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderStatus
from django.utils import timezone
import uuid
import time
import logging
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

def execute_buy_orders(user, buy_signals, API_KEY, API_SECRET, position_size):
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)
    user_id = user.id

    if buy_signals:
        account = trading_client.get_account()
        buying_power = float(account.buying_power)
        total_equity = float(account.equity)
        logger.info(f"User's buying power: {buying_power}. User's total equity: {account.equity}")

        for stock, date in buy_signals:
            stock = stock.strip()
            logger.info(f"Processing stock: {stock} for date: {date}")

            try:
                # Check for existing open buy orders for this stock
                orders = trading_client.get_orders(filter=GetOrdersRequest(
                                                    status=QueryOrderStatus.ALL,
                                                    symbol=stock,
                                                    side=OrderSide.BUY))

                if any(order.status in [OrderStatus.NEW, OrderStatus.PENDING_NEW, OrderStatus.ACCEPTED] for order in orders):
                    logger.info(f"There are open buy orders for {stock}. Skipping...")
                    # Log the failure due to open buy orders
                    BotOperation.objects.create(
                        user=user,
                        stock_symbol=stock,
                        stage="Order Status",
                        status="Failed",
                        reason=f"There Is Already An Open Buy Order For {stock}",
                        timestamp=timezone.now()
                    )
                    time.sleep(2)
                    continue

                # Calculate the amount to spend based on the position size
                amount = round(total_equity * (position_size / 100), 2)

                # Check if buying power is sufficient for the buy order
                if buying_power < amount:
                    logger.info(f"Not enough buying power to continue. Current buying power: {buying_power}")
                    # Log the failure due to insufficient buying power
                    BotOperation.objects.create(
                        user=user,
                        stock_symbol=stock,
                        stage="Order Status",
                        status="Failed",
                        reason=f"Not Enough Buying Power For {stock}",
                        timestamp=timezone.now()
                    )
                    break  # Stop processing further buy signals since the buying power is insufficient

                # Generate a unique order ID for tracking
                client_order_id = str(uuid.uuid4())

                # Submit the buy order
                trading_client.submit_order(order_data=MarketOrderRequest(
                                            symbol=stock,
                                            notional=amount,
                                            side=OrderSide.BUY,
                                            time_in_force=TimeInForce.DAY,
                                            client_order_id=client_order_id))

                logger.info(f"Market order (ID-{client_order_id}) was submitted to buy ${amount} worth of {stock}.")
                # Log the order submission
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Status",  
                    status="Passed", 
                    reason=f"Buy Order Submitted For {stock}",
                    timestamp=timezone.now()
                )
                time.sleep(2)

                # Wait for order status update and handle it accordingly
                while True:
                    order = trading_client.get_order_by_client_id(client_order_id)
                    if order.status == OrderStatus.FILLED:
                        logger.info(f"Order for {stock} has been filled.")
                        # Log the order fill
                        BotOperation.objects.create(
                            user=user,
                            stock_symbol=stock,
                            stage="Order Confirmation",  # Stage: Order Confirmation
                            status="Passed",  
                            reason=f"Buy Order Filled For {stock}",
                            timestamp=timezone.now()
                        )
                        time.sleep(2)
                        break
                    elif order.status in [OrderStatus.CANCELED, OrderStatus.REJECTED]:
                        logger.warning(f"Order for {stock} was {order.status}.")
                        # Log the order rejection or cancellation
                        BotOperation.objects.create(
                            user=user,
                            stock_symbol=stock,
                            stage="Order Confirmation",  # Stage: Order Confirmation
                            status="Failed",  
                            reason=f"Buy Order {order.status.lower()} for {stock}",
                            timestamp=timezone.now()
                        )
                        break
                    time.sleep(2)

            except Exception as e:
                logger.error(f"Error executing buy order for {stock}: {e}")   
                
