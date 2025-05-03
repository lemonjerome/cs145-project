import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SimulationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("WebSocket connection established.")

    async def disconnect(self, close_code):
        print("WebSocket connection closed.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        coordinates = data.get('coordinates')
        