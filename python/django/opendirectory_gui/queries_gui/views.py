# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import queries
import re
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import QueryForm


def index(request):
    template = loader.get_template('queries_gui/index.html')
    form = QueryForm()
    return render(request, 'queries_gui/index.html', {'form': form})


def search(request):
    form = QueryForm(request.POST)
    if form.is_valid():
        keywords_form = form.cleaned_data['keywords']
        keywords_form = re.sub("\s+", ",", keywords_form.strip())
        rows = form.cleaned_data['row_num']
        min_size = form.cleaned_data.get('min_size')
        max_size = form.cleaned_data.get('max_size')
        keywords_split = keywords_form.split(',')
        keywords_split = filter(None, keywords_split)
        keywords = [keyword.strip() for keyword in keywords_split]
        keywords_send = ''
        if len(keywords) > 1:
            i = 1
            for k in keywords[::-1]:
                keywords_send += k + '^' + str(i) + ' AND '
                i += 1
            keywords_send = keywords_send[:keywords_send.rfind('AND')]
        else:
            keywords_send = keywords[0]
        order = form.cleaned_data['order']
        results = queries.searchByKeywords(keywords_send, order, rows, min_size, max_size)
        template = loader.get_template('queries_gui/result.html')
        context = {
            'results': results,
        }
        return HttpResponse(template.render(context, request))
