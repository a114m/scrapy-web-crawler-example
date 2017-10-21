from time import sleep
from os import getenv
import pika
import logging

logger = logging.getLogger(__name__)


class RabbitMQClient():
    def __init__(self):
        self.host_name = getenv('BROKER_HOST', 'localhost')
        self.port = int(getenv('BROKER_PORT', 5672))
        self.userid = getenv('BROKER_USERID', 'guest')
        self.password = getenv('BROKER_PASSWORD', 'guest')
        self.queue = getenv('BROKER_QUEUE', 'scraped_items')
        self.exchange = getenv('BROKER_EXCHANGE', '')
        self.credentials = pika.PlainCredentials(self.userid, self.password)
        self.connection_params = pika.ConnectionParameters(host=self.host_name, port=self.port, credentials=self.credentials)

        self._open_connection()

    def _open_connection(self):
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def start_consuming(self, callback):
        while True:
            try:
                self.channel.basic_consume(callback,
                                           queue=self.queue,
                                           no_ack=True)
                self.channel.start_consuming()
            except pika.exceptions.AMQPConnectionError as err:
                logger.error("Error occurred while connecting to RabbitMQ: %s" % err)
                logger.info("Trying to listen again in 3 seconds")
                sleep(3)
                self._open_connection()
