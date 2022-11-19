import json
import logging

from scrapy.commands import ScrapyCommand
from scrapy.utils.project import get_project_settings

from playwright.sync_api import sync_playwright
from pika import BlockingConnection

from utils import pika_connection_parameters


class DtekComparator(ScrapyCommand):
    def __init__(self):
        self.logger = logging.getLogger(name=self.__class__.__name__)
        self.settings = get_project_settings()
        self.init_playwright()
        self.init_rmq()

    def init_playwright(self):
        self.context_manager = sync_playwright().start()
        self.browser = self.context_manager.firefox.launch(headless=False)
        self.context = self.browser.new_context(user_agent=self.settings.get("USER_AGENT"))
        self.page = self.context.new_page()

    def init_rmq(self):
        self.connection = BlockingConnection(pika_connection_parameters())
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=self.settings.get("DTEK_QUEUE"),
            durable=True
        )
        self.channel.basic_consume(
            queue=self.settings.get("DTEK_QUEUE"),
            on_message_callback=self.on_message_callback,
            auto_ack=True 
        )

    def on_message_callback(self, channel, method, properties, body):
        message_body = json.loads(body)
        self.page.goto(message_body["url"], wait_until="load")

    def run(self, args, opts):
        self.logger.info("Start consuming messages from RMQ...")
        self.channel.start_consuming()
        self.browser.close()
        self.context_manager.stop()
