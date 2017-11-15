import scrapy
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

class DirectorySpider(scrapy.Spider):
    name = "directories"
    urls = 'urls.txt'
    with open(urls) as f:
        start_urls = f.readlines()
    start_urls = [x.strip() for x in start_urls]
    allowed_domains = [url.split("//")[-1].split("/")[0] for url in start_urls]
    print allowed_domains

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
        for link in links:
            if '..' not in link.url and link.url is not response.url:
                yield scrapy.Request(link.url, method="HEAD")
                yield scrapy.Request(link.url)
