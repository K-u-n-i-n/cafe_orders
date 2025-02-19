from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import OrderCreateForm, OrderItemFormSet, OrderSearchForm
from .models import Order

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


class OrderCreateView(
    # WaiterRequiredMixin,
    CreateView
):
    """
    OrderCreateView отображает форму для создания нового заказа.

    Атрибуты:
        model (Order): Модель, связанная с этим представлением.
        form_class (OrderCreateForm): Класс формы, используемый для
            создания заказа.
        template_name (str): Шаблон, используемый для отображения
            представления.
        success_url (str): URL для перенаправления после успешной отправки
            формы.
    Методы:
        get_context_data(**kwargs):
            Добавляет OrderItemFormSet в данные контекста.
        form_valid(form):
            Проверяет форму и formset, сохраняет заказ и его элементы,
                пересчитывает итоговую сумму, и отображает сообщение об
                успешном создании.
    """

    model = Order
    form_class = OrderCreateForm
    template_name = 'orders/order_create.html'
    success_url = reverse_lazy('orders:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = OrderItemFormSet(self.request.POST)
        else:
            context['formset'] = OrderItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            self.object.recalc_total()
            messages.success(self.request, 'Заказ успешно создан')
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))
