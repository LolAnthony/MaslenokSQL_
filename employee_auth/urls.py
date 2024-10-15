from . import views
from django.urls import path

urlpatterns = [
    path('', views.emp_index, name='emp_index'),
    path('profile/', views.emp_profile, name='emp_profile'),
    path('login/', views.emp_login, name='emp_login'),
    path('logout/', views.emp_logout, name='emp_logout'),
    path('change_profile_data/', views.emp_change_profile_data, name='emp_change_profile_data'),
    path('change_password/', views.emp_change_password, name='emp_change_password'),
]
