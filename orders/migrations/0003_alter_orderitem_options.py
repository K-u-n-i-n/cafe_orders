# Generated by Django 5.0.9 on 2025-02-18 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_dish_order_alter_customuser_options_orderitem_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderitem',
            options={'default_related_name': 'order_items', 'verbose_name': 'позиция заказа', 'verbose_name_plural': 'Позиции заказа'},
        ),
    ]
