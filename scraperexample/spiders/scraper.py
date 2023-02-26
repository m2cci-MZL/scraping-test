import html
import json
import re

from scrapy import Spider
from scrapy.exceptions import StopDownload
from scrapy.http import Request
from scrapy.http import Response


class ScraperSpider(Spider):
    name = 'scraper'

    def __init__(
        self,
        headers: str | None,
        urls: list[str],
        *args,
        **kwargs,
    ):
        """
        headers: path to json file containing list of headers
        urls: path to start urls to crawl
        """
        super(ScraperSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls
        self.input_headers = headers

    def start_requests(self):
        for url in self.start_urls:
            yield Request(
                # a high number of pages so we'll have all
                url=url,
                method='GET',
                callback=self.parse_gallery_details,
            )

    def parse_gallery_details(self, response: Response):
        resp_json = json.loads(
            response.css(
                '#wix-warmup-data::text',
            ).extract_first(),
        )
        offers: list[dict] = []
        offers_count: int = 0
        for gallery in resp_json['appsWarmupData'].values():
            for catalog in gallery.values():
                products_meta_with_data = catalog['catalog']['category'][
                    'productsWithMetaData'
                ]
                offers = products_meta_with_data['list']
                offers_count = products_meta_with_data['totalCount']

        assert len(offers), offers_count
        for offer in offers:
            yield Request(
                url=f"https://www.bearspace.co.uk/product-page/{offer['urlPart']}",
                method='GET',
                callback=self.parse,
                cb_kwargs={'offer': offer},
            )

    # The parsing could be easier with the api, but I'd prefer to write little bit of code and avoid dealing with
    # cookies and ban
    def parse(self, response: Response, offer: dict):
        resp_json = json.loads(
            response.css(
                '#wix-warmup-data::text',
            ).extract_first(),
        )
        detailed_offer: dict = next(iter(resp_json['appsWarmupData'].values()))[
            f"productPage_GBP_{offer['urlPart']}"
        ]['catalog']['product']
        media = [
            m
            for m in re.split(
                r'<\\?&?.*?>', html.unescape(detailed_offer['description']),
            )
            if m and not m.isdigit()
        ]
        height, width, media_details = self.parse_media(media)
        yield {
            'url': response.url,
            'data': {
                'title': offer['name'],
                'media': media_details,
                'height_cm': height,
                'width_cm': width,
                'price_gb': offer['price'],
            },
        }

    @staticmethod
    def parse_media(media: list[str]):
        height, width, media_details = None, None, None
        dim_index = 0
        for i, m in enumerate(media):
            if 'diam' in m.lower():
                height = width = re.findall(r'(\d+[\.|,]?\d?)[cm]?', m)[0]
                dim_index = i
                break
            try:
                parsed_dim = re.findall(r'(\d+\.?\d?)[cm]?', m)
                if len(parsed_dim) > 2:
                    height, width, _ = parsed_dim
                else:
                    height, width = parsed_dim
            except (ValueError, IndexError):
                continue
            if height and width:
                dim_index = i
                break
        # the needed data is either in the first or second element
        media_details = media[0 if dim_index == 1 else 1]
        if not height or not width or not media_details:
            raise StopDownload()
        return height, width, media_details
