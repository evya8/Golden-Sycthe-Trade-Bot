from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest, ClosePositionRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus, OrderStatus
import logging
import uuid
import time
from datetime import datetime
from .models import BotOperation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_sell_orders(user, sell_signals, API_KEY, API_SECRET):
    trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

    if sell_signals:
        for stock, date in sell_signals:
            stock = stock.strip()
            logger.info(f"Processing stock: {stock} for date: {date}", extra={'username': user.username})

            try:
                # Check if there is already an open position for the stock
                positions = trading_client.get_all_positions()
                position = next((pos for pos in positions if pos.symbol == stock), None)

                if position is None:
                    logger.info(f"No position found for {stock}. Skipping...", extra={'username': user.username})
                    # Log the failure due to no position
                    BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Status", 
                    status="Failed",  
                    reason=f"There is no position for {stock}",
                    timestamp=datetime.now()
                    )
                    continue

                logger.info(f"Found a position of {position.qty} for {stock}", extra={'username': user.username})

                # Check if there is already an open order for the stock
                orders = trading_client.get_orders(filter=GetOrdersRequest(
                                                   status=QueryOrderStatus.OPEN,
                                                   symbol=stock,
                                                   side=OrderSide.SELL))
                    
                if any(order.symbol == stock and order.side == OrderSide.SELL and order.status in [OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.PENDING_NEW] for order in orders):
                    logger.info(f"There are open orders for {stock}. Skipping...", extra={'username': user.username})
                    # Log the failure due to open orders
                    BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Status", 
                    status="Failed",  
                    reason=f"There is already open sell order for {stock}",
                    timestamp=datetime.now()
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
                        client_order_id=client_order_id)
                )

                logger.info(f"Closing position of {stock}, Order ID-{client_order_id}.", extra={'username': user.username})
                # Log the order submission
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Status", 
                    status="Passed",  
                    reason=f"Sell order submitted for {stock}",
                    timestamp=datetime.now()
                )
                time.sleep(3)

                # Check Position Status
                while True:
                    positions = trading_client.get_all_positions()
                    position = next((pos for pos in positions if pos.symbol == stock), None)

                    if position is None:
                        logger.info(f"Position for {stock} has been closed", extra={'username': user.username})
                        # Log the order fulfillment
                        BotOperation.objects.create(
                            user=user,
                            stock_symbol=stock,
                            stage="Order Confirmation",  # Stage: Order Confirmation
                            status="Filled",  # Status: Order filled
                            reason=f"Sell order filled for {stock}",
                            timestamp=datetime.now()
                        )
                        break
                    else:
                        logger.info(f"Waiting for position {stock} to close...", extra={'username': user.username})
                        time.sleep(2)

            except Exception as e:
                logger.error(f"Error executing sell order for {stock}: {e}", extra={'username': user.username})
                # Log any errors during the order execution
                BotOperation.objects.create(
                    user=user,
                    stock_symbol=stock,
                    stage="Order Confirmation",  # Stage: Order Confirmation
                    status="Failed", 
                    reason=f"Error executing sell order for {stock}: {e}",
                    timestamp=datetime.now()
                )
