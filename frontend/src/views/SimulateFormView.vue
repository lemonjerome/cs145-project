<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100">
    <h1 class="text-4xl font-bold text-green-500 mb-4">Route Simulation</h1>

    <!-- Speed & Buttons -->
    <form @submit.prevent class="mb-6 flex flex-col items-center gap-2">
      <label class="text-lg font-medium">Speed: {{ speedKmh }} km/h</label>
      <input
        type="range"
        min="0"
        max="220"
        step="5"
        v-model.number="speedKmh"
        class="w-80"
        @input="onSpeedChange"
      />
      <div class="flex gap-4 mt-2">
        <button type="button" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded" @click="startSimulation">Start</button>
        <button type="button" class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded" @click="resumeSimulation">Resume</button>
        <button type="button" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded" @click="pauseSimulation">Pause</button>
      </div>
    </form>

    <!-- Map -->
    <div class="flex flex-col items-center w-full max-w-2xl">
      <div id="map" class="w-full h-96 border border-gray-300 rounded-lg"></div>
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
      this.simulateStep();
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
};
</script>

<style scoped>
#map {
  height: 35rem;
  width: 70rem;
}
</style>