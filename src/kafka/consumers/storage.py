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
                missing_fields = []
                if not tweet_id: missing_fields.append('id')
                if not date: missing_fields.append('date')
                if not time: missing_fields.append('time')
                if not content: missing_fields.append('content')

                self.logger.warning(f"Skipping message due to missing required fields {missing_fields}: {message}")
                return

            # Store tweet data in the database
            self.tweet_model.insert_post(
                post_id=tweet_id,  # Changed from platform to match the updated method signature
                post_date=date,
                post_time=time,
                content=content,
                likes=likes,
                retweets=retweets,
                comments=comments
            )
            self.logger.info(f"Stored tweet {tweet_id} from {date} {time}")

        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)
            # Adding exc_info=True to log the full stack trace for better debugging


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
    # Adding a timeout to make the process more robust
    try:
        consumer.consume_messages(consumer.process_message, timeout_seconds=3600)  # 1 hour timeout
    except KeyboardInterrupt:
        logger.info("Storage Consumer stopped by user.")
    except Exception as e:
        logger.error(f"Storage Consumer encountered an error: {e}", exc_info=True)
    finally:
        logger.info("Storage Consumer finished.")
