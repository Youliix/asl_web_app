import schedule
import time

from . import monitoring


def job():
    monitoring.send_email(monitoring.collect_metrics())


def run_scheduler():

    schedule.every(24).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
