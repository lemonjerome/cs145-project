<template>
  <div class="relative min-h-screen flex items-center justify-center">
    <!-- Background Image -->
    <div class="absolute inset-0">
      <img src="../assets/images/gta-san-andreas-map.png" alt="GTA San Andreas Map" class="w-full h-full object-cover" />
    </div>

    <!-- White Overlay -->
    <div class="absolute inset-0 bg-white/85"></div>

    <!-- Content -->
    <div class="relative z-10 flex flex-col items-center">
      <!-- SVG Icons -->
      <div class="flex space-x-4 mb-8">
        <img src="../assets/svg/ambulance-svgrepo-com.svg" alt="Ambulance" class="h-20 w-20" />
        <img src="../assets/svg/police-car-svgrepo-com.svg" alt="Police Car" class="h-20 w-20" />
        <img src="../assets/svg/fire-truck-transport-svgrepo-com.svg" alt="Fire Truck" class="h-20 w-20" />
      </div>

      <!-- Title and Subheader -->
      <h1 class="text-4xl font-bold text-gray-800">Tabipo</h1>
      <p class="text-lg text-gray-600 mt-2">A stoplight and route priority application for emergency vehicles</p>

      <!-- Buttons -->
      <div class="flex flex-col items-center space-y-4 mt-8">
        <router-link to="/destination">
          <button class="bg-green-500 text-white px-6 py-3 rounded-lg shadow hover:bg-green-600">
            Live travel
          </button>
        </router-link>
        <router-link to="/send_route">
          <button class="bg-orange-500 text-white px-6 py-3 rounded-lg shadow hover:bg-orange-600">
            Simulate travel
          </button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LandingPageView",
};
</script>

<style scoped>
/* Add any additional styles here if needed */
</style>