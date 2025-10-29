# accessibility/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('audio-to-libras/', views.audio_to_libras, name='audio_to_libras'),
]