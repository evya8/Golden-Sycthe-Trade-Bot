import logging
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import time
from django.utils import timezone
import traceback
import json
from django.core.cache import cache

# Subclass logging.Formatter to use UTC
class UTCFormatter(logging.Formatter):
    converter = time.gmtime  # Force UTC for log timestamps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Update the logger to use UTCFormatter
for handler in logger.handlers:
    handler.setFormatter(UTCFormatter('%(asctime)s - %(levelname)s - %(message)s'))

# Dictionary to hold user locks
user_locks = {}

def get_user_lock(user_id):
    if user_id not in user_locks:
        user_locks[user_id] = threading.Lock()
    return user_locks[user_id]

def get_user_settings(user_id):
    try:
        from django.contrib.auth.models import User  # Import moved inside the function
        from .models import UserSetting  # Import moved inside the function
        user = User.objects.get(id=user_id)
        user_settings = UserSetting.objects.get(user=user)

        # Ensure filter_symbol and filter_sector are loaded as lists
        filter_symbol = json.loads(user_settings.filter_symbol) if user_settings.filter_symbol else []
        filter_sector = json.loads(user_settings.filter_sector) if user_settings.filter_sector else []

        logger.info(f"User settings fetched for user ID {user_id}")
        return {
            'user': user,
            'user_id': user_id,
            'bot_active': user_settings.bot_active,
            'api_key': user_settings.alpaca_api_key,
            'api_secret': user_settings.alpaca_api_secret,
            'position_size': user_settings.position_size,
            'filter_sector': filter_sector,
            'filter_symbol': filter_symbol
        }
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist.")
        return None
    except UserSetting.DoesNotExist:
        logger.error(f"User settings for user ID {user_id} do not exist.")
        return None
    except Exception as e:
        logger.error(f"Error fetching user settings for user {user_id}: {e}")
        return None

def validate_sectors(sectors):
    """Validate sectors to ensure they are a list of non-empty strings."""
    if isinstance(sectors, list):
        valid_sectors = [sector for sector in sectors if isinstance(sector, str) and sector.strip()]
        invalid_sectors = [sector for sector in sectors if sector not in valid_sectors]
        if invalid_sectors:
            logger.error(f"Invalid sectors detected: {invalid_sectors}")
        return valid_sectors
    else:
        logger.error(f"Expected list of sectors, got {type(sectors)}")
        return []

def validate_symbols(symbols):
    if isinstance(symbols, list):
        valid_symbols = [symbol for symbol in symbols if isinstance(symbol, str) and symbol.isalnum()]
        invalid_symbols = [symbol for symbol in symbols if symbol not in valid_symbols]
        if invalid_symbols:
            logger.error(f"Invalid symbols detected: {invalid_symbols}")
        return valid_symbols
    else:
        logger.error(f"Expected list of symbols, got {type(symbols)}")
        return []

