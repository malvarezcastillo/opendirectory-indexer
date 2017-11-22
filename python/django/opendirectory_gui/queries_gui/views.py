# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib
import json
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import QueryForm


'''
TODO:
- Ordenacion por relevancia, tamaño o fecha
- Implementar consultas (todas)
- Añadir test de latencia y posición 
- Limitar numero de filas devueltas
- Darle un poco de aspecto a la interfaz (??)
'''


class QueryResult:
    def __init__(self, id, creation_date, lastmodified, source,
                 content_length, content_type):
        self.id = id
        self.creation_date = creation_date
        self.lastmodified = lastmodified
        self.source = source
        self.content_length = content_length
        self.content_type = content_type


def index(request):
    template = loader.get_template('queries_gui/index.html')
    form = QueryForm()
    return render(request, 'queries_gui/index.html', {'form': form})


def search(request):
    url = "http://localhost:8983/solr/collection1/select?q=*%3A*&wt=json&indent=true"
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    results = []
    for result in data['response']['docs']:
        results.append(QueryResult(
            result.get('id'), result.get('date'),
            result.get('last-modified'), result.get('source-server'),
            result.get('content-length'), result.get('content-type')))
    template = loader.get_template('queries_gui/result.html')
    context = {
        'results': results,
    }
    return HttpResponse(template.render(context, request))
