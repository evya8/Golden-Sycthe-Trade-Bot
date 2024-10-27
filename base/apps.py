from django.apps import AppConfig
import threading
import logging
from django.core.cache import cache
from .bot import schedule_all_bots

logger = logging.getLogger(__name__)

class BaseConfig(AppConfig):
    name = 'base'

    def ready(self):
        if not cache.get('scheduler_started'):
            cache.set('scheduler_started', True, timeout=None)  # Persist the flag
            logger.info("Starting the bot scheduler...")

            # Start the bot scheduler in a separate thread
            bot_scheduler_thread = threading.Thread(target=schedule_all_bots, daemon=True)
            bot_scheduler_thread.start()

            logger.info("Scheduler started successfully.")
        else:
            logger.info("Scheduler has already been started.")
