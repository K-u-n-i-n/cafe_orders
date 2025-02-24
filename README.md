# Управление заказами в ресторане

[![Django](https://img.shields.io/badge/Django-5.0.9-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12.7-blue)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15.0-red)](https://www.django-rest-framework.org/)

Веб-приложение для автоматизации управления заказами в ресторане.

## 🚀 Особенности

- Полный цикл управления заказами: создание, редактирование, удаление, поиск
- Автоматический расчет стоимости заказа
- Управление статусами заказов (в ожидании/готово/оплачено)
- Расчет дневной выручки по оплаченным заказам
- Ролевая система доступа (официант, повар, администратор)
- REST API с документацией Swagger
- Фильтрация заказов по статусу и номеру стола

## 🛠 Технологии

- Backend: Django 5.0.9
- API: Django REST Framework 3.15.0
- База данных: SQLite
- Язык: Python 3.12.7

## ⚙️ Установка

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/K-u-n-i-n/cafe_orders
    cd cafe_orders
    ```

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

3. Настройте базу данных:
    ```bash
    python manage.py migrate
    ```

4. Создайте администратора:
    ```bash
    python manage.py createsuperuser
    ```

5. Запустите сервер:
    ```bash
    python manage.py runserver
    ```

6. Зайдите в админку по адресу: http://127.0.0.1:8000/admin/

7. Поменяйте администратору роль на: **admin**

8. Создайте несколько блюд

Приложение будет доступно по адресу: http://127.0.0.1:8000/

## 📚 Документация API

Доступна через Swagger UI: http://127.0.0.1:8000/api/v1/docs/

## 👥 Роли и права доступа

Действие              | Официант | Повар  | Админ
----------------------|:--------:|:------:|:-----:
Просмотр заказов      | ✅       | ✅     | ✅   
Создание заказов      | ✅       | ❌     | ✅   
Изменение статуса     | ❌       | ✅*    | ✅   
Редактирование заказа | ❌       | ❌     | ✅   
Удаление заказа       | ❌       | ❌     | ✅   

* Повар может устанавливать только статус "Готово"

## 🌐 Использование

- Веб-интерфейс:
    - /admin-create-user/ - создание пользователя админом
    - /orders/ – список всех заказов
    - /orders/create/ – создание нового заказа
    - /revenue/ – отчет по выручке
    - /admin/ – админ-панель

- API Endpoints:
    - POST /api/v1/users/create/ - создание пользователя админом
    - GET /api/v1/orders/ – список заказов
    - POST /api/v1/orders/ – создать заказ
    - PATCH /api/v1/orders/{id}/ – изменить заказ
    - PATCH /api/v1/orders/{id}/change-status/ – изменить статус
    - GET /api/v1/revenue/ – получить выручку

## Над проектом работали:
Python Developer: <span style="color: green;">*Кунин Александр*</span> (k.u.n.i.n@mail.ru)
