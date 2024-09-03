import logging
from datetime import datetime
import time
import pytz
from .stochastic_momentum import StochasticMomentumStrategy
from .buy_order import execute_buy_orders
from .sell_order import execute_sell_orders
from .models import UserSetting, BotOperation
from django.contrib.auth.models import User

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

def get_user_settings(user_id):
    try:
        user = User.objects.get(id=user_id)
        user_settings = UserSetting.objects.get(user=user)
        return {
            'bot_active': user_settings.bot_active,
            'api_key': user_settings._alpaca_api_key,
            'api_secret': user_settings._alpaca_api_secret,  
            'position_size': user_settings.position_size,
            'filter_sector': user_settings.filter_sector,
            'filter_symbol': user_settings.filter_symbol
        }
    except User.DoesNotExist:
        return None
    except UserSetting.DoesNotExist:
        return None

def run_bot(user_id):
    try:
        settings = get_user_settings(user_id)
        if settings is None:
            logging.error(f"User settings for user ID {user_id} not found.")
            return

        if not settings['bot_active']:
            logging.info(f"Bot for user ID {user_id} is deactivated.")
            return

        API_KEY = settings['api_key']
        API_SECRET = settings['api_secret']
        position_size = settings['position_size']
        filter_sector = settings['filter_sector']
        filter_symbol = settings['filter_symbol']

        strategy = StochasticMomentumStrategy(API_KEY, API_SECRET)
        buy_signals, sell_signals = strategy.check_signals()

        if buy_signals:
            logging.info(f"Executing buy orders for {len(buy_signals)} stocks.")
            execute_buy_orders(buy_signals, API_KEY, API_SECRET, position_size)

        if sell_signals:
            logging.info(f"Executing sell orders for {len(sell_signals)} stocks.")
            execute_sell_orders(sell_signals, API_KEY, API_SECRET, position_size)

        logging.info("Trading bot run completed. Next Activation Monday-Friday at 10:15AM US/Eastern.")
    except Exception as e:
        logging.error(f"An error occurred while running the trading bot: {e}")

def deactivate_bot(user_id):
    # Add logic to stop the bot if needed (e.g., canceling orders, stopping scheduled tasks, etc.)
    logging.info(f"Deactivation logic for bot of user ID {user_id} executed.")
    # Implement any specific deactivation procedures here

def toggle_bot(user_id):
    try:
        user = User.objects.get(id=user_id)
        user_settings = UserSetting.objects.get(user=user)

        if user_settings.bot_active:
            # Deactivate the bot
            deactivate_bot(user_id)
            user_settings.bot_active = False
            logging.info(f"Bot for user ID {user_id} has been deactivated.")
        else:
            # Activate the bot
            run_bot(user_id)
            user_settings.bot_active = True
            logging.info(f"Bot for user ID {user_id} has been activated.")
        
        user_settings.save()
    except User.DoesNotExist:
        logging.error(f"User with ID {user_id} does not exist.")
        raise
    except UserSetting.DoesNotExist:
        logging.error(f"User settings for user ID {user_id} do not exist.")
        raise
    except Exception as e:
        logging.error(f"An error occurred while toggling the bot for user ID {user_id}: {e}")
        raise

def schedule_bot(user_id):
    eastern = pytz.timezone('US/Eastern')
    schedule_time = "10:15"

    while True:
        now = datetime.now(eastern)
        current_time = now.strftime("%H:%M")
        current_day = now.weekday()  # Monday is 0 and Sunday is 6

        # Run the bot only on weekdays (Monday to Friday)
        if current_time == schedule_time and current_day < 5:
            # Check if the bot is active before running it
            user_settings = get_user_settings(user_id)
            if user_settings and user_settings['bot_active']:
                run_bot(user_id)
            else:
                logging.info(f"Bot for user ID {user_id} is deactivated.")

        time.sleep(60)
