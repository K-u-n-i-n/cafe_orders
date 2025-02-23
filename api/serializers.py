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


class OrderReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения заказа"""

    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'status', 'total_price', 'order_items']


class OrderWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления заказа"""

    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['table_number', 'order_items']

    def validate_table_number(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Номер стола должен быть положительным.')
        return value

    def validate_order_items(self, value):
        dish_ids = [item['dish'].id for item in value]
        if len(dish_ids) != len(set(dish_ids)):
            raise serializers.ValidationError(
                'Блюда в заказе не должны повторяться.'
            )
        return value

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item in order_items_data:
            OrderItem.objects.create(order=order, **item)
        order.recalc_total()
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_items', None)
        instance.table_number = validated_data.get(
            'table_number', instance.table_number
        )
        instance.save()
        if order_items_data is not None:
            instance.order_items.all().delete()
            for item in order_items_data:
                OrderItem.objects.create(order=instance, **item)
            instance.recalc_total()
        return instance


class OrderStatusSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения статуса заказа."""

    status = serializers.ChoiceField(choices=Order.ORDER_STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['status']
