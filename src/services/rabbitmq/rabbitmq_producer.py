# src/services/rabbitmq/rabbitmq_producer.py

import sys
import os
import time
import pika
import json
import threading
from services.logger.base_logger import BaseLogger
from config import config

RABBITMQ_CONFIG = config.get("actions.rabbitmq")

logger = BaseLogger("rabbitmq")

def load_mq_config_parameters():
    rabbitmq_config = RABBITMQ_CONFIG

    rabbitmq_username = rabbitmq_config['username']
    rabbitmq_password = rabbitmq_config['password']
    rabbitmq_host = rabbitmq_config['host']
    rabbitmq_port = int(rabbitmq_config['port'])

    logger.info(f"Connecting to RabbitMQ with username: {rabbitmq_username}, host: {rabbitmq_host}, port: {rabbitmq_port}")

    credentials = pika.PlainCredentials(username=rabbitmq_username, password=rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        credentials=credentials
    )

    return parameters

class MQClient:
    def __init__(self, parameters):
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='request_queue', durable=True)
        self.channel.queue_declare(queue='response_queue', durable=True)

    def close(self):
        if self.connection.is_open:
            self.connection.close()

class BlockingMQClient(MQClient):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.process = None

    def set_process(self, process):
        self.process = process

    def process_request(self, ch, method, props, body):
        data_rev = body.decode('utf-8')
        logger.info(f"Recv: {data_rev}")
        resp = self.process(data_rev)
        self.send_response(resp, props.correlation_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_response(self, response, correlation_id):
        self.channel.basic_publish(exchange='',
                                   routing_key='response_queue',
                                   properties=pika.BasicProperties(correlation_id=correlation_id),
                                   body=response)
        logger.info(f"Sent: {response}")

    def listen_for_requests(self):
        try:
            self.channel.basic_consume(queue='request_queue',
                                       on_message_callback=self.process_request)
            logger.info('Waiting for requests...')
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info('Interrupt received, stopping...')
        finally:
            self.connection.close()

class NoneBlockingMQClient(BlockingMQClient):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.lock = threading.Lock()

    def fetch_one_msg(self, queue_name):
        with self.lock:
            method_frame, header_frame, body = self.channel.basic_get(queue=queue_name, auto_ack=False)
            if method_frame:
                data_rev = body.decode('utf-8')
                logger.info(f"Queue has message: {data_rev}")
                return data_rev
            else:
                logger.info("Queue is empty.")
                return None

    def send_one_msg(self, queue_name, message):
        with self.lock:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent message
                )
            )
            logger.info(f"Send msg: {message}")
            return True

    def poll_and_process(self, process_callback, timeout=30):
        start_time = time.time()
        while True:
            with self.lock:
                response = self.fetch_one_msg('response_queue')
                if response:
                    process_callback(response)
                if time.time() - start_time > timeout:
                    logger.error("Polling timeout.")
                    return

            time.sleep(1)

# Main function to control execution
def blocking_test():
    parameters = load_mq_config_parameters()
    client = BlockingMQClient(parameters)

    def append(data):
        return f"The resp to '{data}' is 'resp' : 'ack' ".encode('utf-8')

    try:
        client.set_process(append)
        client.listen_for_requests()
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        client.close()
        logger.info("Connection closed")


def non_blocking_test():
    parameters = load_mq_config_parameters()
    client = NoneBlockingMQClient(parameters)
    try:
        while True:
            if client.fetch_one_msg('request_queue'):
                client.send_one_msg("response_queue", "done")
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        client.close()
        logger.info("Connection closed")
