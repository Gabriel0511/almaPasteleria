<template>
  <div class="user-menu-container">
    <i class="fas fa-bell notf-icon" @click="toggleMenu">
      <span v-if="notificationCount > 0" class="notification-badge">
        {{ notificationCount }}
      </span>
    </i>
    <div v-if="isOpen" class="user-menu">
      <div class="menu-header">Notificaciones</div>
      <div
        class="menu-item"
        v-for="notification in notifications"
        :key="notification.id"
      >
        {{ notification.message }}
      </div>
      <div v-if="notifications.length === 0" class="menu-item">
        No hay notificaciones
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"; // ✅ AGREGAR import de computed

const props = defineProps({
  notifications: {
    type: Array,
    default: () => [],
  },
});

const isOpen = ref(false);
const notificationCount = computed(() => props.notifications.length); // ✅ Ahora computed está definido

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};
</script>
