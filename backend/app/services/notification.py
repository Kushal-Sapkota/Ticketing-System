import json
import logging

from redis import Redis

from app.core.config import settings


logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.redis_url

    def publish_assignment(self, payload: dict) -> str:
        message = json.dumps(payload, default=str)
        logger.info("assignment_notification=%s", message)
        redis_client = Redis.from_url(self.redis_url, decode_responses=True)
        try:
            redis_client.publish("ticket.assignment", message)
        finally:
            redis_client.close()
        return message


notification_service = NotificationService()
