import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SimulationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Simulation WebSocket connection established.")

    async def disconnect(self, close_code):
        print("Simulation WebSocket connection closed.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Simulation received: {data}")
        await self.send(text_data=json.dumps({"message": f"Echo: {data}"}))


class ESP32Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        message = "ESP32 connected to the server."
        print(message)  # Print connection message to the server console
        await self.send(text_data=json.dumps({"message": message}))

    async def disconnect(self, close_code):
        message = "ESP32 disconnected from the server."
        print(message)  # Print disconnection message to the server console
        await self.send(text_data=json.dumps({"message": message}))

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received from ESP32: {data}")  # Print received data
        await self.send(text_data=json.dumps({"message": f"Echo: {data}"}))
