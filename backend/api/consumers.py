import json
from channels.generic.websocket import AsyncWebsocketConsumer
from geopy.distance import geodesic
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class SimulationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.active_groups = set()  # Track active stoplight groups for the simulation
        self.active_stoplights = set() # Track active stoplights for the simulation

        # Retrieve stoplight groups and stoplights from the session
        self.stoplight_groups = self.scope["session"].get("stoplight_groups", [])
        self.stoplights = self.scope["session"].get("stoplights", [])

        if not self.stoplight_groups:
            print("No stoplight groups found in the session.")
        else:
            print(f"Stoplight groups loaded: {self.stoplight_groups}")

        if not self.stoplights:
            print(f"No stoplights in {self.stoplight_groups}")
        else:
            print(f"Stoplights loaded: {self.stoplights}")

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

                  # Find the closest stoplight in this group
                  group_stoplights = [
                      s for s in self.stoplights if s["groupID"] == group_id
                  ]

                  if group_stoplights:
                      closest_stoplight = min(
                          group_stoplights,
                          key=lambda s: geodesic(
                              current_location, (s["lookahead_lat"], s["lookahead_lng"])
                          ).meters
                      )

                      # Track this stoplight as the active one
                      self.active_stoplights.add(closest_stoplight["stoplightID"])

                      message = {
                          "activate": 1,
                          "groupID": group_id,
                          "stoplightID": closest_stoplight["stoplightID"],
                      }

                      print(f"Broadcasting message to ESP Websocket: {message}")

                      await channel_layer.group_send(
                          "esp32_group",
                          {"type": "broadcast_message", "message": message},
                      )
          else:
              if group_id in self.active_groups:
                  # Exiting the radius
                  self.active_groups.remove(group_id)

                  # Deactivate the previously active stoplight in this group
                  group_stoplights = [
                      s for s in self.stoplights if s["groupID"] == group_id
                  ]
                  for stoplight in group_stoplights:
                      if stoplight["stoplightID"] in self.active_stoplights:
                          self.active_stoplights.remove(stoplight["stoplightID"])
                          message = {
                              "activate": 0,
                              "groupID": group_id,
                              "stoplightID": stoplight["stoplightID"],
                          }

                          print(f"Broadcasting message to ESP Websocket: {message}")
                          
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Received from ESP32: {data}")  # Print received data
        await self.send(text_data=json.dumps({"message": f"Echo: {data}"}))

    async def broadcast_message(self, event):
        message = event["message"]
        print(f"Broadcasting to ESP32 WebSocket: {message}")
        await self.send(text_data=json.dumps(message))
