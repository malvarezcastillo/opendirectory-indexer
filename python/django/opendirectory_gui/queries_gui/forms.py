from django import forms
import datetime


class QueryForm(forms.Form):
    keywords = forms.CharField(
        label='Search files using keywords (comma-separated, order by relevance) ', max_length=1024)
    min_size = forms.IntegerField(
        label='Smallest size (in MiB) ', min_value=0, required=False)
    max_size = forms.IntegerField(
        label='Biggest size (in MiB) ', min_value=0, required=False)
    order = forms.ChoiceField(label='Order by ',
                              choices=[("relevance", "Relevance"),
                                       ("size", "Size"),
                                       ("date", "Date")])
    row_num = forms.IntegerField(
            label='Max number of results ', initial=10, min_value=10,
            required=True)
