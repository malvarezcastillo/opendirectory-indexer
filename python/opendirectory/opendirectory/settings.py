# -*- coding: utf-8 -*-

# Scrapy settings for opendirectory project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'opendirectory'

SPIDER_MODULES = ['opendirectory.spiders']
NEWSPIDER_MODULE = 'opendirectory.spiders'


USER_AGENT = 'opendirectory indexer'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 32

ITEM_PIPELINES = {
    'scrapysolr.SolrPipeline' : 100,
}

SOLR_URL = 'http://138.197.178.126:8983/solr/'
SOLR_MAPPING = {
  'id': 'url_to',
  'date': 'date',
  'content-type': 'content_type',
  'content-length': 'content_length',
  'last-modified': 'last_modified',
  'source-server': 'source_server'
}
SOLR_IGNORE_DUPLICATES = True
SOLR_DUPLICATES_KEY_FIELDS = ['id']

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
DEPTH_STATS_VERBOSE = True
DEPTH_LIMIT = 0 
DOWNLOAD_TIMEOUT = 15
DOWNLOAD_MAXSIZE = 1048576
