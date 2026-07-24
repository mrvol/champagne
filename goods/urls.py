from django.urls import path

from goods import views

urlpatterns = [
    path('good/list/', views.good_list, name='good_list'),
    path('good/<int:pk>/', views.good_detail, name='good_detail'),
]
