from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/entrevista/(?P<entrevista_id>\d+)/$', consumers.EntrevistaConsumer.as_asgi()),
]