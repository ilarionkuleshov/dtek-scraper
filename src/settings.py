import os
from dotenv import load_dotenv


load_dotenv()

BOT_NAME = 'dtek'
SPIDER_MODULES = ['spiders']
NEWSPIDER_MODULE = 'spiders'
ROBOTSTXT_OBEY = True
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
VISICOM_API_KEY = os.getenv("VISICOM_API_KEY", "")
CITY = os.getenv("CITY", "Київ")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "3306"))
RABBITMQ_VIRTUAL_HOST = os.getenv("RABBITMQ_VIRTUAL_HOST", "/dtek")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

DTEK_QUEUE = os.getenv("DTEK_QUEUE", "dtek_queue")
