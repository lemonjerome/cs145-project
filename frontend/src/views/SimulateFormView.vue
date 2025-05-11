<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-6 py-8">
    <!-- Loading Modal and Overlay -->
    <div
      v-show="isLoading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white p-6 rounded-lg shadow-lg text-center">
        <h2 class="text-xl font-bold mb-4">Loading Stoplights...</h2>
        <p class="text-gray-600">Please wait while we load the stoplight data.</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="bg-gray-100 rounded-lg shadow-lg w-full min-w-5xl p-6">
      <h1 class="text-4xl font-bold text-green-500 mb-6 text-center">Route Simulation</h1>

      <!-- Speed & Buttons -->
      <form @submit.prevent class="mb-6 flex flex-col items-center gap-4 w-full">
        <label class="text-lg font-medium">Speed: {{ speedKmh }} km/h</label>
        <input
          type="range"
          min="0"
          max="220"
          step="5"
          v-model.number="speedKmh"
          class="w-full"
          @input="onSpeedChange"
        />
        <div class="flex gap-4 mt-2">
          <button type="button" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded" @click="startSimulation">Start</button>
          <button type="button" class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded" @click="resumeSimulation">Resume</button>
          <button type="button" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded" @click="pauseSimulation">Pause</button>
        </div>
      </form>

      <!-- Map -->
      <div class="w-full">
        <div id="map" class="w-full h-96 border border-gray-300 rounded-lg"></div>
      </div>

      <!-- Go Back Button -->
      <button
        class="bg-gray-500 text-white px-6 py-3 rounded-lg shadow hover:bg-gray-600 mt-6"
        @click="showModal = true"
      >
        Go Back
      </button>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg text-center">
        <h2 class="text-xl font-bold mb-4">Are you sure you want to go back?</h2>
        <p class="text-gray-600 mb-6">This will stop the simulation and disconnect from the server.</p>
        <div class="flex justify-center gap-4">
          <button
            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
            @click="confirmGoBack"
          >
            Yes, Go Back
          </button>
          <button
            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
            @click="showModal = false"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";
import trafficLightIcon from "@/assets/svg/traffic-light-svgrepo-com.svg";
import ambulanceIconUrl from "@/assets/svg/ambulance-svgrepo-com.svg";
import accidentIconUrl from "@/assets/svg/accident-svgrepo-com.svg";
import redDotIcon from "@/assets/svg/red-circle-svgrepo-com.svg";

