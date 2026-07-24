from django.urls import path

from transaction import views

urlpatterns = [
    path('transaction/list/', views.transaction_list, name='transaction_list'),
    path('transaction/<int:pk>/', views.transaction_detail, name='transaction_detail'),
]
