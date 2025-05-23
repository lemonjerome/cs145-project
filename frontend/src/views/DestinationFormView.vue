<template>
  <div class="min-h-screen w-full flex flex-col items-stretch justify-center px-2 sm:px-6 md:px-8 py-6">
    <!-- Gray Container -->
    <div class="bg-gray-100 rounded-lg shadow-lg w-full px-2 sm:px-6 md:px-8 py-6">
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
      </div>

      <!-- Destination Search -->
      <div class="flex items-center space-x-4 mb-4">
        <input
          type="text"
          v-model="destination"
          class="border border-gray-300 rounded-lg p-2 w-full bg-white-200"
          placeholder="Search Destination"
        />
        <button 
          @click="searchDestination"
          class="bg-green-500 text-white px-4 py-2 rounded-lg shadow hover:bg-green-600"
        >
          Trace Route
        </button>
      </div>

      <div id="map" class="w-full h-72 sm:h-96 border border-gray-300 rounded-lg"></div>

      <!-- Go Back Button -->
      <button
        class="bg-gray-500 text-white px-6 py-3 rounded-lg shadow hover:bg-gray-600 mt-6 w-full max-w-xs mx-auto"
        @click="showModal = true"
      >
        Go Back
      </button>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
      <div class="bg-white p-6 rounded-lg shadow-lg text-center max-w-xs sm:max-w-sm mx-auto">
        <h2 class="text-xl font-bold mb-4">Are you sure you want to go back?</h2>
        <p class="text-gray-600 mb-6">This will stop the simulation and disconnect from the server.</p>
        <div class="flex flex-col sm:flex-row justify-center gap-4">
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
import axios from 'axios';
import { useStoplightsStore } from "@/stores/stoplights";
import { watch } from "vue";
import trafficLightIcon from "@/assets/svg/traffic-light-svgrepo-com.svg";
import ambulanceIconUrl from "@/assets/svg/ambulance-svgrepo-com.svg";
import accidentIconUrl from "@/assets/svg/accident-svgrepo-com.svg";
import greenCircleIcon from "@/assets/svg/green-circle-svgrepo-com.svg";


