from pika import ConnectionParameters
from pika.credentials import PlainCredentials

from scrapy.utils.project import get_project_settings


def pika_connection_parameters():
    settings = get_project_settings()
    return ConnectionParameters(
        host=settings.get("RABBITMQ_HOST"),
        port=settings.get("RABBITMQ_PORT"),
        virtual_host=settings.get("RABBITMQ_VIRTUAL_HOST"),
        credentials=PlainCredentials(
            username=settings.get("RABBITMQ_USERNAME"),
            password=settings.get("RABBITMQ_PASSWORD")
        )
    )