export default {
  name: "SimulationFormView",
  data() {
    return {
      map: null,
      polyline: null,
      routeCoordinates: [],
      speedKmh: 0,
      simMarker: null,
      animationFrameId: null,
      isPaused: false,
      pausedDistance: 0,
      startTime: null,
      lastTimestamp: null,
      websocket: null, // WebSocket connection
      showModal: false,
      isLoading: true, // Controls the loading modal
    };
  },
  async mounted() {
    try {
      // Establish WebSocket connection
      const websocketUrl = `${import.meta.env.VITE_BACKEND_BASE_URL.replace(
        "http",
        "ws"
      )}/ws/simulation/`;
      this.websocket = new WebSocket(websocketUrl);

      this.websocket.onopen = () => {
        console.log("WebSocket connection established.");
      };

      this.websocket.onerror = (error) => {
        console.error("WebSocket error:", error);
        alert("Failed to establish WebSocket connection.");
      };

      this.websocket.onclose = () => {
        console.log("WebSocket connection closed.");
      };

      const csrfToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken"))
        ?.split("=")[1];

      const response = await axios.get(`${import.meta.env.VITE_BACKEND_API_URL}/stoplights/`, {
        withCredentials: true,
        headers: {
          "X-CSRFToken": csrfToken,
        },
      });

      const stoplight_groups = response.data.stoplight_groups;
      const stoplights = response.data.stoplights;

      if (!Array.isArray(stoplight_groups)) {
        throw new Error("Unexpected response format: stoplight_groups is not an array.");
      }

      // Wait for the DOM to render the map container
      this.$nextTick(() => {
        this.initializeMap();

        // Place stoplight group markers
        stoplight_groups.forEach((stoplight_group) => {
          const { lat, lng, groupID } = stoplight_group;

          const icon = L.icon({
            iconUrl: trafficLightIcon,
            iconSize: [32, 32],
            iconAnchor: [16, 32],
          });

          L.marker([lat, lng], { icon })
            .addTo(this.map)
        });

        // Place stoplight markers
        stoplights.forEach((stoplight) => {
          const { stoplightID, groupID, local_id, lat, lng, lookahead_lat, lookahead_lng } = stoplight;

          const icon = L.icon({
            iconUrl: redDotIcon,
            iconSize: [5, 5],
            iconAnchor: [5, 5],
          });

          L.marker([lat, lng], { icon })
            .addTo(this.map)
        });

        // Add start and destination markers
        this.addRouteMarkers();
      });
    } catch (error) {
      console.error("Error fetching stoplight groups:", error);
      alert("Failed to fetch stoplight groups.");
    } finally {
      // Hide the loading modal
      this.isLoading = false;
    }
  },
  beforeDestroy() {
    if (this.websocket) {
      this.websocket.close();
    }
    localStorage.removeItem("websocket");
  },
  methods: {
    initializeMap() {
      const mapContainer = document.getElementById("map");
      if (!mapContainer) {
        console.error("Map container not found.");
        return;
      }

      this.map = L.map(mapContainer).setView([42.438878, -71.119277], 13);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(this.map);

      const gpxData = localStorage.getItem("gpxData");

      if (gpxData) {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(gpxData, "application/xml");

        const GPX_NS = xmlDoc.documentElement.namespaceURI;
        const trackpoints = xmlDoc.getElementsByTagNameNS(GPX_NS, "trkpt");

        for (let i = 0; i < trackpoints.length; i++) {
          const lat = parseFloat(trackpoints[i].getAttribute("lat"));
          const lon = parseFloat(trackpoints[i].getAttribute("lon"));
          this.routeCoordinates.push([lat, lon]);
        }

        if (this.routeCoordinates.length > 0) {
          this.polyline = L.polyline(this.routeCoordinates, {
            color: "blue",
            weight: 4,
          }).addTo(this.map);

          this.map.fitBounds(this.polyline.getBounds());
        } else {
          alert("No trackpoints found in the GPX file.");
        }
      } else {
        alert("No GPX data found in localStorage.");
      }
    },
    addRouteMarkers() {
      if (this.routeCoordinates.length > 0) {
        // Start marker (ambulance icon)
        const startIcon = L.icon({
          iconUrl: ambulanceIconUrl,
          iconSize: [32, 32],
          iconAnchor: [16, 32],
        });
        this.startMarker = L.marker(this.routeCoordinates[0], { icon: startIcon }).addTo(this.map);

        // Destination marker (accident icon)
        const destinationIcon = L.icon({
          iconUrl: accidentIconUrl,
          iconSize: [32, 32],
          iconAnchor: [16, 32],
        });
        L.marker(this.routeCoordinates[this.routeCoordinates.length - 1], { icon: destinationIcon }).addTo(this.map);
      }
    },
    startSimulation() {
      if (!this.polyline || this.speedKmh <= 0) {
        alert("Please select a speed greater than 0.");
        return;
      }

      this.stopSimulation();
      this.isPaused = false;
      this.pausedDistance = 0;
      this.lastTimestamp = null;

      const start = this.polyline.getLatLngs()[0];
      const ambulanceIcon = L.icon({
        iconUrl: ambulanceIconUrl,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
      });

      // Remove the start marker if it exists
      if (this.startMarker) {
        this.map.removeLayer(this.startMarker);
        this.startMarker = null;
      }

      // Create or update the moving marker
      if (this.simMarker) {
        this.simMarker.setLatLng(start);
      } else {
        this.simMarker = L.marker(start, { icon: ambulanceIcon }).addTo(this.map);
      }

      this.map.panTo(start);
      this.simulateStep();
    },
    confirmGoBack() {
      if (this.websocket) {
        this.websocket.close();
      }
      localStorage.removeItem("websocket");
      this.$router.push("/");
    },
    resumeSimulation() {
      if (!this.polyline || this.speedKmh <= 0) {
        alert("Please select a speed greater than 0.");
        return;
      }

      if (this.isPaused) {
        this.isPaused = false;
        this.lastTimestamp = null;
        this.simulateStep();
      }
    },
    pauseSimulation() {
      this.isPaused = true;
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    },
    stopSimulation() {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    },
    onSpeedChange() {
      if (!this.isPaused && this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId);
        this.lastTimestamp = null;
        this.simulateStep();
      }
    },
    simulateStep() {
      const latlngs = this.polyline.getLatLngs();
      const totalDistance = this.calculateTotalDistance(latlngs);
      const speedMs = Math.max(this.speedKmh / 3.6, 0.1); // m/s

      const animate = (timestamp) => {
        if (this.isPaused) return;

        if (!this.lastTimestamp) this.lastTimestamp = timestamp;
        const elapsed = (timestamp - this.lastTimestamp) / 1000;
        this.lastTimestamp = timestamp;

        this.pausedDistance += speedMs * elapsed;

        if (this.pausedDistance >= totalDistance) {
          const finalPoint = latlngs[latlngs.length - 1];
          this.simMarker.setLatLng(finalPoint);
          this.map.panTo(finalPoint);
          return;
        }

        const newPos = this.interpolateLatLng(latlngs, this.pausedDistance);
        this.simMarker.setLatLng(newPos);
        this.map.panTo(newPos);

        // Send coordinates to the WebSocket server
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
          this.websocket.send(JSON.stringify({ coordinates: newPos }));
        }

        this.animationFrameId = requestAnimationFrame(animate);
      };

      this.animationFrameId = requestAnimationFrame(animate);
    },
    calculateTotalDistance(latlngs) {
      let total = 0;
      for (let i = 0; i < latlngs.length - 1; i++) {
        total += latlngs[i].distanceTo(latlngs[i + 1]);
      }
      return total;
    },
    interpolateLatLng(latlngs, distance) {
      let accumulated = 0;

      for (let i = 0; i < latlngs.length - 1; i++) {
        const segmentDistance = latlngs[i].distanceTo(latlngs[i + 1]);

        if (accumulated + segmentDistance >= distance) {
          const overshoot = distance - accumulated;
          const ratio = overshoot / segmentDistance;

          const lat = latlngs[i].lat + (latlngs[i + 1].lat - latlngs[i].lat) * ratio;
          const lng = latlngs[i].lng + (latlngs[i + 1].lng - latlngs[i].lng) * ratio;

          return L.latLng(lat, lng);
        }

        accumulated += segmentDistance;
      }

      return latlngs[latlngs.length - 1];
    },
  },
  beforeDestroy() {
    if (this.websocket) {
      this.websocket.close();
    }
    localStorage.removeItem("websocket");
  },
};
</script>

<style scoped>
#map {
  height: 35rem;
  width: 100%;
}
.bg-gray-100 {
  background-color: #f7fafc;
}
.bg-white {
  background-color: #ffffff;
}
.rounded-lg {
  border-radius: 0.5rem;
}
.shadow-lg {
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}
.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}
.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}
.max-w-5xl {
  max-width: 80rem;
}
.fixed {
  position: fixed;
}
.inset-0 {
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
.bg-opacity-50 {
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}
.z-50 {
  z-index: 1050;
}
</style>