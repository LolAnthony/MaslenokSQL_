from . import views
from django.urls import path

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('delete_product_cart/<int:product_id>/', views.delete_product_cart, name='delete_product_cart'),
    path('delete_all_products_from_db/', views.delete_all_products_view),
    path('initialize_from_sbis', views.initialize_products_view),
]
