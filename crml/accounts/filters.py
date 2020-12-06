import django_filters
from django_filters import DateFilter, CharFilter
from .models import *

class OrderFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='date_created',lookup_expr='gte')
    #Above gives records which having date >= entered date

    end_date = DateFilter(field_name='date_created',lookup_expr='lte')
    #Above gives records which having date >= entered date

    note = CharFilter(field_name='note', lookup_expr='icontains')
    class Meta:
        model = Order
        #fields = ['product','status']
        fields = '__all__'
        exclude = ['customer','date_created']