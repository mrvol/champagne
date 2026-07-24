from django.urls import path

from review import views

urlpatterns = [
    path('review/list/', views.review_list, name='review_list'),
    path('review/<int:pk>/', views.review_detail, name='review_detail'),
]
