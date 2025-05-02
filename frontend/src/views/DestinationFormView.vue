<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-6 py-8">
    <!-- Gray Container -->
    <div class="bg-gray-100 rounded-lg shadow-lg w-full min-w-4xl p-8">
      <!-- Header -->
      <h1 class="text-4xl font-bold text-green-500 mb-8 text-center">Live Travel</h1>

      <!-- Current GPS Position -->
        <div class="flex items-center space-x-4 mb-4">
          <input
            type="text"
            v-model="currentPosition"
            readonly
            class="border border-gray-300 rounded-lg p-2 w-full bg-gray-200"
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
        <input
          type="text"
          v-model="destination"
          @input="searchDestination"
          class="border border-gray-300 rounded-lg p-2 w-full mb-4"
          placeholder="Search Destination"
        />
        <div id="map" class="w-full h-96 border border-gray-300 rounded-lg"></div>

      <!-- Go Back Button -->
      <router-link to="/" class="mt-6 block text-center">
        <button class="bg-gray-500 text-white px-6 py-3 rounded-lg shadow hover:bg-gray-600">
          Go Back
        </button>
      </router-link>
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
      if (this.destination) {
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
    this.map = L.map("map").setView([37.7749, -122.4194], 13);
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

.bg-gray-100 {
  background-color: #f7fafc; /* Light gray background for the page */
}

.bg-gray-200 {
  background-color: #edf2f7; /* Slightly darker gray for the container */
}

.bg-white {
  background-color: #ffffff; /* White background for inner sections */
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

.p-6 {
  padding: 1.5rem; /* Padding for inner sections */
}

.p-8 {
  padding: 2rem; /* Padding for the outer container */
}

.max-w-4xl {
  max-width: 56rem; /* Wider container for better layout */
}
</style>