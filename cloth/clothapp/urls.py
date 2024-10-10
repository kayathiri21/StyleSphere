from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:product_slug>/', views.detail, name='detail'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='app/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='app/request_password_reset.html',
             email_template_name='app/password_reset_email.html',
             subject_template_name='app/password_reset_subject.txt',
             success_url='/password_reset_done/'),
         name='password_reset'),

    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='app/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='app/reset_password.html',
             success_url='/password_reset_complete/'),
         name='password_reset_confirm'),

    path('password_reset_complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='app/password_reset_complete.html'),
         name='password_reset_complete'),

    path('subcategory/<slug:subcategory_slug>/', views.subcategory_products, name='subcategory_products'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_to_cart'),  # Only one entry here
    path('update-cart/', views.update_cart, name='update_cart'),
    path('search/', views.search, name='search'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
     path('payment_success/', views.payment_success, name='payment_success'),
]
