import scrapy
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

class DirectorySpider(scrapy.Spider):
    name = "directories"
    urls = 'urls.txt'
    with open(urls) as f:
        start_urls = f.readlines()
    start_urls = [x.strip() for x in start_urls]

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


    def parse(self, response):
        yield {
                'url_to': response.url,
                'headers': response.headers
        }
        
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        # Now go through all the found links
        for link in links:
            if '..' not in link.url and link.url is not response.url:
                yield scrapy.Request(link.url, method="HEAD")
                yield scrapy.Request(link.url)
