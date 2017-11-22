# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import queries

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import QueryForm


'''
TODO:
- Ordenacion por relevancia, tamaño o fecha -> DONE
- Usar pesos -> DONE
- Implementar consultas (todas) -> 
- Añadir test de latencia y posición 
- Limitar numero de filas devueltas -> DONE
- Darle un poco de aspecto a la interfaz (??)
'''


def index(request):
    template = loader.get_template('queries_gui/index.html')
    form = QueryForm()
    return render(request, 'queries_gui/index.html', {'form': form})


def search(request):
    form = QueryForm(request.POST)
    if form.is_valid():
        keywords_form = form.cleaned_data['keywords']
        rows = form.cleaned_data['row_num']
        keywords = [keyword.strip() for keyword in keywords_form.split(',')]
        keywords_send = ''
        if len(keywords) > 1:
            i = 1
            for k in keywords[::-1]:
                keywords_send += 'id:*' + k + '*^' + str(i) + ' AND '
                i += 1
            keywords_send = keywords_send[:keywords_send.rfind('AND')]
        else:
            keywords_send = keywords[0]
        order = form.cleaned_data['order']
        results = queries.searchByKeywords(keywords_send, order, rows)
        template = loader.get_template('queries_gui/result.html')
        context = {
            'results': results,
        }
        return HttpResponse(template.render(context, request))
