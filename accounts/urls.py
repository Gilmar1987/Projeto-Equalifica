# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    # Novo endpoint de edição de perfil PCD
    path('pcd/profile/edit/', views.PCDProfileEditView.as_view(), name='pcd_profile_edit'),
]