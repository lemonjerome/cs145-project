from django.urls import path
from .consumers import SimulationConsumer, ESP32Consumer, LiveSimulationConsumer
from .views import post_route, get_stoplights

# Define an empty urlpatterns for HTTP routes (if needed in the future)
urlpatterns = [
    path("route/", post_route, name="route"),  # Endpoint for posting coordinates
    path("stoplights/", get_stoplights, name="get_stoplights"),  # Endpoint to retrieve stoplight groups
]

# WebSocket URL patterns (used in asgi.py)
websocket_urlpatterns = [
    path('ws/simulation/', SimulationConsumer.as_asgi()),  # For simulation
    path('ws/esp32/', ESP32Consumer.as_asgi()),            # For ESP32 connection
    path('ws/live/', LiveSimulationConsumer.as_asgi()),
]