from pika import BlockingConnection
from scrapy.utils.serialize import ScrapyJSONEncoder

from utils import pika_connection_parameters


class RMQPublisherPipeline:
    def __init__(self):
        self.json_encoder = ScrapyJSONEncoder()

    def open_spider(self, spider):
        self.connection = BlockingConnection(pika_connection_parameters())
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=spider.publish_queue,
            durable=True
        )

    def process_item(self, item, spider):
        self.channel.basic_publish(
            exchange="",
            routing_key=spider.publish_queue,
            body=self.json_encoder.encode(item)
        )
        return item

    def close_spider(self, spider):
        self.connection.close()
