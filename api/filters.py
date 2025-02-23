from django_filters import rest_framework as filters

from orders.models import Order


class OrderFilter(filters.FilterSet):
    """Фильтр для модели заказа."""

    table_number = filters.NumberFilter(field_name='table_number')
    status = filters.ChoiceFilter(
        field_name='status',
        choices=Order.ORDER_STATUS_CHOICES
    )

    class Meta:
        model = Order
        fields = ['table_number', 'status']
