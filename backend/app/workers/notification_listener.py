import json
import logging

from redis import Redis

from app.core.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = client.pubsub()
    pubsub.subscribe("ticket.assignment")
    logger.info("Listening for ticket.assignment notifications")
    for message in pubsub.listen():
        if message["type"] == "message":
            payload = json.loads(message["data"])
            logger.info("Notification received: %s", payload)


if __name__ == "__main__":
    main()
