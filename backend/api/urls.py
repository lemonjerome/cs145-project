from django.urls import path
from .consumers import SimulationConsumer, ESP32Consumer

# Define an empty urlpatterns for HTTP routes (if needed in the future)
urlpatterns = []

# WebSocket URL patterns (used in asgi.py)
websocket_urlpatterns = [
    path('ws/simulation/', SimulationConsumer.as_asgi()),  # For simulation
    path('ws/esp32/', ESP32Consumer.as_asgi()),            # For ESP32 connection
]