import urllib
import json

BASE_URL = 'http://138.197.178.126:8983/solr/collection1/select?wt=json'


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


def searchByKeywords(keywords, order, rows):
    url = BASE_URL + '&rows=' + str(rows) + "&q=" + keywords
    if order == 'date':
        url += "&sort=last-modified+desc"
    elif order == 'size':
        url += "&sort=content-length+desc"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    results = []
    for result in data['response']['docs']:
        file_url = result.get('id')
        filename = file_url[file_url.rindex('/') + 1:]
        results.append(QueryResult(
            file_url, filename, result.get('date'),
            result.get('last-modified'), result.get('source-server'),
            result.get('content-length'), result.get('content-type')))
    return results
