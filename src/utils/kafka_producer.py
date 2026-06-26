import json
import os
import logging
from confluent_kafka import Producer

logger = logging.getLogger(__name__)

# Cache the producer instance
_producer_instance = None

def get_kafka_producer():
    global _producer_instance
    if _producer_instance is None:
        broker_url = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
        try:
            _producer_instance = Producer({
                'bootstrap.servers': broker_url
            })
            logger.info(f"Kafka producer initialized with broker: {broker_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
    return _producer_instance

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def publish_draft_event(message_payload: dict):
    """
    Publishes a message to the draft creation Kafka topic.
    """
    topic = os.getenv("KAFKA_DRAFT_TOPIC", "rti_closure_topic")
    producer = get_kafka_producer()
    
    if producer is None:
        logger.error("Cannot publish message: Kafka producer is not initialized.")
        return False
        
    try:
        json_payload = json.dumps(message_payload).encode('utf-8')
        producer.produce(
            topic=topic,
            value=json_payload,
            callback=delivery_report
        )
        producer.poll(0)
        return True
    except Exception as e:
        logger.error(f"Failed to publish Kafka message: {e}")
        return False
