from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from .tasks import daily_update_total_return
import logging
import atexit
from django.conf import settings

logger = logging.getLogger(__name__)

# Check environment settings
ENVIRONMENT = settings.ENVIRONMENT
POSTGRES_LOCALLY = settings.POSTGRES_LOCALLY

if ENVIRONMENT == 'production' or POSTGRES_LOCALLY:
    database_url = settings.DATABASES['default']
    if isinstance(database_url, dict):
        from django.db.utils import ConnectionHandler
        connections = ConnectionHandler(settings.DATABASES)
        db_conn = connections['default']
        database_url = f"postgresql://{db_conn.settings_dict['USER']}:{db_conn.settings_dict['PASSWORD']}@{db_conn.settings_dict['HOST']}:{db_conn.settings_dict['PORT']}/{db_conn.settings_dict['NAME']}"

    # Using PostgreSQL as job store
    jobstores = {
        'default': SQLAlchemyJobStore(url=database_url)
    }
    scheduler = BackgroundScheduler(jobstores=jobstores)
else:
    scheduler = BackgroundScheduler()


def start():
    global scheduler
    if not scheduler.running:
        scheduler.add_job(
            daily_update_total_return,
            trigger=IntervalTrigger(hours=20),
            id='daily_update_total_return',
            name='Update total return every day',
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Scheduler started!")
        atexit.register(lambda: scheduler.shutdown())
    else:
        logger.info("Scheduler is already running.")


# Initialize the scheduler
start()
