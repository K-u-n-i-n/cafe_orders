from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from orders.models import CustomUser, Dish, Order, OrderItem


# Фикстура для API-клиента
@pytest.fixture
def api_client():
    return APIClient()


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


# Фикстура для блюда
@pytest.fixture
def dish(db):
    return Dish.objects.create(name='Блюдо 1', price=Decimal('100.00'))


# Фикстура для заказа
@pytest.fixture
def order(db, waiter_user):
    return Order.objects.create(table_number=1)


# Тест для создания пользователя через API (AdminUserCreateAPIView)
def test_admin_create_user(api_client, admin_user):
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

    # Авторизуем админа
    api_client.force_authenticate(user=admin_user)
    url = '/api/v1/users/create/'
    data = {'username': 'newuser',
            'role': CustomUser.WAITER, 'password': 'secret'}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, \
        'Ошибка: пользователь не создан'
    # Проверяем, что в ответе присутствует идентификатор нового пользователя
    response_data = response.json()
    assert 'id' in response_data, \
        'Ошибка: в ответе отсутствует идентификатор пользователя'


# Тест для получения списка заказов через OrderViewSet (GET)
def test_order_list(api_client, waiter_user, order):
    api_client.force_authenticate(user=waiter_user)
    url = '/api/v1/orders/'
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, \
        'Ошибка: не удалось получить список заказов'
    data = response.json()
    # Если ответ пагинирован, берем список заказов из поля 'results'
    orders = data.get('results', data)
    assert any(
        o['id'] == order.id for o in orders), \
        'Ошибка: заказ не найден в списке'


# Тест для создания заказа через OrderViewSet (POST)
def test_order_create(api_client, waiter_user, dish):
    api_client.force_authenticate(user=waiter_user)
    url = '/api/v1/orders/'
    data = {
        'table_number': 2,
        'order_items': [
            {'dish_id': dish.id, 'quantity': 2}
        ]
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED, \
        'Ошибка: создание заказа не прошло'
    created_order = response.json()
    assert created_order['table_number'] == 2, 'Ошибка: неверный номер стола'


# Тест для изменения статуса заказа через action change_status.
# Для повара попытка установить статус "Оплачено" должна возвращать ошибку.
def test_order_change_status_forbidden(api_client, chef_user, order):
    api_client.force_authenticate(user=chef_user)
    url = f'/api/v1/orders/{order.id}/change-status/'
    data = {'status': Order.PAID}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN, \
        'Ошибка: повару разрешено менять статус на "Оплачено"'
    error = response.json().get('error', '')
    expected_error = 'Повар не может установить статус "Оплачено".'
    assert expected_error in error, 'Ошибка: неверное сообщение об ошибке'


# Тест для успешного изменения статуса заказа администратором
def test_order_change_status_success(api_client, admin_user, order):
    api_client.force_authenticate(user=admin_user)
    url = f'/api/v1/orders/{order.id}/change-status/'
    new_status = 'ready'
    data = {'status': new_status}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK, \
        'Ошибка: администратор не может изменить статус заказа'
    result = response.json()
    assert 'status' in result, 'Ошибка: ответ не содержит нового статуса'
    assert result['status'], 'Ошибка: статус заказа не обновлён'


# Тест для обработки неверного статуса при изменении заказа
def test_order_change_status_invalid(api_client, admin_user, order):
    api_client.force_authenticate(user=admin_user)
    url = f'/api/v1/orders/{order.id}/change-status/'
    data = {'status': 'invalid_status'}
    response = api_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST, \
        'Ошибка: неверный статус должен возвращать код 400'
    error = response.json().get('error', '')
    expected_error = 'Неверный статус'
    assert expected_error in error, \
        'Ошибка: неверное сообщение об ошибке для некорректного статуса'


# Тест для удаления заказа через OrderViewSet (DELETE).
# Удаление доступно только админу.
def test_order_delete(api_client, admin_user, order):
    api_client.force_authenticate(user=admin_user)
    url = f'/api/v1/orders/{order.id}/'
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT, \
        'Ошибка: заказ не удалён'
    with pytest.raises(
        Order.DoesNotExist, match='Order matching query does not exist.'
    ):
        Order.objects.get(id=order.id)


# Тест для получения выручки через RevenueReportAPIView
def test_revenue_report(api_client, admin_user, order, dish):
    api_client.force_authenticate(user=admin_user)
    # Завершаем заказ и создаем позицию
    order.status = Order.PAID
    order.save()
    OrderItem.objects.create(order=order, dish=dish, quantity=3)
    order.recalc_total()
    url = '/api/v1/revenue/'
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, \
        'Ошибка: не удалось получить отчёт о выручке'
    total_revenue = response.json().get('total_revenue')
    expected_total = float(dish.price * 3)
    assert total_revenue == expected_total, 'Ошибка: неверная выручка'
