import os
from dotenv import load_dotenv


load_dotenv()

BOT_NAME = 'dtek'
SPIDER_MODULES = ['spiders']
COMMANDS_MODULE = "commands"
NEWSPIDER_MODULE = 'spiders'
ROBOTSTXT_OBEY = True
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
VISICOM_API_KEY = os.getenv("VISICOM_API_KEY", "")
CITY = os.getenv("CITY", "Київ")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "3306"))
RABBITMQ_VIRTUAL_HOST = os.getenv("RABBITMQ_VIRTUAL_HOST", "/dtek")
RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

DTEK_QUEUE = os.getenv("DTEK_QUEUE", "dtek_queue")
PLAYWRIGHT_HEADLESS = True if os.getenv("PLAYWRIGHT_HEADLESS", "True") == "True" else False

ALPHABET = [
    "а", "б", "в", "г", "ґ", "д", "е", "є", "ж", "з", "и", "і",
    "ї", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у",
    "ф", "х", "ц", "ч", "ш", "щ", "ь", "ю", "я"
]
