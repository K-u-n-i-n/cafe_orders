from django.contrib import admin

from .models import CustomUser, Dish, Order, OrderItem


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role',)
    list_filter = ('role',)
    search_fields = ('username',)
    ordering = ('username',)
    list_per_page = 10


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 10


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'table_number', 'status',
        'total_price', 'get_dishes'
    )
    list_filter = ('status', )
    search_fields = ('id', 'table_number',)
    list_per_page = 10

    @admin.display(description='Блюда')
    def get_dishes(self, obj):
        return ', '.join([dish.name for dish in obj.dishes.all()])


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'dish', 'quantity')
    search_fields = ('order__id', 'dish__name')
    list_filter = ('dish',)
