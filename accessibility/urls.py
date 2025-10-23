# accessibility/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('translate/libras-to-audio/', views.libras_to_audio, name='libras_to_audio'),
    path('translate/audio-to-libras/', views.audio_to_libras, name='audio_to_libras'),
]