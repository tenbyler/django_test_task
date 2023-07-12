import django_filters
from .models import Task
from django_filters.widgets import RangeWidget


# This file contains the filter logic. django_filters library handles it
class CreationFilter(django_filters.FilterSet):
    date_field = django_filters.DateFromToRangeFilter(field_name='date_posted', 
                                                      widget=RangeWidget(attrs={'type': 'date', 
                                                                                'class': 'form-control',}))
    class Meta:
        model = Task
        fields = ['date_posted']


class CompletionFilter(django_filters.FilterSet):
    date_field = django_filters.DateFromToRangeFilter(field_name='date_completed', 
                                                      widget=RangeWidget(attrs={'type': 'date', 
                                                                                'class': 'form-control',}))
    class Meta:
        model = Task
        fields = ['date_posted']