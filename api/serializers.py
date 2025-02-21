from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользовательской модели.

    Поля:
        - id: Идентификатор пользователя.
        - username: Имя пользователя.
        - role: Роль пользователя, выбирается из доступных вариантов.
        - password: Пароль пользователя (только для записи).

    Методы:
        - create: Создает нового пользователя с зашифрованным паролем.
    """

    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
