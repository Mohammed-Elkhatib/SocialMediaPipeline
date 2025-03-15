import os
import json
import logging
from src.kafka.consumers.base import BaseConsumer
from src.models.relational.tweets import TweetModel
from src.config import Config


class StorageConsumer(BaseConsumer):
    def __init__(self):
        """Initialize the storage consumer with its own consumer group."""
        super().__init__(Config.KAFKA_TOPIC, 'storage-consumer-group')
        self.tweet_model = TweetModel()
        self.logger = logging.getLogger(__name__)

    def process_message(self, message):
        """
        Process a message from Kafka and store it in the database.

        Args:
            message (dict): The message from Kafka containing tweet data
        """
        try:
            # Extract tweet data from the message
            tweet_id = message.get('id')
            date = message.get('date')
            time = message.get('time')
            content = message.get('content')
            likes = message.get('likes', 0)
            retweets = message.get('retweets', 0)
            comments = message.get('comments', 0)

            # Validate required fields
            if not all([tweet_id, date, time, content]):
                self.logger.warning(f"Skipping message due to missing required fields: {message}")
                return

            # Store tweet data in the database
            self.tweet_model.insert_post_and_engagement_metrics(
                platform='x',  # Hardcoded for now, could be dynamic in the future
                post_date=date,
                post_time=time,
                content=content,
                likes=likes,
                retweets=retweets,
                comments=comments
            )
            self.logger.info(f"Stored tweet {tweet_id} from {date} {time}")

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and run the consumer
    logger = logging.getLogger(__name__)
    logger.info("Starting Storage Consumer...")

    consumer = StorageConsumer()
    consumer.consume_messages(consumer.process_message)

    logger.info("Storage Consumer finished.")
    