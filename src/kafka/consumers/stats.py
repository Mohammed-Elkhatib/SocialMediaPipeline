import os
import json
from collections import Counter
import pandas as pd
import logging
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


class WordFrequencyConsumer(BaseConsumer):
    def __init__(self):
        # Subscribe to the topic with its own consumer group for word frequency stats
        super().__init__(Config.KAFKA_TOPIC, 'word-frequency-group')
        self.word_counts = Counter()
        self.tweet_model = TweetModel()
        self.logger = logging.getLogger(__name__)

    def process_tweet(self, tweet):
        """
        Extract keywords from the tweet content and update the internal word frequency counter.
        """
        if 'content' in tweet:
            keywords = extract_keywords(tweet['content'])
            self.word_counts.update(keywords)
        else:
            self.logger.warning("Tweet missing 'content' field:", tweet)

    def save_word_frequencies(self, top_n=20):
        """
        Save the top N word frequencies to both a JSON file and the database.
        """
        # Convert Counter to dictionary for top N words
        top_words = dict(self.word_counts.most_common(top_n))

        # Save to JSON file
        word_freq_data = [{'word': word, 'count': count} for word, count in top_words.items()]
        with open(WORD_FREQ_FILE, 'w', encoding='utf-8') as wf:
            json.dump(word_freq_data, wf, ensure_ascii=False, indent=4)
        self.logger.info(f"Top {top_n} word frequencies saved to {WORD_FREQ_FILE}")

        # Save to database
        self.tweet_model.insert_word_frequencies(top_words)
        self.logger.info(f"Word frequencies saved to database")


class EngagementConsumer(BaseConsumer):
    def __init__(self):
        # Subscribe to the topic with its own consumer group for engagement stats
        super().__init__(Config.KAFKA_TOPIC, 'engagement-group')
        self.engagement_data = []
        self.tweet_model = TweetModel()
        self.logger = logging.getLogger(__name__)

    def process_tweet(self, tweet):
        """
        Check that the tweet contains necessary engagement fields and store it for later aggregation.
        """
        if {'id', 'likes', 'comments', 'retweets', 'date', 'time', 'content'}.issubset(tweet.keys()):
            self.engagement_data.append(tweet)
        else:
            self.logger.warning("Tweet missing one or more required fields:", tweet)

    def save_engagement_metrics(self):
        """
        Aggregate the engagement data to find top tweets by likes, comments, and retweets,
        then save to JSON and database.
        """
        if self.engagement_data:
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

            # Save to database
            platform = 'x'  # Hardcoded for now
            self.tweet_model.insert_top_likes(engagement_summary['top_likes'], platform)
            self.tweet_model.insert_top_comments(engagement_summary['top_comments'], platform)
            self.logger.info("Top engagement metrics saved to database")
        else:
            self.logger.warning("No engagement data collected to save.")


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run Word Frequency Consumer
    logger = logging.getLogger(__name__)
    logger.info("Starting Word Frequency Consumer...")
    word_consumer = WordFrequencyConsumer()
    word_consumer.consume_messages(word_consumer.process_tweet, timeout_seconds=10)
    word_consumer.save_word_frequencies(top_n=20)

    # Run Engagement Metrics Consumer
    logger.info("Starting Engagement Metrics Consumer...")
    engagement_consumer = EngagementConsumer()
    engagement_consumer.consume_messages(engagement_consumer.process_tweet, timeout_seconds=10)
    engagement_consumer.save_engagement_metrics()

    logger.info("Stats processing completed.")
