from django_q.tasks import async_task, schedule
from .bot import run_bot
import pytz
from datetime import datetime, timedelta

def run_bot_task():
    run_bot()

def schedule_daily_bot():
    israel_tz = pytz.timezone('Asia/Jerusalem')
    now = datetime.now(israel_tz)
    schedule_time = now.replace(hour=17, minute=15, second=0, microsecond=0)

    # If the schedule time has already passed for today, set it for tomorrow
    if now > schedule_time:
        schedule_time += timedelta(days=1)

    # Schedule the task
    schedule(
        'base.tasks.run_bot_task',
        next_run=schedule_time,
        schedule_type='D',  # Daily
        repeats=-1,  # Repeat indefinitely
        cluster='default'
    )
