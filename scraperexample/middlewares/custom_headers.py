import json
import random
from scrapy.http import Headers


class RandomizeFingerprintMiddleware:
    @classmethod
    def process_request(cls, request, spider):
        with open(spider.input_headers, 'r') as f:
            headers_json_list = json.load(f)

        request.headers = Headers(random.choice(headers_json_list))
