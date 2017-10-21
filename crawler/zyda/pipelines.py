# -*- coding: utf-8 -*-

from scrapy import signals
from scrapy.utils.serialize import ScrapyJSONEncoder
from scrapy.xlib.pydispatch import dispatcher
from scrapy.exceptions import DropItem
from time import sleep
import pika
import logging

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class RabbitMQPipeline(object):
    def __init__(self, host_name, port, userid, password, encoder_class, queue, exchange):
        self.encoder = encoder_class()
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.host_name = host_name
        self.port = port
        self.userid = userid
        self.password = password
        self.encoder_class = encoder_class
        self.queue = queue
        self.exchange = exchange

    @classmethod
    def from_settings(cls, settings):
        host_name = settings.get('BROKER_HOST')
        port = settings.get('BROKER_PORT')
        userid = settings.get('BROKER_USERID')
        password = settings.get('BROKER_PASSWORD')
        encoder_class = settings.get('MESSAGE_Q_SERIALIZER', ScrapyJSONEncoder)
        queue = settings.get('BROKER_QUEUE')
        exchange = settings.get('BROKER_EXCHANGE')
        return cls(host_name, port, userid, password, encoder_class, queue, exchange)

    def spider_opened(self, spider):
        credentials = pika.PlainCredentials(self.userid, self.password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_name, port=self.port, credentials=credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def spider_closed(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        count = 0
        while count < 3:
            count += 1
            try:
                success = self.channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.queue,
                    body=self.encoder.encode(dict(item))
                )
            except Exception as err:
                logging.error("Exception while connecting to RabbitMQ to post item: %s" % err)
                logging.warning("Trying to initialize RabbitMQ connection again")
                self.spider_opened(spider)
                continue
            if success:
                logging.info("Successfully posted item to pipeline")
                return item
            else:
                if count < 3:
                    logging.warning("Sleeping for 2 sec and trying to post item to RabbitMQ again")
                    sleep(2)

        raise DropItem("Failed to post item to pipeline, exceeded number of tries: " % item)
