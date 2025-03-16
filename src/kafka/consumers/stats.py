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
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
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
            self.logger.warning(f"Tweet missing 'content' field: {tweet}")

    def save_word_frequencies(self, top_n=None):
        """
        Save the word frequencies to both a JSON file and the database.
        If top_n is specified, only the top N words will be saved to JSON.
        All words are saved to the database for comprehensive analytics.
        """
        if not self.word_counts:
            self.logger.warning("No word frequency data collected to save.")
            return

        # For JSON file, optionally limit to top N words
        words_to_save = self.word_counts.most_common(top_n) if top_n else self.word_counts.items()
        word_freq_data = [{'word': word, 'count': count} for word, count in words_to_save]

        with open(WORD_FREQ_FILE, 'w', encoding='utf-8') as wf:
            json.dump(word_freq_data, wf, ensure_ascii=False, indent=4)

        msg = f"Top {top_n} word frequencies saved to {WORD_FREQ_FILE}" if top_n else f"All word frequencies saved to {WORD_FREQ_FILE}"
        self.logger.info(msg)

        # Save all words to database - using improved batch processing method
        self.tweet_model.insert_word_frequencies(dict(self.word_counts))
        self.logger.info(f"Word frequencies saved to database: {len(self.word_counts)} words processed")


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
        required_fields = {'id', 'likes', 'comments', 'retweets', 'date', 'time', 'content'}

        if required_fields.issubset(tweet.keys()):
            # Ensure the post exists in the database first to avoid foreign key issues
            try:
                # Map the fields to match our database schema
                self.tweet_model.insert_post(
                    post_id=tweet['id'],
                    post_date=tweet['date'],
                    post_time=tweet['time'],
                    content=tweet['content'],
                    likes=tweet['likes'],
                    retweets=tweet['retweets'],
                    comments=tweet['comments']
                )
                # Add to engagement data for later aggregation
                self.engagement_data.append(tweet)
            except Exception as e:
                self.logger.error(f"Failed to insert post {tweet.get('id', 'unknown')}: {str(e)}")
        else:
            missing = required_fields - set(tweet.keys())
            self.logger.warning(f"Tweet missing required fields {missing}: {tweet}")

    def save_engagement_metrics(self, top_n=10):
        """
        Aggregate the engagement data to find top tweets by likes, comments, and retweets,
        then save to JSON and database.
        """
        if not self.engagement_data:
            self.logger.warning("No engagement data collected to save.")
            return

        df = pd.DataFrame(self.engagement_data)

        # Prepare data format for database submission
        likes_data = df.nlargest(top_n, 'likes')[['id', 'likes']].to_dict(orient='records')
        comments_data = df.nlargest(top_n, 'comments')[['id', 'comments']].to_dict(orient='records')
        retweets_data = df.nlargest(top_n, 'retweets')[['id', 'retweets']].to_dict(orient='records')

        # Create summaries for JSON file
        engagement_summary = {
            'top_likes': df.nlargest(top_n, 'likes').to_dict(orient='records'),
            'top_comments': df.nlargest(top_n, 'comments').to_dict(orient='records'),
            'top_retweets': df.nlargest(top_n, 'retweets').to_dict(orient='records')
        }

        # Save to JSON file
        with open(ENGAGEMENT_FILE, 'w', encoding='utf-8') as ef:
            json.dump(engagement_summary, ef, ensure_ascii=False, indent=4)
        self.logger.info(f"Engagement metrics saved to {ENGAGEMENT_FILE}")

        # Save to database using updated methods
        self.tweet_model.update_top_likes(likes_data)
        self.tweet_model.update_top_comments(comments_data)
        self.tweet_model.update_top_retweets(retweets_data)
        self.logger.info(f"Top {top_n} engagement metrics saved to database")


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
    engagement_consumer.save_engagement_metrics(top_n=10)

    logger.info("Stats processing completed.")
