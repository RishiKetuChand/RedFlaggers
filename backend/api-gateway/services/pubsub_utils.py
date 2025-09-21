from google.cloud import pubsub_v1
import json
from config import PROJECT_ID


def publish_message(topic_id: str, message: dict):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, topic_id)

    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f"📨 Published to {topic_path}: {message}")
    return future.result()
