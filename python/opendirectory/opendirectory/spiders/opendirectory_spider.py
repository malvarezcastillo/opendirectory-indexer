import scrapy
import re
import datetime
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
        UNKNOWN_TYPE = 'unknown'
        SERVER_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
        content_type = response.headers.get('Content-Type', UNKNOWN_TYPE)
        date_header = response.headers.get('Date')
        lastmodified_header = response.headers.get('Last-Modified')
        date = None
        lastmodified = None
        if date_header is not None:
            date = datetime.datetime.strptime(date_header, SERVER_DATE_FORMAT).strftime(DATETIME_FORMAT)
        if lastmodified_header is not None:
            lastmodified = datetime.datetime.strptime(lastmodified_header, SERVER_DATE_FORMAT).strftime(DATETIME_FORMAT)

        yield {
                #'headers': response.headers,
                'url_to': response.url,
                'content_type' : content_type,
                'date' : date,
                'source_server' : response.headers.get('Server', UNKNOWN_TYPE),
                'content_length' : response.headers.get('Content-Length', 0),
                'last_modified' : lastmodified
        }

        if self.allowedcontenttype(content_type):
            links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
            for link in links:
                if '..' not in link.url and link.url is not response.url:
                    yield scrapy.Request(link.url)
                    yield scrapy.Request(link.url, method="HEAD")
