from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.views.generic.edit import FormView

from .forms import (
    AdminUserCreationForm,
    OrderCreateForm,
    OrderItemFormSet,
    OrderSearchForm,
    OrderStatusForm,
)
from .mixins import (
    AdminRequiredMixin,
    ChefOrAdminRequiredMixin,
    WaiterOrAdminRequiredMixin,
)
from .models import CustomUser, Order


class OrderListView(
    LoginRequiredMixin,
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
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Order.ORDER_STATUS_CHOICES
        return context

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
    LoginRequiredMixin,
    WaiterOrAdminRequiredMixin,
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
        else:
            for error in formset.non_form_errors():
                error_text = str(error).replace('dish', 'Блюдо')
                messages.error(self.request, error_text)
            return self.render_to_response(self.get_context_data(form=form))


class OrderDeleteView(
    LoginRequiredMixin,
    AdminRequiredMixin,
    DeleteView
):
    """
    OrderDeleteView отвечает за удаление заказов.

    Атрибуты:
        model (Order): Модель, с которой работает представление.
        success_url (str): URL, на который будет перенаправлен пользователь
            после успешного удаления заказа.
    Методы:
        delete(request, *args, **kwargs): Обрабатывает запрос на удаление
            заказа, выводит сообщение об успешном удалении и вызывает метод
            delete родительского класса.
    """

    model = Order
    success_url = reverse_lazy('orders:list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Заказ успешно удален')
        return super().delete(request, *args, **kwargs)


class OrderStatusUpdateView(
    LoginRequiredMixin,
    ChefOrAdminRequiredMixin,
    UpdateView
):
    """
    OrderStatusUpdateView отвечает за обновление статуса заказа.

    Атрибуты:
        model (Order): Модель, с которой работает представление.
        form_class (OrderStatusForm): Форма для обновления статуса заказа.
        template_name (str): Путь к шаблону, используемому для отображения
            формы.
        success_url (str): URL, на который будет перенаправлен пользователь
            после успешного обновления статуса заказа.
    Методы:
        form_valid(self, form): Проверяет, что повар не может установить
            статус "Оплачен". Если попытка есть — возвращает ошибку.
            Обрабатывает успешное обновление формы.
    """

    model = Order
    form_class = OrderStatusForm
    template_name = 'orders/order_status_form.html'
    success_url = reverse_lazy('orders:list')

    def form_valid(self, form):
        new_status = form.cleaned_data['status']

        if self.request.user.is_chef and new_status == 'paid':
            messages.error(
                self.request,
                'Вы не можете установить статус "Оплачено". Выберите другой.'
            )
            return self.form_invalid(form)
        messages.success(self.request, 'Статус заказа обновлен')
        return super().form_valid(form)


class OrderUpdateView(
    LoginRequiredMixin,
    AdminRequiredMixin,
    UpdateView
):
    """
    OrderUpdateView отображает форму для изменения заказа.

    Атрибуты:
        model (Order): Модель заказа.
        form_class (OrderCreateForm): Форма для изменения заказа.
        template_name (str): Шаблон для отображения формы.
        success_url (str): URL перенаправления после успешного обновления.

    Методы:
        get_context_data(**kwargs):
            Добавляет OrderItemFormSet в контекст.
        form_valid(form):
            Проверяет валидность формы и formset, сохраняет заказ и его
                элементы, пересчитывает итоговую сумму и выводит сообщение
                об успешном обновлении.
    """

    model = Order
    form_class = OrderCreateForm
    template_name = 'orders/order_update.html'
    success_url = reverse_lazy('orders:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = OrderItemFormSet(
                self.request.POST, instance=self.object)
        else:
            context['formset'] = OrderItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            self.object.recalc_total()  # пересчёт итоговой суммы
            messages.success(self.request, 'Заказ успешно обновлен')
            return super().form_valid(form)
        else:
            for error in formset.non_form_errors():
                error_text = str(error).replace('dish', 'Блюдо')
                messages.error(self.request, error_text)
            return self.render_to_response(self.get_context_data(form=form))


class RevenueReportView(
    LoginRequiredMixin,
    AdminRequiredMixin,
    TemplateView
):
    """
    Представление для отчета о доходах.

    Атрибуты:
        template_name (str): Имя шаблона, используемого для отображения отчета
            о доходах.
    Методы:
        get_context_data(**kwargs): Получает контекстные данные для шаблона,
            включая общую сумму дохода.
    """

    template_name = 'orders/revenue_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = Order.objects.filter(
            status=Order.PAID).aggregate(total=Sum('total_price'))
        context['total_revenue'] = total['total'] or 0
        return context


class AdminCreateUserView(
    LoginRequiredMixin,
    AdminRequiredMixin,
    FormView,
):
    """
    Отвечает за создание нового пользователя администратором.

    Атрибуты:
        template_name (str): Имя шаблона, используемого для отображения формы
            создания пользователя.
        form_class (AdminUserCreationForm): Класс формы, используемый для
            создания пользователя.
        success_url (str): URL для перенаправления после успешного создания
            пользователя.

    Методы:
        form_valid(self, form):
            Обрабатывает успешное создание формы, создает нового пользователя
                и отображает сообщение об успешном создании.
    """

    template_name = 'registration/admin_create_user.html'
    form_class = AdminUserCreationForm
    success_url = reverse_lazy('orders:admin_create_user')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        role = form.cleaned_data['role']
        user = CustomUser(username=username, role=role)
        user.set_password(password)
        user.save()
        messages.success(
            self.request, f'Пользователь {username} успешно создан.')
        return super().form_valid(form)


def page_not_found(request, exception):
    """Страница 404"""

    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Страница 500"""

    return render(request, 'pages/500.html', status=500)
