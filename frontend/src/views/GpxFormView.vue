<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-6 py-8">
    <!-- Container -->
    <div class="bg-gray-100 rounded-lg shadow-lg w-full max-w-lg p-6">
      <!-- Header -->
      <h1 class="text-4xl font-bold text-orange-500 mb-8 text-center">Simulate Travel</h1>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="flex flex-col items-center space-y-4">
        <!-- File Input -->
        <input
          type="file"
          accept=".gpx"
          @change="handleFileChange"
          class="border border-gray-300 rounded-lg p-2 w-full"
          required
        />

        <!-- Submit Button -->
        <button
          type="submit"
          class="bg-orange-500 text-white px-6 py-3 rounded-lg shadow hover:bg-orange-600"
        >
          Start Travel Simulation
        </button>
      </form>

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
import axios from "axios";

export default {
  name: "GpxFormView",
  data() {
    return {
      selectedFile: null,
    };
  },
  methods: {
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },
    async handleSubmit() {
      if (this.selectedFile) {
        const reader = new FileReader();
        reader.onload = async () => {
          const gpxContent = reader.result;

          // Store the GPX file content in localStorage
          localStorage.setItem("gpxData", gpxContent);

          // Parse the GPX file to extract coordinates
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(gpxContent, "application/xml");
          const GPX_NS = xmlDoc.documentElement.namespaceURI;
          const trackpoints = xmlDoc.getElementsByTagNameNS(GPX_NS, "trkpt");

          const coordinates = [];
          for (let i = 0; i < trackpoints.length; i++) {
            const lat = parseFloat(trackpoints[i].getAttribute("lat"));
            const lon = parseFloat(trackpoints[i].getAttribute("lon"));
            coordinates.push([lat, lon]);
          }


          if (coordinates.length === 0) {
            alert("No coordinates found in the GPX file.");
            return;
          }

          try {
            // Post the coordinates to the backend
            const csrfToken = document.cookie
              .split("; ")
              .find((row) => row.startsWith("csrftoken"))
              ?.split("=")[1];

            await axios.post(
              `${import.meta.env.VITE_BACKEND_API_URL}/route/`,
              { coordinates },
              {
                withCredentials: true,
                headers: {
                  "X-CSRFToken": csrfToken,
                },
              }
            );

            // Navigate to the simulation page
            this.$router.push("/simulate");
          } catch (error) {
            console.error("Error processing the request:", error);
            alert("Failed to process the request.");
          }
        };
        reader.readAsText(this.selectedFile);
      } else {
        alert("Please select a .gpx file before submitting.");
      }
    },
  },
};
</script>

<style scoped>
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

.max-w-lg {
  max-width: 32rem; /* Ensure the container is wide enough for the form */
}
</style>