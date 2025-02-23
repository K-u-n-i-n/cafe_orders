from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import AdminUserCreateAPIView, OrderViewSet, RevenueReportAPIView

router_v1 = DefaultRouter()
router_v1.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('login/', obtain_auth_token, name='api_token_auth'),
    path(
        'users/create/', AdminUserCreateAPIView.as_view(),
        name='admin_create_user'
    ),
    path(
        'revenue/', RevenueReportAPIView.as_view(),
        name='revenue_report'
    ),
    path('', include(router_v1.urls)),
]
