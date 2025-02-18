from django.views.generic import ListView

from .models import Order
from .forms import OrderSearchForm
# from .mixins import WaiterRequiredMixin


class OrderListView(
    # WaiterRequiredMixin,
    ListView
):
    """
    OrderListView отображает постраничный список заказов для официантов.

    Атрибуты:
        model (Order): Модель, которую будет отображать этот вид.
        paginate_by (int): Количество заказов на странице.
        context_object_name (str): Имя переменной контекста для списка заказов.
    Методы:
        get_queryset():
            Возвращает набор запросов заказов, отфильтрованных по
                критериям формы поиска, если они предоставлены.
        get_context_data(**kwargs):
            Добавляет форму поиска в данные контекста.
    """

    model = Order
    paginate_by = 10
    context_object_name = 'orders'

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('order_items__dish')
        form = OrderSearchForm(self.request.GET)

        if form.is_valid():
            if table_number := form.cleaned_data.get('table_number'):
                qs = qs.filter(table_number=table_number)
            if status := form.cleaned_data.get('status'):
                qs = qs.filter(status=status)

        return qs

