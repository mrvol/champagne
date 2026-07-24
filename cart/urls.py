from django.urls import path

from cart import views

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('good/<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
]
