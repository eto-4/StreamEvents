from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/remove-avatar/', views.remove_avatar, name='remove_avatar'), 
    path('<str:username>/', views.public_profile_view, name='public_profile'),
]