def run_bot(user_id):
    lock = get_user_lock(user_id)
    if lock.locked():
        logger.warning(f"Bot for user {user_id} is already running.")
        return

    with lock:
        try:
            settings = get_user_settings(user_id)
            if settings is None:
                logger.error(f"User settings for user ID {user_id} not found.")
                return
            
            user = settings['user']

            logger.info(f"Running bot for user ID: {user_id}. Bot Active: {settings['bot_active']}")

            if not settings['bot_active']:
                logger.info(f"Bot for user ID {user_id} is deactivated.")
                return

            API_KEY = settings['api_key']
            API_SECRET = settings['api_secret']
            position_size = settings['position_size']
            filter_sector = settings['filter_sector']
            filter_symbol = settings['filter_symbol']

            logger.info(f"User ID: {user_id}, API Key: {API_KEY[:4]}****, Position Size: {position_size}, "
                        f"Sector Filter: {filter_sector}, Symbol Filter: {filter_symbol}")

            # Validate filter_symbol and filter_sector before processing
            valid_symbols = validate_symbols(filter_symbol)
            valid_sectors = validate_sectors(filter_sector)

            if not valid_symbols and not valid_sectors:
                logger.info(f"No filters provided from user {user_id}, proceeding to screen stocks")
                

            from .stochastic_momentum import StochasticMomentumStrategy  # Import moved inside the function
            strategy = StochasticMomentumStrategy(
                user=user,
                API_KEY=API_KEY,
                API_SECRET=API_SECRET,
                filter_symbol=valid_symbols,
                filter_sector=valid_sectors
            )

            logger.info(f"Running StochasticMomentumStrategy for user {user_id}")
            buy_signals, sell_signals = strategy.check_signals()

            logger.info(f"Buy signals for user {user_id}: {buy_signals}")
            logger.info(f"Sell signals for user {user_id}: {sell_signals}")

            if buy_signals:
                from .buy_order import execute_buy_orders  # Import moved inside the function
                logger.info(f"Executing buy orders for {len(buy_signals)} stocks for user {user_id}.")
                execute_buy_orders(user, buy_signals, API_KEY, API_SECRET, position_size)

            if sell_signals:
                from .sell_order import execute_sell_orders  # Import moved inside the function
                logger.info(f"Executing sell orders for {len(sell_signals)} stocks for user {user_id}.")
                execute_sell_orders(user, sell_signals, API_KEY, API_SECRET)

            logger.info(f"Bot run completed successfully for user ID {user_id} at {timezone.now()}.")

        except Exception as e:
            logger.error(f"An error occurred while running the trading bot for user ID {user_id}: {str(e)}")
            logger.error(f"Error details: {traceback.format_exc()}")

def deactivate_bot(user_id):
    logger.info(f"Deactivation logic for bot of user ID {user_id} executed.")
    # Implement any specific deactivation procedures here
    
def toggle_bot(user_id):
    try:
        from django.contrib.auth.models import User  # Import moved inside the function
        from .models import UserSetting  # Import moved inside the function
        user = User.objects.get(id=user_id)
        user_settings = UserSetting.objects.get(user=user)

        if user_settings.bot_active:
            # Deactivate the bot
            deactivate_bot(user_id)
            user_settings.bot_active = False
            logger.info(f"Bot for user ID {user_id} has been deactivated.")
        else:
            # Activate the bot
            run_bot(user_id)
            user_settings.bot_active = True
            logger.info(f"Bot for user ID {user_id} has been activated.")
        
        user_settings.save()
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist.")
    except UserSetting.DoesNotExist:
        logger.error(f"User settings for user ID {user_id} do not exist.")
    except Exception as e:
        logger.error(f"An error occurred while toggling the bot for user ID {user_id}: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")

# Global lock to ensure that the entire bot execution runs only once at a time
execution_lock = threading.Lock()

def run_bot_for_all_users():
    if execution_lock.locked():
        logger.warning("A bot execution is already in progress. Skipping this run.")
        return

    with execution_lock:
        logger.info(f"Attempting to run bots at {timezone.now()} (Server Time)")
        try:
            from .models import UserSetting  # Import moved inside the function
            active_users = UserSetting.objects.filter(bot_active=True).values_list('user_id', flat=True)

            logger.info(f"Running bot for {len(active_users)} active users.")

            for user_id in active_users:
                run_bot(user_id)  # Avoid threading, run bots sequentially to prevent overlap

        except Exception as e:
            logger.error(f"Error in running bots for users: {e}")
            logger.error(f"Error details: {traceback.format_exc()}")

### Scheduling with APScheduler

def schedule_all_bots():
    scheduler = BackgroundScheduler(timezone='US/Eastern')

    # Schedule the bot to run at 10:15 AM Monday to Friday
    scheduler.add_job(
        run_bot_for_all_users,
        'cron',
        day_of_week='mon-fri',
        hour=10,
        minute=15,
        misfire_grace_time=3600,  # Allow the job to run within 1 hour of the scheduled time
        max_instances=1,  # Only one instance should run at a time
        coalesce=False  # Do not merge missed executions to avoid stacking jobs
    )

    logger.info("Scheduler started. Bots will run at 10:15 AM Monday to Friday.")

    # Start the scheduler
    scheduler.start()

    try:
        # Keep the main thread alive while the scheduler is running
        while True:
            time.sleep(45)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down.")
