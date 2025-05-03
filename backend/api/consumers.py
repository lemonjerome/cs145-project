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
        if coordinates:
            print(f"Received coordinates: {coordinates}", flush=True)
            # Echo the coordinates back to the client
            await self.send(text_data=json.dumps({
                'message': f"Coordinates received: {coordinates}"
            }))