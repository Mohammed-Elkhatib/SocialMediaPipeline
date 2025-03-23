import argparse
import logging
import threading
import time
from confluent_kafka import Consumer, KafkaException
from src.utils.logger import configure_logging
from src.scraper.core import scrape_twitter
from src.kafka.producer import KafkaSender
from src.kafka.consumers.storage import StorageConsumer


def run_scraper(username):
    """Run the Twitter scraper for a specific username."""
    logging.info(f"Starting Twitter scraper for @{username}")

    # Initialize the Kafka producer
    sender = KafkaSender()

    # Run the scraper
    try:
        scrape_twitter(username, sender)
        logging.info(f"Scraping completed for @{username}")
    except Exception as e:
        logging.error(f"Scraping failed: {str(e)}")


def run_storage_consumer():
    """Run the storage consumer to persist data to the database."""
    logging.info("Starting storage consumer")

    try:
        storage_consumer = StorageConsumer()
        storage_consumer.consume_messages(storage_consumer.process_message)
        logging.info("Storage consumer finished")
    except Exception as e:
        logging.error(f"Storage consumer failed: {str(e)}")


def wait_for_kafka_data(topic, bootstrap_servers, group_id="polling_group", timeout=30, poll_interval=2):
    """
    Waits for data to be available in Kafka before starting the consumer.
    """
    print(f"⏳ Waiting for data in Kafka topic '{topic}' (Timeout: {timeout}s)...")

    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'latest',
        'enable.auto.commit': False
    }

    consumer = Consumer(conf)
    consumer.subscribe([topic])

    start_time = time.time()
    while time.time() - start_time < timeout:
        msg = consumer.poll(timeout=1.0)  # Poll Kafka
        if msg is not None and msg.error() is None:
            print("✅ Data detected in Kafka! Starting consumer...")
            consumer.close()
            return True  # Exit immediately when data is found
        time.sleep(poll_interval)

    print("⚠️ No data received within timeout. Starting consumer anyway.")
    consumer.close()
    return False  # If no data is found within the timeout, start consumer anyway


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Run the social media data pipeline')
    parser.add_argument('--username', '-u', default="ALJADEEDNEWS",
                        help='Twitter username to scrape (default: ALJADEEDNEWS)')
    parser.add_argument('--mode', '-m', choices=['scrape', 'consume', 'all'], default='all',
                        help='Mode to run: scrape, consume, or all (default: all)')
    args = parser.parse_args()

    # Configure logging
    configure_logging()
    logging.info("Initializing pipeline")

    # Run in the specified mode
    scraper_thread = None

    # Run scraper in a separate thread
    if args.mode in ['scrape', 'all']:
        scraper_thread = threading.Thread(target=run_scraper, args=(args.username,))
        scraper_thread.start()

    # Run consumer
    if args.mode in ['consume', 'all']:
        if 'all' in args.mode:
            wait_for_kafka_data(topic="social-media-data", bootstrap_servers="localhost:9092")

        print("🟢 Starting consumer...")
        storage_thread = threading.Thread(target=run_storage_consumer)
        storage_thread.start()
        storage_thread.join()

    # Ensure scraper thread finishes before exiting (if it was started)
    if scraper_thread:
        scraper_thread.join()


if __name__ == '__main__':
    main()
