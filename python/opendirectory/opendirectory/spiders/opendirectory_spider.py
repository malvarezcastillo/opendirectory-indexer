import scrapy
from scrapy.linkextractor import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

class ScraperItem(scrapy.Item):
    # The source URL
    url_from = scrapy.Field()
    # The destination URL
    url_to = scrapy.Field()

class DirectorySpider(scrapy.Spider):
    name = "directories"
    urls = 'urls.txt'
    with open(urls) as f:
        start_urls = f.readlines()
    start_urls = [x.strip() for x in start_urls]
    allowed_domains = start_urls

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
        items = []
        # Only extract canonicalized and unique links (with respect to the current page)
        links = LinkExtractor(canonicalize=True, unique=True).extract_links(response)
        # Now go through all the found links
        for link in links:
            # Check whether the domain of the URL of the link is allowed; so whether it is in one of the allowed domains
            is_allowed = False
            for allowed_domain in self.allowed_domains:
                if allowed_domain in link.url:
                    is_allowed = True
            # If it is allowed, create a new item and add it to the list of found items
            if is_allowed and '..' not in link.url and link.url is not response.url:
                item = ScraperItem()
                item['url_from'] = response.url
                item['url_to'] = link.url
                items.append(item)
        # Return all the found items
        return items
