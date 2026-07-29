from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

import address.views
import cart.views
import company.views
import goods.views
import invite.views
import mp.views
import order.views
import payment.views
import person.views
import review.views
import transaction.views
import warehouse.views

urlpatterns = [
    path('i18n/setlang/', person.views.set_language, name='set_language'),

    path('admin/', admin.site.urls),
    path('', mp.views.home, name='home'),
    path('staff/stats/', mp.views.staff_dashboard, name='staff_dashboard'),

    # person
    path('user/list/', person.views.user_list, name='user_list'),
    path('user/<int:pk>/', person.views.user_detail, name='user_detail'),
    path('api/user/list/', person.views.user_detail_api, name='user_list_api'),
    path('api/user/<int:pk>/', person.views.user_detail_api, name='user_detail_api'),
    path('staff/users/', person.views.staff_user_list, name='staff_user_list'),
    path('login/', person.views.login_view, name='login'),
    path('register/', person.views.register, name='register'),
    path('logout/', person.views.logout_view, name='logout'),
    path('passkey/register/options/', person.views.passkey_register_options, name='passkey_register_options'),
    path('passkey/register/verify/', person.views.passkey_register_verify, name='passkey_register_verify'),
    path('passkey/login/options/', person.views.passkey_login_options, name='passkey_login_options'),
    path('passkey/login/verify/', person.views.passkey_login_verify, name='passkey_login_verify'),

    # address
    path('address/list/', address.views.address_list, name='address_list'),
    path('address/<int:pk>/', address.views.address_detail, name='address_detail'),

    # company
    path('company/list/', company.views.company_list, name='company_list'),
    path('company/<int:pk>/', company.views.company_detail, name='company_detail'),
    path('company/<int:pk>/goods/', company.views.company_goods, name='company_goods'),
    path('api/company/list/', company.views.company_list_api, name='company_list_api'),
    path('api/company/<int:pk>/', company.views.company_detail_api, name='company_detail_api'),
    path('staff/companies/', company.views.staff_company_list, name='staff_company_list'),

    # goods
    path('good/list/', goods.views.good_list, name='good_list'),
    path('good/<int:pk>/', goods.views.good_detail, name='good_detail'),
    path('api/good/<int:pk>/', goods.views.good_detail_api, name='good_detail_api'),
    path('api/good/list/', goods.views.good_detail_api, name='good_list_api'),
    path('api/good/stats/', goods.views.good_stats_api, name='good_stats_api'),
    path('api/good/<int:pk>/photos/', goods.views.good_photos_api, name='good_photos_api'),
    path('staff/goods/', goods.views.staff_good_list, name='staff_good_list'),

    # order
    path('order/list/', order.views.order_list, name='order_list'),
    path('order/<int:pk>/', order.views.order_detail, name='order_detail'),
    path('order/<int:pk>/invoice/', order.views.order_invoice, name='order_invoice'),
    path('order/<int:pk>/reorder/', order.views.order_reorder, name='order_reorder'),
    path('api/order/list/', order.views.order_list_api, name='order_list_api'),
    path('api/order/<int:pk>/', order.views.order_detail_api, name='order_detail_api'),
    path('staff/orders/', order.views.staff_order_list, name='staff_order_list'),

    # payment
    path('payment/list/', payment.views.payment_list, name='payment_list'),
    path('payment/<int:pk>/', payment.views.payment_detail, name='payment_detail'),

    # review
    path('review/list/', review.views.review_list, name='review_list'),
    path('review/<int:pk>/', review.views.review_detail, name='review_detail'),

    # transaction
    path('transaction/list/', transaction.views.transaction_list, name='transaction_list'),
    path('transaction/<int:pk>/', transaction.views.transaction_detail, name='transaction_detail'),

    # warehouse
    path('warehouse/list/', warehouse.views.warehouse_list, name='warehouse_list'),
    path('warehouse/<int:pk>/', warehouse.views.warehouse_detail, name='warehouse_detail'),
    path('stock/list/', warehouse.views.stock_list, name='stock_list'),
    path('stock/<int:pk>/', warehouse.views.stock_detail, name='stock_detail'),

    # cart
    path('cart/', cart.views.cart_detail, name='cart_detail'),
    path('cart/remove/<int:item_id>/', cart.views.remove_from_cart, name='remove_from_cart'),
    path('good/<int:pk>/add-to-cart/', cart.views.add_to_cart, name='add_to_cart'),
    path('api/goods/search/', cart.views.api_search, name='api_search'),

    # invite / onboarding
    path('staff/invites/', invite.views.staff_invite_list, name='staff_invite_list'),
    path('api/invite/list/', invite.views.invitation_list_api, name='invite_list_api'),
    path('invite/<str:token>/', invite.views.invitation_landing, name='invite_landing'),
    path('invite/<str:token>/company/', invite.views.invitation_company, name='invite_company'),
    path('invite/<str:token>/products/', invite.views.invitation_products, name='invite_products'),
    path('invite/<str:token>/products/add/', invite.views.invitation_product_edit, name='invite_product_add'),
    path('invite/<str:token>/products/<int:pk>/', invite.views.invitation_product_edit, name='invite_product_edit'),
    path('invite/<str:token>/products/<int:pk>/delete/', invite.views.invitation_product_delete, name='invite_product_delete'),
    path('invite/<str:token>/review/', invite.views.invitation_review, name='invite_review'),
    path('invite/<str:token>/completed/', invite.views.invitation_completed, name='invite_completed'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 