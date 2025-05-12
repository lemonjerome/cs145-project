import json
from channels.generic.websocket import AsyncWebsocketConsumer
from geopy.distance import geodesic
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class SimulationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.active_groups = set()  # Track active stoplight groups for the simulation

        # Retrieve stoplight groups and closest stoplights from the session
        self.stoplight_groups = self.scope["session"].get("stoplight_groups", [])
        self.closest_stoplights = self.scope["session"].get("closest_stoplights", {})

        print("Simulation WebSocket connection established.")

    async def disconnect(self, close_code):
        print("Simulation WebSocket connection closed.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        coordinates = data.get("coordinates")
        if not coordinates:
            return

        # Check proximity to stoplight groups
        current_location = (coordinates["lat"], coordinates["lng"])
        channel_layer = get_channel_layer()

        for group in self.stoplight_groups:
            group_id = group["groupID"]
            group_location = (group["lat"], group["lng"])
            distance_to_group = geodesic(current_location, group_location).meters

            if distance_to_group <= 100:
                if group_id not in self.active_groups:
                    # Entering the radius
                    self.active_groups.add(group_id)

                    # Get the precomputed closest stoplight for this group
                    closest_stoplight = self.closest_stoplights.get(str(group_id))

                    if closest_stoplight:
                        message = {
                            "activate": 1,
                            "groupID": group_id,
                            "stoplightID": closest_stoplight["stoplightID"],
                        }

                        # Send to frontend WebSocket
                        await self.send(text_data=json.dumps(message))

                        await channel_layer.group_send(
                            "esp32_group",
                            {"type": "broadcast_message", "message": message},
                        )

            else:
                if group_id in self.active_groups:
                    # Exiting the radius
                    self.active_groups.remove(group_id)

                    # Deactivate the previously active stoplight in this group
                    closest_stoplight = self.closest_stoplights.get(str(group_id))
                    if closest_stoplight:
                        message = {
                            "activate": 0,
                            "groupID": group_id,
                            "stoplightID": closest_stoplight["stoplightID"],
                        }

                        # Send to frontend WebSocket
                        await self.send(text_data=json.dumps(message))

                        await channel_layer.group_send(
                            "esp32_group",
                            {"type": "broadcast_message", "message": message},
                        )

class ESP32Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("esp32_group", self.channel_name)
        print("ESP32 WebSocket connection established.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("esp32_group", self.channel_name)
        print("ESP32 WebSocket connection closed.")


    async def broadcast_message(self, event):
        message = event["message"]
        print(f"Broadcasting to ESP32 WebSocket: {message}")
        await self.send(text_data=json.dumps(message))
