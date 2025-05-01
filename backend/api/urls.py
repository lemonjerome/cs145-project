from django.urls import path
from .consumers import SimulationConsumer

# Define an empty urlpatterns for HTTP routes (if needed in the future)
urlpatterns = []

# WebSocket URL patterns (used in asgi.py)
websocket_urlpatterns = [
    path('ws/simulation/', SimulationConsumer.as_asgi()),
]