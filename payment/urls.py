from django.urls import path

from payment import views

urlpatterns = [
    path('payment/list/', views.payment_list, name='payment_list'),
    path('payment/<int:pk>/', views.payment_detail, name='payment_detail'),
]
