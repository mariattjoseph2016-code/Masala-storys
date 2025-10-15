from django.urls import path
from .views import product_list, product_detail, add_product, update_product, delete_product


urlpatterns = [
    path('', product_list, name='product_list'),
    path('add/', add_product, name='add_product'),
    path('update/<int:pk>/', update_product, name='update_product'),
    path('delete/<int:pk>/', delete_product, name='delete_product'),
    path('<slug:slug>/', product_detail, name='product_detail'),
]


