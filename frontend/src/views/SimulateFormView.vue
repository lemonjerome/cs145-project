<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-6 py-8">
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
      websocket: null,
      showModal: false, // State for showing the confirmation modal
    };
  },
  mounted() {
    this.map = L.map("map").setView([42.438878, -71.119277], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(this.map);

    const gpxData = localStorage.getItem("gpxData");

    if (gpxData) {
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(gpxData, "application/xml");

      // GPX_NS depends on gpx version used
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
  methods: {
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
      if (this.simMarker) {
        this.simMarker.setLatLng(start);
      } else {
        this.simMarker = L.marker(start).addTo(this.map);
      }

      this.map.panTo(start);

      // Establish WebSocket connection
      this.websocket = new WebSocket("ws://localhost:8000/ws/simulation/");
      this.websocket.onopen = () => {
        console.log("WebSocket connection established.");
      };
      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data.message);
      };
      this.websocket.onclose = () => {
        console.log("WebSocket connection closed.");
      };

      this.simulateStep();
    },
    confirmGoBack() {
      // Close the WebSocket connection
      if (this.websocket) {
        this.websocket.close();
      }
      // Navigate back to the home page
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
        this.simulateStep(); // Restart animation with updated speed
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
  },
};
</script>

<style scoped>
#map {
  height: 35rem;
  width: 100%; /* Ensure the map takes the full width of its container */
}

.bg-gray-100 {
  background-color: #f7fafc; /* Light gray background for the page */
}

.bg-white {
  background-color: #ffffff; /* White background for the container */
}

.rounded-lg {
  border-radius: 0.5rem; /* Rounded corners for elements */
}

.shadow-lg {
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
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
  max-width: 80rem; /* Wider container for better map display */
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
  z-index: 1000; /* Ensure the overlay is above the map */
}

.z-50 {
  z-index: 1050; /* Ensure the modal is above the overlay */
}
</style>