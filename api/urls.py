from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import AdminUserCreateAPIView

router_v1 = DefaultRouter()

urlpatterns = [
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('users/create/', AdminUserCreateAPIView.as_view(),
         name='admin_create_user'),
]
