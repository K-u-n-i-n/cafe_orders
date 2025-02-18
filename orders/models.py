from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    WAITER = "waiter"
    CHEF = "chef"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (WAITER, "Официант"),
        (CHEF, "Шеф-повар"),
        (ADMIN, "Админ"),
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


class Dish(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['name']

    def __str__(self):
        return self.name
