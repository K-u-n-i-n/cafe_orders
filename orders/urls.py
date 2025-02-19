from django.urls import path

from .views import OrderCreateView, OrderDeleteView, OrderListView

app_name = 'orders'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('create/', OrderCreateView.as_view(), name='create'),
    path('<int:pk>/delete/', OrderDeleteView.as_view(), name='delete'),
]
