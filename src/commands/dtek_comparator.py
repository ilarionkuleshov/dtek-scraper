import json
import logging

from datetime import datetime as dt
from urllib.parse import parse_qsl

from scrapy.commands import ScrapyCommand
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter

from playwright.sync_api import sync_playwright
from pika import BlockingConnection

from utils import pika_connection_parameters


class DtekComparator(ScrapyCommand):
    def __init__(self):
        super(DtekComparator, self).__init__()
        self.decorate_run()

    def init(self):
        self.logger = logging.getLogger(name=self.__class__.__name__)
        self.settings = get_project_settings()
        self.alphabet = self.settings.get("ALPHABET")
        self.file_path = f"data/{dt.now().strftime('%d_%m_%Y_%H_%M_%S')}.jl"
        self.init_playwright()
        self.init_rmq()

    def init_playwright(self):
        self.context_manager = sync_playwright().start()
        self.browser = self.context_manager.firefox.launch(
            headless=self.settings.get("PLAYWRIGHT_HEADLESS")
        )
        self.context = self.browser.new_context(user_agent=self.settings.get("USER_AGENT"))
        self.page = self.context.new_page()
        self.page.goto("https://www.dtek-kem.com.ua/ua/shutdowns", wait_until="load")

    def init_rmq(self):
        self.connection = BlockingConnection(pika_connection_parameters())
        self.channel = self.connection.channel()
        self.channel.queue_declare(
            queue=self.settings.get("DTEK_QUEUE"),
            durable=True
        )

    def dtek_compare(self, message_body):
        self.logger.info(f"Comparing street: {message_body['street_variations']}")
        foreign_addresses = []
        present_addresses = []
        for variation in message_body["street_variations"]:
            try:
                street = self.format_street(variation, message_body["type"])
                self.page.click("input[id='street']")
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Backspace")
                self.page.type("input[id='street']", street)
                div_locator = self.page.locator(f"""xpath=//div[@id="streetautocomplete-list"]/div[strong[contains(text(), "{street}")]]""")
                if div_locator.count():
                    div_locator = div_locator.first
                    input_value = div_locator.locator("xpath=input[@type='hidden']").input_value()
                    div_locator.click()
                    with self.page.expect_response("https://www.dtek-kem.com.ua/ua/ajax") as response_info:
                        response = response_info.value
                        street_post_value = None
                        for data in parse_qsl(response.request.post_data):
                            if data[0] == "data[0][value]":
                                street_post_value = data[1]
                                break
                        if input_value == street_post_value:
                            response_data = response.json().get("data")
                            if response_data:
                                addresses = list(response_data.keys())
                                present_addresses += addresses
            except Exception as e:
                self.logger(e)
        if len(present_addresses):
            present_addresses = list(dict.fromkeys(present_addresses))
            present_addresses = [self.format_address(address) for address in present_addresses]
            for address in message_body["addresses"]:
                if not self.format_address(address) in present_addresses:
                    foreign_addresses.append(address)
        if len(foreign_addresses):
            foreign_addresses = list(dict.fromkeys(foreign_addresses))
            self.write_to_file(
                {
                    "street": self.street_from_variations(
                        message_body["street_variations"],
                        message_body["type"]
                    ),
                    "addresses": ", ".join(foreign_addresses)
                }
            )

    def format_street(self, street, street_type):
        street = street.lower()
        street_parts = street.split(" ")
        street_num = None
        street_letter = None
        for part in street_parts:
            if part[0].isdigit():
                street_num = part
            elif part in self.alphabet:
                street_letter = part
        if street_num:
            street_parts.remove(street_num)
            street_num = "".join([sym for sym in street_num if sym.isdigit()])
        if street_letter:
            street_parts.remove(street_letter)
        street = " ".join(street_parts)
        if street_num:
            street += f" {street_num}"
        if street_letter:
            street += street_letter
        if street_type == "пл.":
            street_type = "площа"
        elif street_type == "узвіз":
            street_type = "узв."
        street = f"{street_type} {street}"
        return street

    def format_address(self, address):
        address = address.lower()
        address_split = address.split("/")
        if len(address_split) == 2 and address_split[1] in self.alphabet:
            address = "".join(address_split)
        return address

    def write_to_file(self, item):
        with open(self.file_path, "a") as file:
            line = json.dumps(ItemAdapter(item).asdict()) + "\n"
            file.write(line)

    def run(self, args, opts):
        self.logger.info("Start consuming messages from RMQ...")
        for method_frame, properties, body in self.channel.consume(
            self.settings.get("DTEK_QUEUE"),
            inactivity_timeout=15
        ):
            if body:
                message_body = json.loads(body)
                self.dtek_compare(message_body)
                self.channel.basic_ack(method_frame.delivery_tag)
        self.connection.close()
        self.browser.close()
        self.context_manager.stop()

    def decorate_run(self):
        def decorator(function):
            def wrapper(*args, **kwargs):
                self.init()
                return function(*args, **kwargs)
            return wrapper
        self.run = decorator(self.run)

    @staticmethod
    def street_from_variations(street_variations, street_type):
        street = street_variations.pop(0)
        if len(street_variations):
            other_variations = ", ".join(street_variations)
            street += f" {other_variations}"
        street = f"{street_type} {street}"
        return street
