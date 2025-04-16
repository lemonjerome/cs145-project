<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100">
    <!-- Header -->
    <h1 class="text-4xl font-bold text-green-500 mb-8">Live Travel</h1>

    <!-- Current GPS Position -->
    <div class="flex items-center space-x-4 mb-6">
      <input
        type="text"
        v-model="currentPosition"
        readonly
        class="border border-gray-300 rounded-lg p-2 w-80 bg-gray-200"
        placeholder="Current GPS Position"
      />
      <button
        @click="getCurrentPosition"
        class="bg-green-500 text-white px-4 py-2 rounded-lg shadow hover:bg-green-600"
      >
        Get Position
      </button>
    </div>

    <!-- Destination Search -->
    <div class="flex flex-col items-center w-full max-w-2xl">
      <input
        type="text"
        v-model="destination"
        @input="searchDestination"
        class="border border-gray-300 rounded-lg p-2 w-full mb-4"
        placeholder="Search Destination"
      />
      <div id="map" class="w-full h-96 border border-gray-300 rounded-lg"></div>
    </div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon from "../assets/svg/location-pin-svgrepo-com.svg";

export default {
  name: "DestinationFormView",
  data() {
    return {
      currentPosition: "",
      destination: "",
      map: null,
      marker: null,
    };
  },
  methods: {
    getCurrentPosition() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            this.currentPosition = `${latitude}, ${longitude}`;
            if (this.map) {
              this.map.setView([latitude, longitude], 13);
            }
          },
          (error) => {
            alert("Unable to retrieve your location.");
          }
        );
      } else {
        alert("Geolocation is not supported by your browser.");
      }
    },
    searchDestination() {
      // Use Leaflet's geocoding or a third-party API for destination search
      if (this.destination) {
        // Example: Simulate a destination search result
        const simulatedLatLng = [37.7749, -122.4194]; // Example: San Francisco
        if (this.marker) {
          this.marker.setLatLng(simulatedLatLng);
        } else {
          this.marker = L.marker(simulatedLatLng, {
            icon: L.icon({
              iconUrl: markerIcon,
              iconSize: [40, 40],
            }),
          }).addTo(this.map);
        }
        this.map.setView(simulatedLatLng, 13);
      }
    },
  },
  mounted() {
    // Initialize the Leaflet map
    this.map = L.map("map").setView([37.7749, -122.4194], 13); // Default to San Francisco
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(this.map);
  },
};
</script>

<style scoped>
#map {
  height: 24rem; /* Adjust height as needed */
}
</style>