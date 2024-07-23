from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_q.tasks import schedule
from datetime import datetime, timedelta
import pytz

@receiver(post_migrate)
def schedule_daily_bot(sender, **kwargs):
    from base.tasks import run_bot_task

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
