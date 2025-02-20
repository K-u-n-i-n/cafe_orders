from django.urls import path

from .views import (
    AdminCreateUserView,
    OrderCreateView,
    OrderDeleteView,
    OrderListView,
    OrderStatusUpdateView,
    RevenueReportView
)


app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('create/', OrderCreateView.as_view(), name='create'),
    path('revenue/', RevenueReportView.as_view(), name='revenue'),
    path('<int:pk>/delete/', OrderDeleteView.as_view(), name='delete'),
    path(
        '<int:pk>/status/', OrderStatusUpdateView.as_view(),
        name='update_status'
    ),
    path(
        'admin-create-user/', AdminCreateUserView.as_view(),
        name='admin_create_user'
    ),
]
