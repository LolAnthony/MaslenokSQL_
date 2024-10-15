from . import views
from django.urls import path

urlpatterns = [
    path('profile/', views.sh_profile, name='sh_profile'),
    path('login/', views.sh_login, name='sh_login'),
    path('logout/', views.sh_logout, name='sh_logout'),
    path('change_profile_data/', views.sh_change_profile_data, name='sh_change_profile_data'),
    path('change_password/', views.sh_change_password, name='sh_change_password'),
]
