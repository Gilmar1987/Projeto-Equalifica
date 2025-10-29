# companies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.RecruiterDashboardView.as_view(), name='recruiter_dashboard'),
    path('vagas/new/', views.create_vaga, name='vaga_create'),
    path('entrevistas/new/<int:candidatura_id>/', views.schedule_interview, name='schedule_interview'),
    path('entrevistas/edit/<int:entrevista_id>/', views.edit_interview, name='edit_interview'),
    path('entrevistas/cancel/<int:entrevista_id>/', views.cancel_interview, name='cancel_interview'),
]