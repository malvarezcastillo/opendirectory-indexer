import scrapy
import re
import requests
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

class DirectorySpider(scrapy.Spider):
    name = "directories"
    urls = 'urls.txt'
    with open(urls) as f:
        start_urls = f.readlines()
    start_urls = [x.strip() for x in start_urls]
    allowed_domains = [url.split("//")[-1].split("/")[0] for url in start_urls]

    rules = [
        Rule(
            LinkExtractor(
                canonicalize=True,
                unique=True
            ),
            follow=True,
            callback="parse"
        )
    ]

    def allowedcontenttype(self, content_type):
        allowed_content_types = ['text/plain', 'text/html']
        for t in allowed_content_types:
            if re.search(t, content_type, re.IGNORECASE):
                return True
        return False

    def parse(self, response):
        content_type = response.headers['Content-Type']
        yield {
                'url_to': response.url,
                'headers': response.headers,
                'content_type' : content_type
        }

        if self.allowedcontenttype(content_type):
            links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
            for link in links:
                if '..' not in link.url and link.url is not response.url:
                    yield scrapy.Request(link.url)
                    yield scrapy.Request(link.url, method="HEAD")
