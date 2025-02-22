from django.contrib.auth import get_user_model
from rest_framework import serializers

from orders.models import Dish, Order, OrderItem

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользовательской модели.

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


class DishSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели блюда.
    """

    class Meta:
        model = Dish
        fields = ['id', 'name', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели элемента заказа.
    """

    dish = DishSerializer(read_only=True)
    dish_id = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.all(), source='dish', write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'dish', 'dish_id', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели заказа.
    """

    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'total_price', 'order_items']
        read_only_fields = ['id', 'total_price']
