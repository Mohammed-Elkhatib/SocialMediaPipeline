import os
import json
from collections import Counter
import pandas as pd
from base import BaseConsumer
from src.utils.data_helpers import extract_keywords  # Ensure this function is available and correctly extracts keywords from text

# Paths and Directories Setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_FOLDER, exist_ok=True)
WORD_FREQ_FILE = os.path.join(DATA_FOLDER, 'word_frequencies.json')
ENGAGEMENT_FILE = os.path.join(DATA_FOLDER, 'tweets_engagement.json')


class WordFrequencyConsumer(BaseConsumer):
    def __init__(self):
        # Subscribe to the same topic with its own consumer group for word frequency stats
        super().__init__('social-media-data', 'word-frequency-group')
        self.word_counts = Counter()

    def process_tweet(self, tweet):
        """
        Extract keywords from the tweet content and update the internal word frequency counter.
        """
        if 'content' in tweet:
            keywords = extract_keywords(tweet['content'])
            self.word_counts.update(keywords)
        else:
            print("Tweet missing 'content' field:", tweet)

    def save_word_frequencies(self, top_n=20):
        """
        Save the top N word frequencies to a JSON file.
        """
        word_freq_data = [{'word': word, 'count': count} for word, count in self.word_counts.most_common(top_n)]
        with open(WORD_FREQ_FILE, 'w', encoding='utf-8') as wf:
            json.dump(word_freq_data, wf, ensure_ascii=False, indent=4)
        print(f"Top {top_n} word frequencies saved to {WORD_FREQ_FILE}")


class EngagementConsumer(BaseConsumer):
    def __init__(self):
        # Subscribe to the same topic with its own consumer group for engagement stats
        super().__init__('social-media-data', 'engagement-group')
        self.engagement_data = []

    def process_tweet(self, tweet):
        """
        Check that the tweet contains necessary engagement fields and store it for later aggregation.
        """
        if {'id', 'likes', 'comments', 'retweets'}.issubset(tweet.keys()):
            self.engagement_data.append(tweet)
        else:
            print("Tweet missing one or more engagement fields:", tweet)

    def save_engagement_metrics(self):
        """
        Aggregate the engagement data to find top tweets by likes, comments, and retweets, then save to JSON.
        """
        if self.engagement_data:
            df = pd.DataFrame(self.engagement_data)
            engagement_summary = {
                'top_likes': df.nlargest(10, 'likes').to_dict(orient='records'),
                'top_comments': df.nlargest(10, 'comments').to_dict(orient='records'),
                'top_retweets': df.nlargest(10, 'retweets').to_dict(orient='records')
            }
            with open(ENGAGEMENT_FILE, 'w', encoding='utf-8') as ef:
                json.dump(engagement_summary, ef, ensure_ascii=False, indent=4)
            print(f"Engagement metrics saved to {ENGAGEMENT_FILE}")
        else:
            print("No engagement data collected to save.")


if __name__ == '__main__':
    # Run Word Frequency Consumer
    print("Starting Word Frequency Consumer...")
    word_consumer = WordFrequencyConsumer()
    word_consumer.consume_messages(word_consumer.process_tweet, timeout_seconds=10)
    word_consumer.save_word_frequencies(top_n=20)

    # Run Engagement Metrics Consumer
    print("Starting Engagement Metrics Consumer...")
    engagement_consumer = EngagementConsumer()
    engagement_consumer.consume_messages(engagement_consumer.process_tweet, timeout_seconds=10)
    engagement_consumer.save_engagement_metrics()

    print("Stats processing completed.")
