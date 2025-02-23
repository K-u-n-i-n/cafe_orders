from decimal import Decimal

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from orders.models import CustomUser, Dish, Order, OrderItem


# Фикстуры для пользователей
@pytest.fixture
def admin_user(db):
    return CustomUser.objects.create_user(
        username='admin', password='password', role=CustomUser.ADMIN
    )


@pytest.fixture
def chef_user(db):
    return CustomUser.objects.create_user(
        username='chef', password='password', role=CustomUser.CHEF
    )


@pytest.fixture
def waiter_user(db):
    return CustomUser.objects.create_user(
        username='waiter', password='password', role=CustomUser.WAITER
    )


# Фикстуры для модели Dish
@pytest.fixture
def dish(db):
    return Dish.objects.create(name='Блюдо 1', price=Decimal('100.00'))


# Фикстура для Order
@pytest.fixture
def order(db, waiter_user):
    return Order.objects.create(table_number=1)


# Фикстура для OrderItem
@pytest.fixture
def order_item(db, order, dish):
    return OrderItem.objects.create(order=order, dish=dish, quantity=2)


# Тест пересчёта итоговой суммы заказа
def test_order_recalc_total(db, order, dish):
    # Ошибка: итоговая сумма не пересчитана правильно.
    order.order_items.all().delete()
    OrderItem.objects.create(order=order, dish=dish, quantity=3)
    order.recalc_total()
    assert order.total_price == dish.price * 3


# Тест срабатывания сигнала при сохранении OrderItem
def test_signal_order_total_on_save(db, order, dish):
    # Ошибка: сигнал post_save не обновил итоговую сумму заказа.
    order.order_items.all().delete()
    OrderItem.objects.create(order=order, dish=dish, quantity=4)
    order.refresh_from_db()
    assert order.total_price == dish.price * 4


# Тест срабатывания сигнала при удалении OrderItem
def test_signal_order_total_on_delete(db, order, dish):
    # Ошибка: после удаления OrderItem итоговая сумма не обнулилась.
    item = OrderItem.objects.create(order=order, dish=dish, quantity=5)
    order.refresh_from_db()
    item.delete()
    order.refresh_from_db()
    assert order.total_price == Decimal('0.00')


# Тест представления списка заказов
def test_order_list_view(db, client, waiter_user, order):
    client.force_login(waiter_user)
    url = reverse('orders:list')
    response = client.get(url)
    assert response.status_code == 200
    # Ошибка: список заказов не найден в контексте.
    assert 'orders' in response.context
    assert order in response.context['orders']


# Тест создания заказа через представление OrderCreateView
def test_order_create_view(db, client, waiter_user, dish):
    client.force_login(waiter_user)
    url = reverse('orders:create')
    data = {
        'table_number': '2',
        'order_items-TOTAL_FORMS': '1',
        'order_items-INITIAL_FORMS': '0',
        'order_items-MIN_NUM_FORMS': '0',
        'order_items-MAX_NUM_FORMS': '1000',
        'order_items-0-dish': dish.id,
        'order_items-0-quantity': '2',
    }
    response = client.post(url, data)
    # Ошибка: при корректном заполнении формы должно быть перенаправление.
    assert response.status_code == 302


# Тест удаления заказа через представление OrderDeleteView
def test_order_delete_view(db, client, admin_user, order):
    client.force_login(admin_user)
    url = reverse('orders:delete', args=[order.id])
    response = client.post(url)
    # Ошибка: заказ не был удалён или отсутствует перенаправление.
    assert response.status_code == 302
    assertRedirects(response, reverse('orders:list'))
    # Изменено ожидаемое сообщение на фактическое сообщение исключения Django.
    with pytest.raises(
        Order.DoesNotExist, match='Order matching query does not exist.'
    ):
        Order.objects.get(id=order.id)


# Тест обновления статуса заказа запрещённый для повара
def test_order_status_update_view_forbidden(db, client, chef_user, order):
    order.status = Order.PENDING
    order.save()
    client.force_login(chef_user)
    url = reverse('orders:update_status', args=[order.id])
    data = {'status': 'paid'}
    response = client.post(url, data)
    # Получение сообщений из запроса
    messages = list(get_messages(response.wsgi_request))
    expected_error = (
        'Вы не можете установить статус "Оплачено". Выберите другой.'
    )
    assert any(expected_error in m.message for m in messages)


# Тест изменения заказа через OrderUpdateView
def test_order_update_view(db, client, admin_user, order, dish):
    client.force_login(admin_user)
    url = reverse('orders:update', args=[order.id])
    data = {
        'table_number': '3',
        'order_items-TOTAL_FORMS': '1',
        'order_items-INITIAL_FORMS': '0',
        'order_items-MIN_NUM_FORMS': '0',
        'order_items-MAX_NUM_FORMS': '1000',
        'order_items-0-dish': dish.id,
        'order_items-0-quantity': '1',
    }
    response = client.post(url, data)
    # Ошибка: при обновлении заказа не происходит перенаправление
    # или данные не обновляются.
    assert response.status_code == 302
    order.refresh_from_db()
    assert order.table_number == 3


# Тест представления отчёта о доходах RevenueReportView
def test_revenue_report_view(db, client, admin_user, order, dish):
    client.force_login(admin_user)
    order.status = Order.PAID
    order.save()
    OrderItem.objects.create(order=order, dish=dish, quantity=2)
    order.recalc_total()
    url = reverse('orders:revenue')
    response = client.get(url)
    assert response.status_code == 200
    # Ошибка: отсутствуют данные о выручке в контексте шаблона.
    assert 'total_revenue' in response.context
    total_revenue = response.context['total_revenue']
    expected_total = dish.price * 2
    assert total_revenue == expected_total


# Переделанный тест фильтрации заказов
@pytest.mark.parametrize('table_number,status,expected_count', [
    ('1', Order.PENDING, 1),
    ('999', Order.PENDING, 0),
])
def test_order_search_filter(
    db, client, waiter_user, order, table_number, status, expected_count
):
    # Фикстура order не модифицируется - она имеет table_number=1
    # и status=PENDING
    client.force_login(waiter_user)
    url = reverse('orders:list')
    response = client.get(
        url, data={'table_number': table_number, 'status': status})
    # Оповещение: фильтрация заказов
    assert response.status_code == 200
    orders = response.context['orders']
    assert len(orders) == expected_count
