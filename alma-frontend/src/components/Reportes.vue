<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";

const router = useRouter();

const handleNavigation = (route) => {
  router.push(route);
};

// Referencia al sidebar para controlarlo desde el header
const sidebarRef = ref(null);

// Método para alternar el sidebar desde el header
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};


</script>