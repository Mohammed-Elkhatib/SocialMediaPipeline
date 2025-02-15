from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import time


class BaseConsumer:
    def __init__(self, topic, group_id, bootstrap_servers='localhost:9092', auto_offset_reset='earliest'):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': auto_offset_reset
        })
        self.consumer.subscribe([topic])
        print(f"Subscribed to topic '{topic}' with group '{group_id}'.")

    def consume_messages(self, process_func, timeout_seconds=10):
        """
        Continuously polls Kafka for new messages and processes each message using the provided function.
        If no messages are received for timeout_seconds, the consumer stops.
        """
        start_time = time.time()
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg:
                    if not msg.error():
                        try:
                            # Decode and process the message
                            data = json.loads(msg.value().decode('utf-8'))
                            process_func(data)
                        except Exception as e:
                            print(f"Error processing message: {e}")
                        # Reset timeout counter on successful processing
                        start_time = time.time()
                    else:
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            print(f"End of partition reached: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")
                        else:
                            raise KafkaException(msg.error())
                # If no message is received within the timeout, break out.
                if time.time() - start_time > timeout_seconds:
                    print(f"No messages received for {timeout_seconds} seconds. Stopping consumer.")
                    break
        except KeyboardInterrupt:
            print("Consumer interrupted by user.")
        finally:
            self.consumer.close()
