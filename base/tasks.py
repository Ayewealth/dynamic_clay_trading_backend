from .models import InvestmentSubscription
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def daily_update_total_return():
    logger.info("Running daily update total return task")
    subscriptions = InvestmentSubscription.objects.filter(
        end_date__gte=timezone.now())
    for subscription in subscriptions:
        subscription.update_total_return()
        logger.info(f"Updated total return for subscription {subscription.id}")
