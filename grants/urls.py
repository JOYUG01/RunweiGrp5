# grants/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('grants/', views.grants_list, name='grants_list'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),  # Updated to CustomLoginView
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('apply/<str:grant_name>/', views.apply, name='apply'),
]
