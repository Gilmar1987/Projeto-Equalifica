# equalifica_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts.views import PCDDashboardView
from companies.views import RecruiterDashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')), 
    
    # Dashboards diretos (sem prefixo app)
    path('pcd/dashboard/', PCDDashboardView.as_view(), name='pcd_dashboard'),
    path('recruiter/dashboard/', RecruiterDashboardView.as_view(), name='recruiter_dashboard'),
    
    path('vagas/', include('recruitment.urls')), 
    path('recruiter/', include('companies.urls')),  # ← alterado de 'companies/' para 'recruiter/'
    path('accessibility/', include('accessibility.urls')),  # ← adicionado
]