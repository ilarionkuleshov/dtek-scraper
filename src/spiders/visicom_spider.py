import json

from scrapy import Spider, Request
from scrapy.utils.project import get_project_settings


class VisicomSpider(Spider):
    name = "visicom"
    alphabet = [
        "а", "б", "в", "г", "ґ", "д", "е", "є", "ж", "з", "и", "і",
        "ї", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у",
        "ф", "х", "ц", "ч", "ш", "щ", "ь", "ю", "я"
    ]
    custom_settings = {
        "ITEM_PIPELINES": {
            "pipelines.RMQPublisherPipeline": 800
        }
    }

    def __init__(self):
        super(VisicomSpider, self).__init__()
        self.settings = get_project_settings()
        self.publish_queue = self.settings.get("DTEK_QUEUE")

    def start_requests(self):
        for letter in self.alphabet:
            yield Request(
                url=f"https://api.visicom.ua/data-api/5.0/uk/geocode.json?categories=adr_street&text={self.settings.get('CITY')}, {letter}&key={self.settings.get('VISICOM_API_KEY')}",
                callback=self.parse_visicom_streets
            )
            break

    def parse_visicom_streets(self, response):
        response_json = json.loads(response.text)
        features = response_json.get("features")
        if features:
            for feature in features:
                if feature["properties"]["settlement_type"] == "місто" and \
                feature["properties"]["settlement"] == self.settings.get("CITY") and \
                feature["properties"]["categories"] == "adr_street":
                    for street in self.street_variations(feature["properties"]["name"]):
                        yield Request(
                            url=f"https://api.visicom.ua/data-api/4.0/uk/search/adr_address.json?text={street}&key={self.settings.get('VISICOM_API_KEY')}",
                            callback=self.parse_visicom_addresses
                        )
                        return

    def parse_visicom_addresses(self, response):
        response_json = json.loads(response.text)
        features = response_json.get("features")
        addresses = {}
        if features:
            for feature in features:
                if feature["properties"]["settlement_type"] == "місто" and \
                feature["properties"]["settlement"] == self.settings.get("CITY") and \
                feature["properties"]["categories"] == "adr_address":
                    street = feature["properties"]["street"]
                    address = feature["properties"]["name"]
                    if street in addresses:
                        if not address in addresses[street]:
                            addresses[street].append(address)
                    else:
                        addresses[street] = [address]
        for address in addresses:
            yield {
                "street_variations": self.street_variations(address),
                "addresses": addresses[address]
            }

    @staticmethod
    def street_variations(street):
        street_variations = []
        if "(" in street and ")" in street:
            street_variations.append(street.split("(")[0].strip())
            street_variations.append(street.split("(")[1].split(")")[0].strip())
        else:
            street_variations.append(street)
        return street_variations
