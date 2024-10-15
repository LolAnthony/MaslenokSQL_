from django.urls import path, include

from admin_menu import views

urlpatterns = [
    path('', views.admin_menu, name='admin_menu'),
    path('edit_product/', views.edit_product, name='edit_product'),
    path('add_product/', views.add_product, name='add_product'),
]
