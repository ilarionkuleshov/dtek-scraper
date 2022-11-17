import json

from scrapy import Request, signals
from scrapy.exceptions import DontCloseSpider

from pika import BlockingConnection
from utils import pika_connection_parameters


class RMQConsumerMiddleware:
    def __init__(self, crawler):
        self.spider = crawler.spider
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.connection = BlockingConnection(pika_connection_parameters())
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=spider.consume_queue,
            durable=True
        )
        self.channel.basic_consume(
            queue=spider.consume_queue,
            on_message_callback=self.on_message_callback,
            auto_ack=True
        )
        self.channel.start_consuming()

    def on_message_callback(self, channel, method, properties, body):
        message_body = json.loads(body)
        next_message_out = self.spider.next_message(message_body)
        if self.crawler.crawling and isinstance(next_message_out, Request):
            self.crawler.engine.crawl(next_message_out, spider=self.spider)

    def spider_idle(self, spider):
        raise DontCloseSpider

    def spider_closed(self, spider):
        self.connection.close()
