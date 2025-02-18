from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role',)
    list_filter = ('role',)
    search_fields = ('username',)
    list_per_page = 10
