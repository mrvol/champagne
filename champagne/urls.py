from django.contrib import admin
from django.urls import include, path

from mp import views as mp_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mp_views.home, name='home'),
    path('', include('person.urls')),
    path('', include('address.urls')),
    path('', include('company.urls')),
    path('', include('goods.urls')),
    path('', include('order.urls')),
    path('', include('payment.urls')),
    path('', include('review.urls')),
    path('', include('transaction.urls')),
    path('', include('warehouse.urls')),
]
