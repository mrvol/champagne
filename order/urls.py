from django.urls import path

from order import views

urlpatterns = [
    path('order/list/', views.order_list, name='order_list'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
]
