from django.urls import path

from person import views

urlpatterns = [
    path('user/list/', views.user_list, name='user_list'),
    path('user/<int:pk>/', views.user_detail, name='user_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('passkey/register/options/', views.passkey_register_options, name='passkey_register_options'),
    path('passkey/register/verify/', views.passkey_register_verify, name='passkey_register_verify'),
    path('passkey/login/options/', views.passkey_login_options, name='passkey_login_options'),
    path('passkey/login/verify/', views.passkey_login_verify, name='passkey_login_verify'),
]
