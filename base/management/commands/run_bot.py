from django.core.management.base import BaseCommand
from base.bot import run_bot

class Command(BaseCommand):
    help = 'Run the trading bot'

    def handle(self, *args, **kwargs):
        run_bot()
