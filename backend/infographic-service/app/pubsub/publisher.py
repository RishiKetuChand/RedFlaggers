import json
import logging
from typing import Dict, Any

from google.cloud import pubsub_v1
from google.cloud.exceptions import NotFound

from ..config.settings import settings

logger = logging.getLogger(__name__)


class PubSubPublisher:
    def __init__(self):
        self.publisher_client = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher_client.topic_path(
            settings.gcp.project_id, settings.gcp.output_topic_name
        )
        # Ensure topic exists (create if missing)
        self._ensure_topic_exists()

    def _ensure_topic_exists(self):
        try:
            self.publisher_client.get_topic(request={"topic": self.topic_path})
            logger.info(f"Topic already exists: {self.topic_path}")
        except NotFound:
            self.publisher_client.create_topic(request={"name": self.topic_path})
            logger.info(f"Created topic: {self.topic_path}")
        except Exception as e:
            logger.error(f"Error checking/creating topic: {str(e)}")
            raise e

    def publish_result(self, result_data: Dict[str, Any]) -> bool:
        """Publish analysis results to the output topic"""
        try:
            message_data = json.dumps(result_data).encode('utf-8')
            
            future = self.publisher_client.publish(self.topic_path, message_data)
            message_id = future.result()
            
            logger.info(f"Published result message with ID: {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish result: {str(e)}")
            return False

    def publish_error(self, error_data: Dict[str, Any]) -> bool:
        """Publish error information to the output topic"""
        error_message = {
            "status": "error",
            "timestamp": error_data.get("timestamp"),
            "error": error_data.get("error"),
            "startup_name": error_data.get("startup_name"),
            "request_id": error_data.get("request_id")
        }
        
        return self.publish_result(error_message)
