from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_login_view, name='signup_login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('razorpay-webhook/', views.razorpay_webhook, name='razorpay_webhook'),

]
