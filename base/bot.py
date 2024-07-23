import logging
from datetime import datetime
import time
import pytz
from .stochastic_momentum import StochasticMomentumStrategy
from .buy_order import execute_buy_orders
from .sell_order import execute_sell_orders
from .config import API_KEY, API_SECRET
from .models import UserSetting
from django.contrib.auth.models import User



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_user_settings(user_id):
    try:
        user = User.objects.get(id=user_id)
        user_settings = UserSetting.objects.get(user=user)
        # Assuming you need to decrypt the secret for usage
        return {
            'alpaca_api_key': user_settings.alpaca_api_key,
            'alpaca_api_secret': user_settings.alpaca_api_secret,  # Decrypt if necessary
            'position_size': user_settings.position_size,
        }
    except User.DoesNotExist:
        return None
    except UserSetting.DoesNotExist:
        return None
    


def run_bot():
    try:
        strategy = StochasticMomentumStrategy()
        buy_signals, sell_signals = strategy.check_signals()

        if buy_signals:
            logging.info(f"Executing buy orders for {len(buy_signals)} stocks.")
            execute_buy_orders(buy_signals, API_KEY, API_SECRET)

        if sell_signals:
            logging.info(f"Executing sell orders for {len(sell_signals)} stocks.")
            execute_sell_orders(sell_signals, API_KEY, API_SECRET)

        logging.info("Trading bot run completed. Next Activation tomorrow at 17:15 Israel time.")
    except Exception as e:
        logging.error(f"An error occurred while running the trading bot: {e}")

def schedule_bot():
    israel_tz = pytz.timezone('Asia/Jerusalem')
    schedule_time = "17:15"

    while True:
        now = datetime.now(israel_tz).strftime("%H:%M")
        if now == schedule_time:
            run_bot()
        time.sleep(60)
