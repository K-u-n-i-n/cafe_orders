# Generated by Django 5.0.9 on 2025-02-23 16:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_orderitem_unique_order_in_dish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='table_number',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Номер стола должен быть не менее 1'), django.core.validators.MaxValueValidator(50, message='Номер стола не может превышать 50')]),
        ),
    ]
