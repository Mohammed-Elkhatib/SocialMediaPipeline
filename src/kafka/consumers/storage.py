from src.kafka.consumers.base import BaseConsumer
from database.queries import SocialMediaQueries
import json
import logging


class DatabaseStorageConsumer(BaseConsumer):
    """
    Kafka consumer that stores social media data in the MySQL database.
    Extends the BaseConsumer and uses SocialMediaQueries for database operations.
    """

    def __init__(self, topic='social-media-data', group_id='database-storage-group'):
        """Initialize the consumer with database connection."""
        super().__init__(topic, group_id)
        self.db = SocialMediaQueries()
        logging.info("Database storage consumer initialized")
        self.processed_count = 0

    def process_message(self, message):
        """
        Process a single message from Kafka and store it in the database.

        Args:
            message (dict): The decoded Kafka message containing tweet data
        """
        try:
            # Extract required fields
            post_date = message.get('date')
            post_time = message.get('time')
            content = message.get('content')
            likes = message.get('likes', 0)
            retweets = message.get('retweets', 0)
            comments = message.get('comments', 0)

            # Validate required fields
            if not all([post_date, post_time, content]):
                logging.warning(f"Skipping message with missing required fields: {message}")
                return

            # Store in database (platform hardcoded as 'x' for now)
            self.db.insert_post_and_engagement_metrics(
                platform='x',
                post_date=post_date,
                post_time=post_time,
                content=content,
                likes=likes,
                retweets=retweets,
                comments=comments
            )

            self.processed_count += 1
            if self.processed_count % 10 == 0:
                logging.info(f"Stored {self.processed_count} messages in database")

        except Exception as e:
            logging.error(f"Error storing message in database: {e}")
            # Continue processing despite errors

    def update_analytics_tables(self):
        """
        Update analytics tables with aggregated data after processing.
        This includes word frequencies, top comments, and top likes.
        """
        try:
            # Get all posts for analytics processing
            posts = self.db.fetch_posts(platform='x')
            if not posts:
                logging.warning("No posts found for analytics processing")
                return

            # Process word frequencies
            all_content = ' '.join([post['content'] for post in posts])
            from src.utils.data_helpers import extract_keywords
            keywords = extract_keywords(all_content)

            # Count word frequencies
            word_freq = {}
            for word in keywords:
                if len(word) > 2:  # Skip very short words
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Store word frequencies
            self.db.insert_word_frequencies(word_freq)

            # Update top comments and likes
            # Sort posts by comments/likes and get top 10
            top_comments = sorted(posts, key=lambda x: x.get('comments', 0), reverse=True)[:10]
            top_likes = sorted(posts, key=lambda x: x.get('likes', 0), reverse=True)[:10]

            # Store in database
            self.db.insert_top_comments(top_comments, 'x')
            self.db.insert_top_likes(top_likes, 'x')

            logging.info("Analytics tables updated successfully")

        except Exception as e:
            logging.error(f"Error updating analytics tables: {e}")


def run_storage_consumer():
    """Main function to run the database storage consumer."""
    try:
        logging.info("Starting database storage consumer...")
        consumer = DatabaseStorageConsumer()

        # Process messages
        consumer.consume_messages(consumer.process_message, timeout_seconds=30)

        # Update analytics tables after processing all messages
        consumer.update_analytics_tables()

        logging.info(f"Database storage consumer finished. Processed {consumer.processed_count} messages.")

    except Exception as e:
        logging.error(f"Database storage consumer failed: {str(e)}")


if __name__ == '__main__':
    # Configure logging if needed
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Run the consumer
    run_storage_consumer()