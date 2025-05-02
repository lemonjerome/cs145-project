<script setup>
</script>

<template>
  <div>
    <!-- Background Image -->
    <div class="absolute inset-0">
      <img src="@/assets/images/gta-san-andreas-map.png" alt="GTA San Andreas Map" class="w-full h-full object-cover" />
    </div>

    <!-- White Overlay -->
    <div class="absolute inset-0 bg-white/85"></div>
    <div class="relative z-10 flex flex-col items-center justify-center min-h-screen">
      <router-view /> <!-- This renders the matched route's component -->
    </div>
  </div>
</template>

<style scoped>
</style>
