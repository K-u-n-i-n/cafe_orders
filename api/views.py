from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser

from .serializers import CustomUserSerializer


class AdminUserCreateAPIView(CreateAPIView):
    """
    API для создания пользователя с ролями.
    Только администратор может создавать пользователей.
    """

    permission_classes = [IsAdminUser]
    serializer_class = CustomUserSerializer
