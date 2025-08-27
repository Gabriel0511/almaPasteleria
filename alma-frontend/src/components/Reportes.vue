<template>
  <Sidebar @navigate="handleNavigation" />
  <div>Hola muuy buenas a todos gapisimos</div>
</template>

<script setup>
import { useRouter } from "vue-router";
import Sidebar from "./Sidebar.vue"; // Ajusta la ruta según tu estructura

const router = useRouter();

const handleNavigation = (route) => {
  router.push(route);
};
</script>
