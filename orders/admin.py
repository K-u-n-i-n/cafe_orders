from django.contrib import admin

from .models import CustomUser, Dish


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role',)
    list_filter = ('role',)
    search_fields = ('username',)
    list_per_page = 10


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'price',)
    search_fields = ('name',)
    list_per_page = 10
