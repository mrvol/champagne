from django.urls import path

from address import views

urlpatterns = [
    path('address/list/', views.address_list, name='address_list'),
    path('address/<int:pk>/', views.address_detail, name='address_detail'),
]
