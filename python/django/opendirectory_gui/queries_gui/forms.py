from django import forms
import datetime


class QueryForm(forms.Form):
    keywords = forms.CharField(
        label='Search files using keywords (comma-separated, order by relevance) ', max_length=1024)
    init_date = forms.DateField(
        label='Starting date ', required=False)
    end_date = forms.DateField(
        label='End date ', required=False)
    min_size = forms.IntegerField(
        label='Smallest size (in MiB) ', min_value=0, required=False)
    max_size = forms.IntegerField(
        label='Biggest size (in MiB) ', min_value=0, required=False)
