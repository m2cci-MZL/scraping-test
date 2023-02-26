import click
from scrapy.crawler import CrawlerProcess
import json

from scrapy.utils.project import get_project_settings

from scraperexample.spiders.scraper import ScraperSpider


@click.command()
@click.option('--urls', help='path to start urls to crawl', default=None)
@click.option(
    '--concurrent_requests',
    help='number of desired requests to run in parallel',
    default=3,
)
@click.option('--headers', help='path to json file containing list of headers')
def crawl_spider(urls: str, concurrent_requests: int, headers: str):
    """
    :param urls: path to start urls to crawl
    :param concurrent_requests: number of desired requests to run in parallel
    :param headers: path to json file containing list of headers
    :return: None
    """
    if urls:
        with open(urls, 'r') as f:
            urls_list = json.load(f)['urls']
    else:
        return
    process = CrawlerProcess(
        settings={
            **get_project_settings(),
            'CONCURRENT_REQUESTS': concurrent_requests,
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 1,
        },
    )

    process.crawl(ScraperSpider, urls=urls_list, headers=headers)
    process.start()


if __name__ == '__main__':
    crawl_spider()
