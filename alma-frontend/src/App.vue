<template>
  <div id="app">
    <NotificationSystem ref="notificationSystem" />
    <RouterView />
  </div>
</template>

<script setup>
import { ref, provide } from "vue";
import NotificationSystem from "./components/NotificationSystem.vue";

const notificationSystem = ref();

// Proveer el sistema de notificaciones a todos los componentes
provide("notifications", {
  show: (data) => notificationSystem.value?.showNotification(data),
  remove: (id) => notificationSystem.value?.removeNotification(id),
});
</script>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