export default {
  name: "DestinationFormView",
  data() {
    return {
      currentPosition: "",
      destination: "",
      map: null,
      positionMarker: null,
      destinationMarker: null,
      showModal: false,
      websocket:null, 
      watchId: null,
      routePolyline: null,
      gpxGenerated: false,
      groupMarkers: {},
      routeCoordinates: [],
      activatedMarker: null,
    };
  },
  setup() {
    const stoplightsStore = useStoplightsStore();
    return { stoplightsStore };
  },
  methods: {
    addActivatedMarker(latlng) {
      this.removeActivatedMarker(); // Remove existing marker if any

      const icon = L.icon({
        iconUrl: greenCircleIcon, // Use the green circle SVG
        iconSize: [170, 170], // Adjust size as needed
        iconAnchor: [88, 82], // Center the icon
      });

      // Add the green circle marker with a lower zIndexOffset
      this.activatedMarker = L.marker(latlng, { icon, zIndexOffset: -1000, opacity: 0.6}).addTo(this.map);
    },
    removeActivatedMarker() {
      if (this.activatedMarker) {
        this.map.removeLayer(this.activatedMarker);
        this.activatedMarker = null;
      }
    },
    startWatchingPosition() {
      if (navigator.geolocation) {
        this.watchId = navigator.geolocation.watchPosition(
          (position) => {
            const { latitude, longitude } = position.coords;

            this.currentPosition = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;

            if (this.currentPosition && this.websocket && this.websocket.readyState === WebSocket.OPEN) {
              this.websocket.send(JSON.stringify({ lat: latitude, lng: longitude }));
            }

            if (this.map) {
              if (this.positionMarker) {
                this.positionMarker.setLatLng([latitude, longitude]);
              } else {
                this.positionMarker = L.marker([latitude, longitude], {
                  icon: L.icon({
                  iconUrl: ambulanceIconUrl,
                  iconSize: [32, 32],
                  iconAnchor: [16, 20],
                }),
                }).addTo(this.map);
              }
            }
            this.fitMarkersInView();

            if (this.destinationMarker) {
              this.traceRoute([latitude, longitude], this.destinationMarker.getLatLng());
            }
          },
          (error) => {
            alert("Unable to retrieve your location.");
          },
          { 
            enableHighAccuracy: true, 
            timeout: 5000,
            maximumAge: 0 
          }
        );
      } else {
        alert("Geolocation is not supported by your browser.");
      }
    },
    async searchDestination() {
      if (!this.destination) return;

      // Try parsing as lat,lng coords first
      const coords = this.destination.split(",").map(coord => parseFloat(coord.trim()));

      if (coords.length === 2 && !coords.some(isNaN)) {
        // It's valid coordinates
        this.gpxGenerated = true;

        if (this.destinationMarker) {
          this.destinationMarker.setLatLng(coords);
        } else {
          this.destinationMarker = L.marker(coords, {
            icon: L.icon({
              iconUrl: accidentIconUrl,
              iconSize: [32, 32],
              iconAnchor: [16, 32],
            }),
          }).addTo(this.map);
        }

        if (this.positionMarker) {
          this.traceRoute(this.positionMarker.getLatLng(), L.latLng(coords));
        }
        this.fitMarkersInView();

      } else {
        // Otherwise, treat as landmark name and query Nominatim
        try {
          const query = encodeURIComponent(this.destination);
          const url = `https://nominatim.openstreetmap.org/search?q=${query}&format=json&limit=1`;

          const response = await fetch(url, {
            headers: {
              "Accept": "application/json",
            }
          });
          const data = await response.json();

          if (data.length === 0) {
            alert("No results found for that landmark.");
            return;
          }

          const place = data[0];
          const lat = parseFloat(place.lat);
          const lon = parseFloat(place.lon);

          this.gpxGenerated = true;

          if (this.destinationMarker) {
            this.destinationMarker.setLatLng([lat, lon]);
          } else {
            this.destinationMarker = L.marker([lat, lon], {
              icon: L.icon({
                iconUrl: accidentIconUrl,
                iconSize: [32, 32],
                iconAnchor: [16, 32],
              }),
            }).addTo(this.map);
          }

          if (this.positionMarker) {
            this.traceRoute(this.positionMarker.getLatLng(), L.latLng([lat, lon]));
          }
          this.fitMarkersInView();

        } catch (error) {
          console.error("Nominatim search error:", error);
          alert("Error occurred while searching for the landmark.");
        }
      }
    },
    async placeStoplightsNearRoute() {
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

        const stoplight_groups = response.data.stoplight_groups; // <-- Use backend data only

        // console.log("Stoplights:", JSON.stringify(response.data.stoplight_groups));

        for (const stoplight_group of stoplight_groups) {
          const { lat, lng, groupID } = stoplight_group;

          const icon = L.icon({
            iconUrl: trafficLightIcon,
            iconSize: [32, 32],
            iconAnchor: [20, 15],
          });

          const marker = L.marker([lat, lng], { icon }).addTo(this.map);
          this.groupMarkers[groupID] = marker;

          await this.$nextTick(); // wait for Vue DOM updates, if needed
        }
      } else {
        alert("No GPX data found in localStorage.");
      }
    },
    fitMarkersInView() {
      const latLngs = [];

      if (this.positionMarker) {
        latLngs.push(this.positionMarker.getLatLng());
      }

      if (this.destinationMarker) {
        latLngs.push(this.destinationMarker.getLatLng());
      }

      if (latLngs.length >= 2) {
        this.map.fitBounds(L.latLngBounds(latLngs), { padding: [50, 50] });
      } else if (latLngs.length === 1) {
        this.map.setView(latLngs[0], 40);
      }
    },
    async traceRoute(start, end) {
      // OSRM expects lng,lat format (GeoJSON standard)
      const startLat = start.lat || start[0];
      const startLng = start.lng || start[1];
      const endLat = end.lat || end[0];
      const endLng = end.lng || end[1];

      const osrmBaseUrl = import.meta.env.VITE_OSRM_URL;
      const osrmUrl = `${osrmBaseUrl}/route/v1/car/${startLng},${startLat};${endLng},${endLat}?geometries=geojson`;

      fetch(osrmUrl)
        .then((res) => res.json())
        .then(async (data) => {
          if (!data.routes || data.routes.length === 0) {
            alert("No route found.");
            return;
          }

          const route = data.routes[0].geometry;

          // Remove existing polyline if existing
          if (this.routePolyline) {
            this.map.removeLayer(this.routePolyline);
          }

          this.routePolyline = L.geoJSON(route, {
            style: { color: "blue", weight: 4, opacity: 0.7 },
          }).addTo(this.map);

          // Fit bounds to route for proper view
          this.map.fitBounds(this.routePolyline.getBounds(), { padding: [50, 50] });

          // Prepare coordinates as [lat, lng] pairs for backend
          const routeCoords = route.coordinates.map(([lng, lat]) => [lat, lng]);
          try {
            const csrfToken = document.cookie
              .split("; ")
              .find((row) => row.startsWith("csrftoken"))
              ?.split("=")[1];

            await axios.post(
              `${import.meta.env.VITE_BACKEND_API_URL}/route/`,
              { coordinates: routeCoords },
              {
                withCredentials: true,
                headers: {
                  "X-CSRFToken": csrfToken,
                },
              }
            );
            // Fetch stoplights after posting route
            await this.fetchStoplights();
          } catch (err) {
            console.error("Error sending route to backend:", err);
            alert("Failed to send route to backend.");
          }

          // Generate first OSRM route as a GPX file; basis of stoplights to show
          if (this.gpxGenerated) {
            const gpxContent = this.generateGpx(route.coordinates);
            localStorage.setItem("gpxData", gpxContent);
            this.gpxGenerated = false;

            console.log(gpxContent);

            await this.placeStoplightsNearRoute();
          }
        })
        .catch((err) => {
          console.error("Error fetching route:", err);
          alert("Failed to fetch route from OSRM.");
        });
    },
    generateGpx(coords) {
      // Create initial GPX file when trace route initiated
      const now = new Date().toISOString();

      const gpxHeader = `<?xml version="1.0" encoding="UTF-8"?>
    <gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.topografix.com/GPX/1/1 
                            http://www.topografix.com/GPX/1/1/gpx.xsd"
        creator="LiveTravelApp"
        version="1.1"
        xmlns="http://www.topografix.com/GPX/1/1">
      <metadata>
        <time>${now}</time>
      </metadata>
      <trk>
        <name>OSRM Route</name>
        <type>car</type>
        <trkseg>
    `;

      const gpxFooter = `
        </trkseg>
      </trk>
    </gpx>`;

      const gpxPoints = coords
        .map(([lng, lat], i) => {
          const time = new Date(Date.now() + i * 1000).toISOString(); // spaced timestamps every 1 sec
          return `      <trkpt lat="${lat}" lon="${lng}">
            <ele>0</ele>
            <time>${time}</time>
          </trkpt>`;
        })
        .join("\n");

      return gpxHeader + gpxPoints + gpxFooter;
    },
    confirmGoBack() {
      // Stop watching the position
      if (this.watchId !== null) {
        navigator.geolocation.clearWatch(this.watchId);
        this.watchId = null;
      }

      if (this.websocket) {
        this.websocket.close();
      }
      localStorage.removeItem("websocket");
      this.$router.push("/");
    },
    async fetchStoplights() {
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
      this.stoplightsStore.setStoplightGroups(response.data.stoplight_groups);
      this.stoplightsStore.setStoplights(response.data.stoplights);
    },
    updateStoplightMarkers() {
      // Remove old markers
      Object.values(this.groupMarkers).forEach(marker => this.map.removeLayer(marker));
      this.groupMarkers = {};
      // Add new markers from store
      this.stoplightsStore.stoplightGroups.forEach(group => {
        const { lat, lng, groupID } = group;
        const icon = L.icon({
          iconUrl: trafficLightIcon,
          iconSize: [32, 32],
          iconAnchor: [20, 15],
        });
        const marker = L.marker([lat, lng], { icon }).addTo(this.map);
        this.groupMarkers[groupID] = marker;
      });
    },
  },
  watch: {
    // Watch for changes in the Pinia store and update markers
    'stoplightsStore.stoplightGroups': {
      handler() {
        if (this.map) this.updateStoplightMarkers();
      },
      deep: true,
    },
  },
  mounted() {
    this.map = L.map("map").setView([0, 0], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(this.map);

    this.map.whenReady(() => {
      navigator.geolocation.getCurrentPosition(
        () => {
          this.startWatchingPosition();
        },
        (err) => {
          alert("Please enable location services to use this feature.");
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    });

    const init = async () => {
      try {
        const websocketUrl = `${import.meta.env.VITE_BACKEND_BASE_URL.replace(
          "https",
          "wss"
        )}/ws/live/`;
        this.websocket = new WebSocket(websocketUrl);

        this.websocket.onmessage = (event) => {
          const message = JSON.parse(event.data);

          if (message.activate === 1) {
            // Group activated
            this.activatedGroup = message.groupID;

            // Get the marker's screen position
            const marker = this.groupMarkers[message.groupID];
            if (marker) {
              this.addActivatedMarker(marker.getLatLng());
            }
          } else if (message.activate === 0) {
            // Group deactivated
            if (this.activatedGroup === message.groupID) {
              this.activatedGroup = null;
              this.removeActivatedMarker();
            }
          }
        };

        this.websocket.onopen = () => {
          console.log("WebSocket connection established.");

          // remove this later
          alert("Websocket connection established.")
        };

        this.websocket.onerror = (error) => {
          console.error("WebSocket error:", error);
          alert("Failed to establish WebSocket connection.");
        };

        this.websocket.onclose = () => {
          console.log("WebSocket connection closed.");

          // remove this later
          alert("Websocket connection closed.")
        };

      } catch (error) {
        console.error("Error during mounted init:", error);
      }
    };

    init(); // Call the inner async function
  },
  beforeUnmount() {
    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
  }
};
</script>

<style scoped>
.bg-opacity-50 {
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

#map {
  height: 35rem; /* Adjust height as needed */
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