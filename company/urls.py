from django.urls import path

from company import views

urlpatterns = [
    path('company/list/', views.company_list, name='company_list'),
    path('company/<int:pk>/', views.company_detail, name='company_detail'),
]
