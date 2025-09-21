import logging
import signal
import sys

from .config.settings import settings
from .pubsub.subscriber import PubSubSubscriber
from .utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


class InfographicService:
    def __init__(self):
        setup_logging()
        logger.info("Initializing Infographic Service...")
        
        self.subscriber = PubSubSubscriber()
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def start(self):
        logger.info("Starting Infographic Service...")
        logger.info(f"GCP Project: {settings.gcp.project_id}")
        logger.info(f"Subscription: {settings.gcp.subscription_name}")
        logger.info(f"Output Topic: {settings.gcp.output_topic_name}")
        logger.info(f"Max Workers: {settings.service.max_workers}")
        logger.info(f"Model: {settings.service.model_name}")
        
        self.running = True
        
        try:
            # Start listening for messages - this will block indefinitely
            self.subscriber.start_listening()
        except Exception as e:
            logger.error(f"Service error: {str(e)}")
            raise
        finally:
            self.stop()

    def stop(self):
        if self.running:
            logger.info("Stopping Infographic Service...")
            self.running = False

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)