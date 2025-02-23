from rest_framework.permissions import BasePermission, SAFE_METHODS


class CustomOrderPermission(BasePermission):
    """
    Кастомный класс разрешений для заказов.

    Права доступа:
    - Все авторизованные могут просматривать заказы (GET).
    - Официант и админ могут создавать заказы (POST).
    - Повар и админ могут менять статус (PATCH change-status).
    - Только админ может редактировать (PATCH) и удалять (DELETE).
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == 'POST':
            return request.user.is_waiter or request.user.is_admin

        if view.action == 'change_status':
            return request.user.is_chef or request.user.is_admin

        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'partial_update', 'destroy']:
            return request.user.is_admin
        return True
