from . import views
from django.urls import path

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('registration/', views.registration, name='registration'),
    path('change_profile_data/', views.change_profile_data, name='change_profile_data'),
    path('change_password/', views.change_password, name='change_password'),
]
