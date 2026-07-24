from django.urls import path

from person import views

urlpatterns = [
    path('user/list/', views.user_list, name='user_list'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
]
