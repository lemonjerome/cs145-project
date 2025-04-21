<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100">
    <!-- Header -->
    <h1 class="text-4xl font-bold text-orange-500 mb-8">Simulate Travel</h1>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="flex flex-col items-center space-y-4">
      <!-- File Input -->
      <input
        type="file"
        accept=".gpx"
        @change="handleFileChange"
        class="border border-gray-300 rounded-lg p-2 w-80"
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
    <router-link to="/" class="mt-6">
      <button class="bg-gray-500 text-white px-6 py-3 rounded-lg shadow hover:bg-gray-600">
        Go Back
      </button>
    </router-link>
  </div>
</template>

<script>
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
    handleSubmit() {
      if (this.selectedFile) {
        // Read the file content as text
        const reader = new FileReader();
        reader.onload = () => {
          const gpxContent = reader.result;
          // Store the GPX file content in localStorage
          localStorage.setItem("gpxData", gpxContent);
          // Navigate to the simulation page
          this.$router.push("/simulate");
        };
        reader.readAsText(this.selectedFile); // Read the selected GPX file
      } else {
        alert("Please select a .gpx file before submitting.");
      }
    },
  },
};
</script>

<style scoped>
/* Add any additional styles here if needed */
</style>