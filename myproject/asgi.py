import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from myapp import routing as myapp_routing  # Update the import statement here
from myapp.consumers import ChatConsumer  # Import your ChatConsumer here

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Replace 'myproject' with your project name

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                myapp_routing.websocket_urlpatterns  # Use 'myapp_routing' here
            )
        ),
    }
)

# Add the ChatConsumer to the application
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                myapp_routing.websocket_urlpatterns
            )
        ),
    }
)
