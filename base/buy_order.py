from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderStatus
import uuid
from datetime import datetime
import time
import logging
from .models import BotOperation, User
from django.contrib.auth import get_user_model

# Configure logging
class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            user = get_user_model().objects.get(username=record.username)
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

def execute_buy_orders(user, buy_signals, API_KEY, API_SECRET, position_size):
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

    if buy_signals:
        account = trading_client.get_account()
        buying_power = float(account.buying_power)
        total_equity = float(account.equity)
        logger.info(f"User's buying power: {buying_power}. User's total equity: {account.equity}", extra={'username': user.username})

        for stock, date in buy_signals:
            stock = stock.strip()
            logger.info(f"Processing stock: {stock} for date: {date}", extra={'username': user.username})

            try:
                orders = trading_client.get_orders(filter=GetOrdersRequest(
                                                    status=QueryOrderStatus.ALL,
                                                    symbol=stock,
                                                    side=OrderSide.BUY))

                if any(order.symbol == stock and order.side == OrderSide.BUY and order.status == OrderStatus.NEW for order in orders):
                    logger.info(f"There are open orders for {stock}. Skipping...", extra={'username': user.username})
                    continue

                positions = trading_client.get_all_positions()
                if any(position.symbol == stock for position in positions):
                    logger.info(f"There is already a position for {stock}. Skipping", extra={'username': user.username})
                    continue

                amount = round(total_equity * (position_size / 100), 2)

                if buying_power < amount:
                    logger.info(f"Not enough buying power to continue. Current buying power: {buying_power}", extra={'username': user.username})
                    break

                client_order_id = str(uuid.uuid4())

                trading_client.submit_order(order_data=MarketOrderRequest(
                                            symbol=stock,
                                            notional=amount,
                                            side=OrderSide.BUY,
                                            time_in_force=TimeInForce.DAY,
                                            client_order_id=client_order_id))

                logger.info(f"Market order (ID-{client_order_id}) was submitted to buy ${amount} worth of {stock}.", extra={'username': user.username})
                # Log the order submission
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Confirmation",  # Stage: Order Confirmation
                    status="Submitted",  # Status: Order submitted
                    reason=f"Buy order submitted for {stock}",
                    timestamp=datetime.now()
                )
                time.sleep(2)

                while True:
                    order = trading_client.get_order_by_client_id(client_order_id)
                    if order.status == OrderStatus.FILLED:
                        logger.info(f"Order for {stock} has been filled.", extra={'username': user.username})
                        # Log the order fill
                        BotOperation.objects.create(
                            user=user,
                            stock_symbol=stock,
                            stage="Order Confirmation",  # Stage: Order Confirmation
                            status="Filled",  # Status: Order filled
                            reason=f"Buy order filled for {stock}",
                            timestamp=datetime.now()
                        )
                        break
                    elif order.status in [OrderStatus.CANCELED, OrderStatus.REJECTED]:
                        logger.warning(f"Order for {stock} was {order.status}.", extra={'username': user.username})
                        # Log the order rejection/cancellation
                        BotOperation.objects.create(
                            user=user,
                            stock_symbol=stock,
                            stage="Order Confirmation",  # Stage: Order Confirmation
                            status=order.status,  # Status: Order status
                            reason=f"Buy order {order.status.lower()} for {stock}",
                            timestamp=datetime.now()
                        )
                        break
                    time.sleep(2)

            except Exception as e:
                logger.error(f"Error executing buy order for {stock}: {e}", extra={'username': user.username})
                # Log any errors during the order execution
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Confirmation",  # Stage: Order Confirmation
                    status="Error",  # Status: Error occurred
                    reason=f"Error executing buy order for {stock}: {e}",
                    timestamp=datetime.now()
                )
