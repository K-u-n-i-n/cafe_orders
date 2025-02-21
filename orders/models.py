from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    WAITER = 'waiter'
    CHEF = 'chef'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (WAITER, 'Официант'),
        (CHEF, 'Шеф-повар'),
        (ADMIN, 'Админ'),
    ]

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=WAITER
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_chef(self):
        return self.role == self.CHEF

    @property
    def is_waiter(self):
        return self.role == self.WAITER


class Dish(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['name']

    def __str__(self):
        return self.name


class Order(models.Model):
    PENDING = 'pending'
    READY = 'ready'
    PAID = 'paid'

    ORDER_STATUS_CHOICES = [
        (PENDING, 'В ожидании'),
        (READY, 'Готово'),
        (PAID, 'Оплачено'),
    ]
    table_number = models.IntegerField()
    status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default=PENDING
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    dishes = models.ManyToManyField(
        Dish,
        through='OrderItem'
    )

    def recalc_total(self):
        total = Decimal('0.00')
        for item in self.order_items.all():
            total += item.dish.price * item.quantity
        self.total_price = total
        self.save(update_fields=['total_price'])

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['table_number']
        default_related_name = 'orders'

    def __str__(self):
        return f'Заказ {self.id} (Стол {self.table_number})'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE
    )
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        default_related_name = 'order_items'
        constraints = [
            models.UniqueConstraint(
                fields=('order', 'dish'),
                name='unique_order_in_dish',
            )
        ]

    def __str__(self):
        return f'{self.dish.name} x {self.quantity}'
