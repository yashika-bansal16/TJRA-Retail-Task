import redis
import json
import os
from typing import Optional

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
QUEUE_NAME = "analytics_events"

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)


def enqueue_event(event_data: dict) -> bool:
    """
    Add event to the processing queue.
    Returns True if successful, False otherwise.
    """
    try:
        redis_client.lpush(QUEUE_NAME, json.dumps(event_data))
        return True
    except Exception as e:
        print(f"Error enqueueing event: {e}")
        return False


def dequeue_event() -> Optional[dict]:
    """
    Remove and return an event from the processing queue.
    Returns None if queue is empty.
    """
    try:
        event_json = redis_client.brpop(QUEUE_NAME, timeout=1)
        if event_json:
            return json.loads(event_json[1])
        return None
    except Exception as e:
        print(f"Error dequeueing event: {e}")
        return None


def get_queue_length() -> int:
    """Get the current length of the queue"""
    try:
        return redis_client.llen(QUEUE_NAME)
    except Exception:
        return 0

