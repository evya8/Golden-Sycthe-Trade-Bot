from django.apps import AppConfig
import threading
import logging
from .bot import schedule_all_bots 

logger = logging.getLogger(__name__)

class BaseConfig(AppConfig):
    name = 'base'
    scheduler_started = False

    def ready(self):
        # Prevent multiple threads from being started on multiple calls to ready()
        if not self.scheduler_started:
            self.scheduler_started = True
            logger.info("Starting the bot scheduler...")

            # Start the bot scheduler in a separate thread
            bot_scheduler_thread = threading.Thread(target=schedule_all_bots, daemon=True)
            bot_scheduler_thread.start()

            logger.info("Scheduler started successfully.")
        else:
            logger.info("Scheduler has already been started.")
