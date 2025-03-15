import os
import json
import logging
import threading
from collections import Counter
import pandas as pd
from src.kafka.consumers.base import BaseConsumer
from src.utils.data_helpers import extract_keywords
from src.models.relational.tweets import TweetModel
from src.config import Config

# Paths and Directories Setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_FOLDER, exist_ok=True)
WORD_FREQ_FILE = os.path.join(DATA_FOLDER, 'word_frequencies.json')
ENGAGEMENT_FILE = os.path.join(DATA_FOLDER, 'tweets_engagement.json')


class StorageConsumer(BaseConsumer):
    def __init__(self):
        """Initialize the storage consumer with its own consumer group."""
        super().__init__(Config.KAFKA_TOPIC, 'storage-consumer-group')
        self.tweet_model = TweetModel()
        self.logger = logging.getLogger(__name__)
        self.processed_tweets = set()  # Track processed tweet IDs

    def process_message(self, message):
        """
        Process a message from Kafka and store it in the database.

        Args:
            message (dict): The message from Kafka containing tweet data
        """
        if not message:
            self.logger.warning("Received empty message, skipping")
            return

        try:
            # Extract tweet data from the message
            tweet_id = message.get('id')

            # Skip if we've already processed this tweet
            if tweet_id in self.processed_tweets:
                return

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

            # Mark as processed
            self.processed_tweets.add(tweet_id)
            self.logger.info(f"Stored tweet {tweet_id} from {date} {time}")

        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)


class WordFrequencyConsumer(BaseConsumer):
    def __init__(self, shared_message_store=None):
        # Subscribe to the topic with its own consumer group for word frequency stats
        super().__init__(Config.KAFKA_TOPIC, 'word-frequency-group')
        self.word_counts = Counter()
        self.tweet_model = TweetModel()
        self.logger = logging.getLogger(__name__)
        self.shared_message_store = shared_message_store or []
        self._lock = threading.Lock()

    def process_message(self, message):
        """
        Extract keywords from the tweet content and update the internal word frequency counter.
        """
        if not message:
            return

        try:
            # Store in shared message store for other consumers if provided
            if self.shared_message_store is not None:
                with self._lock:
                    self.shared_message_store.append(message)

            # Extract and count keywords
            if 'content' in message:
                keywords = extract_keywords(message['content'])
                self.word_counts.update(keywords)
            else:
                self.logger.warning("Tweet missing 'content' field:", message)
        except Exception as e:
            self.logger.error(f"Error processing message for word frequency: {e}", exc_info=True)

    def save_word_frequencies(self, top_n=20):
        """
        Save the top N word frequencies to both a JSON file and the database.
        """
        try:
            # Convert Counter to dictionary for top N words
            top_words = dict(self.word_counts.most_common(top_n))

            # Skip if no words were processed
            if not top_words:
                self.logger.warning("No words to save in frequencies")
                return

            # Save to JSON file
            word_freq_data = [{'word': word, 'count': count} for word, count in top_words.items()]
            with open(WORD_FREQ_FILE, 'w', encoding='utf-8') as wf:
                json.dump(word_freq_data, wf, ensure_ascii=False, indent=4)
            self.logger.info(f"Top {top_n} word frequencies saved to {WORD_FREQ_FILE}")

            # Save to database
            self.tweet_model.insert_word_frequencies(top_words)
            self.logger.info(f"Word frequencies saved to database")
        except Exception as e:
            self.logger.error(f"Error saving word frequencies: {e}", exc_info=True)


class EngagementConsumer(BaseConsumer):
    def __init__(self, shared_message_store=None):
        # Subscribe to the topic with its own consumer group for engagement stats
        super().__init__(Config.KAFKA_TOPIC, 'engagement-group')
        self.engagement_data = []
        self.tweet_model = TweetModel()
        self.logger = logging.getLogger(__name__)
        self.shared_message_store = shared_message_store

    def process_messages_from_store(self):
        """Process messages from the shared store instead of consuming directly"""
        if not self.shared_message_store:
            self.logger.warning("No messages in shared store to process")
            return

        for message in self.shared_message_store:
            self.process_message(message)

    def process_message(self, message):
        """
        Check that the tweet contains necessary engagement fields and store it for later aggregation.
        """
        if not message:
            return

        try:
            if {'id', 'likes', 'comments', 'retweets', 'date', 'time', 'content'}.issubset(message.keys()):
                self.engagement_data.append(message)
            else:
                self.logger.warning(f"Tweet missing one or more required fields: {message}")
        except Exception as e:
            self.logger.error(f"Error processing message for engagement: {e}", exc_info=True)

    def save_engagement_metrics(self):
        """
        Aggregate the engagement data to find top tweets by likes, comments, and retweets,
        then save to JSON and database.
        """
        try:
            if not self.engagement_data:
                self.logger.warning("No engagement data collected to save.")
                return

            df = pd.DataFrame(self.engagement_data)

            # Create summaries by engagement type
            engagement_summary = {
                'top_likes': df.nlargest(10, 'likes').to_dict(orient='records'),
                'top_comments': df.nlargest(10, 'comments').to_dict(orient='records'),
                'top_retweets': df.nlargest(10, 'retweets').to_dict(orient='records')
            }

            # Save to JSON file
            with open(ENGAGEMENT_FILE, 'w', encoding='utf-8') as ef:
                json.dump(engagement_summary, ef, ensure_ascii=False, indent=4)
            self.logger.info(f"Engagement metrics saved to {ENGAGEMENT_FILE}")

            # Save to database - only after storage consumer has finished
            platform = 'x'  # Hardcoded for now
            self.tweet_model.insert_top_likes(engagement_summary['top_likes'], platform)
            self.tweet_model.insert_top_comments(engagement_summary['top_comments'], platform)
            self.logger.info("Top engagement metrics saved to database")
        except Exception as e:
            self.logger.error(f"Error saving engagement metrics: {e}", exc_info=True)


def run_pipeline():
    """Run the entire pipeline with coordinated consumers"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Create a shared message store for all consumers
    shared_messages = []

    # Step 1: Run Storage Consumer to ensure data is stored first
    logger.info("Starting Storage Consumer...")
    storage_consumer = StorageConsumer()
    # Use a longer timeout to ensure we process enough messages
    storage_consumer.consume_messages(storage_consumer.process_message, timeout_seconds=30)
    logger.info("Storage Consumer finished.")

    # Step 2: Run Word Frequency Consumer
    logger.info("Starting Word Frequency Consumer...")
    word_consumer = WordFrequencyConsumer(shared_messages)
    word_consumer.consume_messages(word_consumer.process_message, timeout_seconds=30)
    word_consumer.save_word_frequencies(top_n=20)

    # Step 3: Run Engagement Metrics Consumer using the shared messages
    logger.info("Starting Engagement Metrics Consumer...")
    engagement_consumer = EngagementConsumer(shared_messages)
    # Process from shared store instead of consuming directly
    engagement_consumer.process_messages_from_store()
    engagement_consumer.save_engagement_metrics()

    logger.info("Pipeline run completed")
