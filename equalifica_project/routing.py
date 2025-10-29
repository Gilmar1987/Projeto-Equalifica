# equalifica_project/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import accessibility.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(accessibility.routing.websocket_urlpatterns),
})