import django_filters

from orders.models import Order


class OrderFilter(django_filters.FilterSet):
    """Фильтр для модели заказа."""

    table_number = django_filters.NumberFilter(field_name='table_number')
    status = django_filters.ChoiceFilter(
        field_name='status', choices=Order.ORDER_STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['table_number', 'status']
