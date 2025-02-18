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

    def __str__(self):
        return self.username
