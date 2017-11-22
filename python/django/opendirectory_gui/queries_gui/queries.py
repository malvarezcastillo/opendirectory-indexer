import urllib
import json
import datetime

BASE_URL = 'http://138.197.178.126:8983/solr/collection1/select?wt=json'
CONVERSION_RATE = 1024
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
OUTPUT_FORMAT = '%d %b %Y %H:%M:%S'

class QueryResult:
    def __init__(self, id, filename, creation_date, lastmodified, source,
                 content_length, content_type):
        self.id = id
        self.filename = filename
        self.creation_date = creation_date
        self.lastmodified = lastmodified
        self.source = source
        self.content_length = content_length
        self.content_type = content_type


def searchByKeywords(keywords, order, rows, min_size, max_size):
    url = BASE_URL + '&rows=' + str(rows) + "&q=" + keywords
    if order == 'date':
        url += "&sort=last-modified+desc"
    elif order == 'size':
        url += "&sort=content-length+desc"
    if min_size is not None and max_size is not None:
        url += "&fq=content-length:[" + \
            str(min_size*CONVERSION_RATE) + " TO " + str(max_size*CONVERSION_RATE) + "]"
    elif min_size is not None:
        url += "&fq=content-length:[" + str(min_size*CONVERSION_RATE) + " TO *]"
    elif max_size is not None:
        url += "&fq=content-length:[* TO " + str(max_size*CONVERSION_RATE) + "]"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    results = []
    for result in data['response']['docs']:
        file_url = result.get('id')
        filename = file_url[file_url.rindex('/') + 1:]
        size = result.get('content-length') / (CONVERSION_RATE*CONVERSION_RATE)
        date = result.get('last-modified')
        if date is not None:
            last_modified = datetime.datetime.strptime(date,DATETIME_FORMAT).strftime(OUTPUT_FORMAT)
        else:
            last_modified = None
        results.append(QueryResult(
            file_url, filename, result.get('date'),
            last_modified, result.get('source-server'),
            size, result.get('content-type')))
    return results
