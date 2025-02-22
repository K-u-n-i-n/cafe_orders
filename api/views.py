from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.viewsets import ModelViewSet

from orders.models import Order
from .filters import OrderFilter
from .serializers import CustomUserSerializer, OrderSerializer


class AdminUserCreateAPIView(CreateAPIView):
    """
    API для создания пользователя с ролями.
    Только администратор может создавать пользователей.
    """

    permission_classes = [IsAdminUser]
    serializer_class = CustomUserSerializer


class OrderViewSet(ModelViewSet):
    """
    API для CRUD операций с заказами.
    Поддерживается фильтрация по номеру стола и статусу.
    """

    queryset = Order.objects.all().prefetch_related('order_items__dish')
    serializer_class = OrderSerializer
    filterset_class = OrderFilter

    @action(detail=True, methods=['patch'], url_path='change-status')
    def change_status(self, request, pk=None):
        """
        Частичное обновление статуса заказа.
        """

        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.ORDER_STATUS_CHOICES).keys():
            return Response(
                {'error': 'Неверный статус'},
                status=HTTP_400_BAD_REQUEST
            )
        if request.user.is_chef and new_status == Order.PAID:
            return Response(
                {'error': 'Повар не может установить статус "Оплачено".'},
                status=HTTP_403_FORBIDDEN
            )
        order.status = new_status
        order.recalc_total()
        order.save(update_fields=['status', 'total_price'])
        return Response({'status': order.get_status_display()})
