from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import os
from collections import Counter
import pandas as pd
from process import extract_keywords
import time

# Paths and Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_FOLDER, exist_ok=True)
WORD_FREQ_FILE = os.path.join(DATA_FOLDER, 'word_frequencies.json')
ENGAGEMENT_FILE = os.path.join(DATA_FOLDER, 'tweets_engagement.json')

# Base Kafka Consumer Class
class BaseConsumer:
    def __init__(self, topic, group_id):
        self.consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([topic])

    def consume_messages(self, process_func, timeout_seconds=10):
        start_time = time.time()
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg and not msg.error():
                    process_func(json.loads(msg.value().decode('utf-8')))
                    start_time = time.time()  # Reset timer on new message
                elif time.time() - start_time > timeout_seconds:
                    print(f"No messages received for {timeout_seconds} seconds. Stopping.")
                    break
        except KeyboardInterrupt:
            print("Consumer interrupted.")
        finally:
            self.consumer.close()


# Word Frequency Consumer Class
class WordFrequencyConsumer(BaseConsumer):
    def __init__(self):
        super().__init__('social-media-data', 'word-frequency-group')
        self.word_counts = Counter()

    def process_tweet(self, tweet):
        keywords = extract_keywords(tweet['content'])
        self.word_counts.update(keywords)

    def save_word_frequencies(self, top_n=20):
        word_freq_data = [{'word': w, 'count': c} for w, c in self.word_counts.most_common(top_n)]
        with open(WORD_FREQ_FILE, 'w', encoding='utf-8') as wf:
            json.dump(word_freq_data, wf, ensure_ascii=False, indent=4)
        print(f"Top {top_n} word frequencies saved to {WORD_FREQ_FILE}")


# Engagement Metrics Consumer Class
class EngagementConsumer(BaseConsumer):
    def __init__(self):
        super().__init__('social-media-data', 'engagement-group')
        self.engagement_data = []

    def process_tweet(self, tweet):
        if {'id', 'likes', 'comments', 'retweets'}.issubset(tweet):
            self.engagement_data.append(tweet)

    def save_engagement_metrics(self):
        df = pd.DataFrame(self.engagement_data)
        engagement_summary = {
            'top_likes': df.nlargest(10, 'likes').to_dict(orient='records'),
            'top_comments': df.nlargest(10, 'comments').to_dict(orient='records'),
            'top_retweets': df.nlargest(10, 'retweets').to_dict(orient='records')
        }
        with open(ENGAGEMENT_FILE, 'w', encoding='utf-8') as ef:
            json.dump(engagement_summary, ef, ensure_ascii=False, indent=4)
        print(f"Engagement metrics saved to {ENGAGEMENT_FILE}")


word_consumer = WordFrequencyConsumer()
word_consumer.consume_messages(word_consumer.process_tweet, timeout_seconds=10)
word_consumer.save_word_frequencies(top_n=20)

engagement_consumer = EngagementConsumer()
engagement_consumer.consume_messages(engagement_consumer.process_tweet, timeout_seconds=10)
engagement_consumer.save_engagement_metrics()
print("Done")