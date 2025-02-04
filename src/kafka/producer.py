from confluent_kafka import Producer
import json
import logging
from src.config import Config


class KafkaSender:
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': Config.KAFKA_BROKER})
        self.topic = Config.KAFKA_TOPIC
        self.count = 0

    def send(self, message):
        try:
            self.producer.produce(
                self.topic,
                key=message['id'],
                value=json.dumps(message)
            )
            self.count += 1
            if self.count % 10 == 0:
                logging.info(f"Sent batch of 10 tweets (Total: {self.count})")

        except Exception as e:
            logging.error(f"Failed to send message: {str(e)}")

    def __del__(self):
        self.producer.flush()
        logging.info(f"Final count: {self.count} tweets sent")
