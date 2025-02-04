from confluent_kafka import Consumer, KafkaException, KafkaError
import json

# Kafka Consumer setup
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'social-media-group',
    'auto.offset.reset': 'earliest'
})

# Subscribe to the topic
consumer.subscribe(['social-media-data'])

print("Listening for messages from Kafka...")

try:
    while True:
        msg = consumer.poll(1.0)  # Timeout after 1 second

        if msg is None:
            # No message available within timeout
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
except KeyboardInterrupt:
    print("Consumer interrupted")
finally:
    # Close the consumer when done
    consumer.close()
