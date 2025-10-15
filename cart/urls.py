from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view'),
    path('add/<int:product_id>/', views.add_to_cart, name='add'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove'),
    path('clear/', views.clear_cart, name='clear'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('payment/', views.payment, name='payment'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('wishlist/move-to-cart/<int:product_id>/', views.wishlist_move_to_cart, name='wishlist_move_to_cart'),
]

