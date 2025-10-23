# recruitment/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.vagas_list, name='vagas_list'),
    path('<int:id>/', views.vaga_detail, name='vaga_detail'),
    path('<int:vaga_id>/candidatar/', views.candidatar, name='candidatar'),
    path('entrevistas/<int:entrevista_id>/', views.entrevista_view, name='entrevista'),
]