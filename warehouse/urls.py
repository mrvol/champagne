from django.urls import path

from warehouse import views

urlpatterns = [
    path('warehouse/list/', views.warehouse_list, name='warehouse_list'),
    path('warehouse/<int:pk>/', views.warehouse_detail, name='warehouse_detail'),
    path('stock/list/', views.stock_list, name='stock_list'),
    path('stock/<int:pk>/', views.stock_detail, name='stock_detail'),
]
