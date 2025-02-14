"""from confluent_kafka import Consumer, KafkaException, KafkaError
import json
from process import analyze_sentiment, extract_keywords
#from database import save_to_db
from collections import Counter
import time
import json
import os
# Get the absolute path to the project root (adjust if necessary)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

# Ensure the data folder exists
DATA_FOLDER = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

# Define the file path
WORD_FREQ_FILE = os.path.join(DATA_FOLDER, "word_frequencies.json")

total_word_count = Counter()

# Kafka Consumer setup
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'social-media-group',
    'auto.offset.reset': 'earliest'
})

# Subscribe to the topic
consumer.subscribe(['social-media-data'])


# After processing all tweets, save the word frequency data as JSON
def save_top_word_frequencies(word_counts, filename=WORD_FREQ_FILE, top_n=10):
    word_freq_data = [{"word": word, "count": count} for word, count in word_counts.most_common(top_n)]

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(word_freq_data, f, ensure_ascii=False, indent=4)

    print(f"Top {top_n} word frequencies saved to {filename}")

print("Listening for messages from Kafka...")

# Set a maximum timeout for inactivity (e.g., 60 seconds)
inactivity_timeout = 10  # in seconds
last_message_time = time.time()  # track when the last message was received


try:
    while True:
        msg = consumer.poll(1.0)  # Timeout after 1 second

        if msg is None:
            # No message available within timeout
            if time.time() - last_message_time > inactivity_timeout:
                print("No new messages for a while. Stopping the consumer.")
                break  # Exit the loop after inactivity timeout
            continue
        elif msg.error():
            # Error handling
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition
                print(f"End of partition reached: {msg.topic} [{msg.partition}] @ {msg.offset}")
            else:
                raise KafkaException(msg.error())
        else:
            # Successfully received a message
            tweet = json.loads(msg.value().decode('utf-8'))
            print(f"Received Tweet: {tweet}")
            #tweet['sentiment'] = analyze_sentiment(tweet['content'])
            keywords = extract_keywords(tweet['content'])
            #print(f"Extracted keywords: {keywords}")

            # Only update counter if keywords are found
            if keywords:
                total_word_count.update(keywords)
                #print(f"Updated word count: {total_word_count}")
            else:
                print("No keywords extracted from this tweet.")

            # Reset last_message_time to current time
            last_message_time = time.time()

        # Save to the database
            #save_to_db(tweet)

except KeyboardInterrupt:
    print("Consumer interrupted")
finally:
    #print(f"Word Frequencies Across All Tweets: {total_word_count}")
    most_frequent = total_word_count.most_common(10)
    #print(f"Most Frequent Words: {most_frequent}")
    # Close the consumer when done
    consumer.close()
    # Convert to dictionary and save
    save_top_word_frequencies(total_word_count, WORD_FREQ_FILE, top_n=20)
"""
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import os
import time
import pandas as pd
from collections import Counter
from process import analyze_sentiment, extract_keywords

# Paths and Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_FOLDER, exist_ok=True)
WORD_FREQ_FILE = os.path.join(DATA_FOLDER, 'word_frequencies.json')
ENGAGEMENT_FILE = os.path.join(DATA_FOLDER, 'tweets_engagement.json')

# Kafka Consumer Setup
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'social-media-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(['social-media-data'])

# Engagement and Word Counters
total_word_count = Counter()
engagement_data = []

# Time Limit Configuration
inactivity_timeout = 10  # seconds
last_message_time = time.time()

# Save Word Frequencies
def save_word_frequencies(counter):
    data = [{'word': w, 'count': c} for w, c in counter.most_common(20)]
    with open(WORD_FREQ_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Save Engagement Metrics
def save_engagement_metrics(tweets):
    df = pd.DataFrame(tweets)
    if not df.empty:
        df['total_engagement'] = df['likes'] + df['comments'] + df['retweets']
        top_tweets = df.sort_values(by='total_engagement', ascending=False).head(20)
        top_tweets.to_json(ENGAGEMENT_FILE, orient='records', force_ascii=False, indent=4)

print("Listening for messages from Kafka...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            if time.time() - last_message_time > inactivity_timeout:
                print("No new messages for a while. Stopping the consumer.")
                break
        elif not msg.error():
            tweet = json.loads(msg.value().decode('utf-8'))
            keywords = extract_keywords(tweet['content'])
            engagement_data.append(tweet)
            total_word_count.update(keywords)
            last_message_time = time.time()
except KeyboardInterrupt:
    print("Interrupted. Saving results...")
finally:
    consumer.close()
    save_word_frequencies(total_word_count)
    save_engagement_metrics(engagement_data)
    print("Data saved. Exiting.")
