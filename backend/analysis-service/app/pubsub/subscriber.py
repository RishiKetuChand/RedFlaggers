import json
import logging
import asyncio
import multiprocessing
import os
import sys
from concurrent.futures import TimeoutError
from typing import Dict, Any

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message

from ..config.settings import settings
from ..processing.processor import AnalysisProcessor
from ..pubsub.publisher import PubSubPublisher

logger = logging.getLogger(__name__)


class PubSubSubscriber:
    def __init__(self):
        self.subscriber_client = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber_client.subscription_path(
            settings.gcp.project_id, settings.gcp.subscription_name
        )
        self.processor = AnalysisProcessor()
        self.publisher = PubSubPublisher()

    def start_listening(self):
        logger.info(f"Starting to listen on subscription: {self.subscription_path}")
        
        streaming_pull_future = self.subscriber_client.subscribe(
            self.subscription_path, callback=self._callback
        )

        logger.info("📡 Listening for messages...")

        try:
            streaming_pull_future.result()  # Keep listening indefinitely
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            streaming_pull_future.cancel()
        except Exception as e:
            logger.error(f"Subscriber error: {str(e)}")
            streaming_pull_future.cancel()

    def _callback(self, message: Message) -> None:
        logger.info(f"Received message: {message.message_id}")
        
        try:
            # Decode message data
            data = json.loads(message.data.decode('utf-8'))
            logger.info(f"Processing request for startup: {data.get('startup_name', 'unknown')}")
            
            # Log message attributes if any
            if message.attributes:
                logger.debug("Message attributes:")
                for key, value in message.attributes.items():
                    logger.debug(f"  {key}: {value}")
            
            # Validate message format
            if not self._validate_message(data):
                logger.error(f"Invalid message format: {data}")
                message.ack()
                return
            
            # Start a new process for this message
            process = multiprocessing.Process(
                target=self._process_message_in_subprocess,
                args=(data, message.message_id)
            )
            process.start()
            
            # Acknowledge message immediately after starting process
            message.ack()
            logger.info(f"Started process {process.pid} for message: {message.message_id}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message {message.message_id}: {str(e)}")
            message.ack()
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {str(e)}")
            message.ack()

    @staticmethod
    def _process_message_in_subprocess(data: Dict[str, Any], message_id: str) -> None:
        """Process message in a separate process"""
        # Set up logging for subprocess
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"🔄 Starting processing in subprocess for message: {message_id}")
            
            # Create processor and publisher instances in subprocess
            processor = AnalysisProcessor()
            publisher = PubSubPublisher()
            
            # Create new event loop for this process
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the async processing
                result = loop.run_until_complete(processor.process_analysis_request(data))
                
                # Publish result
                if result.get('status') == 'completed':
                    success = publisher.publish_result(result)
                    if success:
                        logger.info(f"📤 Successfully published result for: {result.get('startup_name')}")
                    else:
                        logger.error(f"Failed to publish result for: {result.get('startup_name')}")
                else:
                    publisher.publish_error(result)
                    logger.error(f"Analysis failed for: {result.get('startup_name')}")
                    
            finally:
                loop.run_until_complete(asyncio.wait_for(asyncio.sleep(1.0), timeout=5.0))
                loop.close()
                
        except Exception as e:
            logger.error(f"Error in subprocess processing for message {message_id}: {str(e)}")
            try:
                publisher = PubSubPublisher()
                error_data = {
                    "startup_name": data.get('startup_name', 'unknown'),
                    "error": str(e),
                    "timestamp": None,
                    "request_id": None
                }
                publisher.publish_error(error_data)
            except Exception as pub_error:
                logger.error(f"Failed to publish error: {str(pub_error)}")
        finally:
            logger.info(f"Subprocess completed for message: {message_id}")
            sys.exit(0)

    def _validate_message(self, data: Dict[str, Any]) -> bool:
        """Validate that message contains required fields"""
        required_fields = ['rag_corpus', 'startup_name', 'upload_id']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return False
            
        return True
