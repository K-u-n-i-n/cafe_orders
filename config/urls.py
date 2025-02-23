from django.contrib import admin
from django.urls import include, path

handler404 = 'orders.views.page_not_found'
handler500 = 'orders.views.server_error'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/v1/', include('api.urls')),
    path('', include('orders.urls', namespace='orders')),
]
