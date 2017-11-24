import urllib
import json
import datetime
import socket
import urllib2

BASE_URL = 'http://138.197.178.126:8983/solr/collection1/select?wt=json'
CONVERSION_RATE = 1024
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
OUTPUT_FORMAT = '%d %b %Y %H:%M:%S'

class QueryResult:
    def __init__(self, id, filename, creation_date, lastmodified, source,
                 content_length, content_type, ip, location, available):
        self.id = id
        self.filename = filename
        self.creation_date = creation_date
        self.lastmodified = lastmodified
        self.source = source
        self.content_length = content_length
        self.content_type = content_type
        self.ip = ip
        self.location = location
        self.available = available


class Domain:
    def __init__(self, name, ip, location, ping):
        self.name = name
        self.ip = ip
        self.location = location
        self.ping = ping

def checkHostStatus(host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host,80))
    if result == 0:
        return 'OK'
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host,443))
        if result == 0:
            return 'OK'
        else:
            return 'KO'

def getLocation(host):
    f = urllib2.urlopen('http://freegeoip.net/json/' + host)
    json_string = f.read()
    f.close()
    location = json.loads(json_string)
    location_city = location.get('city')
    location_state = location.get('region_name')
    location_country = location.get('country_name')
    if location_city.strip() and location_state.strip():
        return location_city + ", " + location_state + ", " + location_country 
    else:
        return location_country
            

def searchByKeywords(keywords, order, rows, min_size, max_size):
    domains = {}
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
        domain = file_url.split("//")[-1].split("/")[0]
        if domains.get(domain) is None:
            ip = socket.gethostbyname(domain)
            location = getLocation(ip)
            available = checkHostStatus(ip)
            domains[domain] = {'ip': ip, 'location': location, 'available': available}
        filename = file_url[file_url.rindex('/') + 1:]
        size = result.get('content-length') / (CONVERSION_RATE*CONVERSION_RATE)
        date = result.get('last-modified')
        if date is not None:
            last_modified = datetime.datetime.strptime(date,DATETIME_FORMAT).strftime(OUTPUT_FORMAT)
        else:
            last_modified = None
        domain_info = domains.get(domain)
        results.append(QueryResult(
            file_url, filename, result.get('date'),
            last_modified, result.get('source-server'),
            size, result.get('content-type'), domain_info.get('ip'), 
            domain_info.get('location'), domain_info.get('available')))
    return results
