import argparse
import logging
import threading
from src.utils.logger import configure_logging
from src.scraper.core import scrape_twitter
from src.kafka.producer import KafkaSender
from src.kafka.consumers.storage import StorageConsumer
from src.kafka.consumers.stats import WordFrequencyConsumer, EngagementConsumer
from src.kafka.consumers.pipeline import run_pipeline


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


def run_stats_consumers():
    """Run the stats consumers to analyze the data."""
    logging.info("Starting stats consumers")

    try:
        # Run Word Frequency Consumer
        word_consumer = WordFrequencyConsumer()
        word_consumer.consume_messages(word_consumer.process_tweet, timeout_seconds=30)
        word_consumer.save_word_frequencies(top_n=20)

        # Run Engagement Metrics Consumer
        engagement_consumer = EngagementConsumer()
        engagement_consumer.consume_messages(engagement_consumer.process_tweet, timeout_seconds=30)
        engagement_consumer.save_engagement_metrics()

        logging.info("Stats consumers finished")
    except Exception as e:
        logging.error(f"Stats consumers failed: {str(e)}")


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Run the social media data pipeline')
    parser.add_argument('--username', '-u', default="LBCI_NEWS",
                        help='Twitter username to scrape (default: LBCI_NEWS)')
    parser.add_argument('--mode', '-m', choices=['scrape', 'consume', 'all', 'pipeline'], default='pipeline',
                        help='Mode to run: scrape, consume, pipeline, or all (default: all)')
    args = parser.parse_args()

    # Configure logging
    configure_logging()
    logging.info("Initializing pipeline")

    # Run in the specified mode
    if args.mode in ['scrape', 'pipeline', 'all']:
        run_scraper(args.username)

    if args.mode in ['consume', 'all']:
        # Start consumers in separate threads
        storage_thread = threading.Thread(target=run_storage_consumer)
        stats_thread = threading.Thread(target=run_stats_consumers)

        storage_thread.start()
        stats_thread.start()

        # Wait for consumers to finish
        storage_thread.join()
        stats_thread.join()

    if args.mode == 'pipeline':
        # Run the coordinated pipeline
        run_pipeline()

    logging.info("Pipeline run completed")


if __name__ == '__main__':
    main()
