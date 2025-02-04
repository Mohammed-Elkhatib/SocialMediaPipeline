import logging
from src.utils.logger import configure_logging
from src.scraper.core import scrape_twitter
from src.kafka.producer import KafkaSender


def main():
    configure_logging()
    logging.info("Initializing pipeline")
    sender = KafkaSender()
    try:
        scrape_twitter("ALJADEEDNEWS", sender)
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")


if __name__ == '__main__':
    main()
