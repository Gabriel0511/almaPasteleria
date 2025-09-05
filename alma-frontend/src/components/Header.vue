<template>
  <header class="header">
    <div class="header-left">
      <h1 class="page-title">{{ title }}</h1>
      <br />
      <div class="logo">
        <img src="/src/Logo2.png" alt="Logo Pastelería" />
      </div>
    </div>

    <div class="header-right">
      <!-- Botón de notificaciones -->
      <button class="icon-btn" @click="toggleNotfMenu">
        <i class="fas fa-bell"></i>
        <span v-if="unreadNotifications > 0" class="notification-badge">
          {{ unreadNotifications }}
        </span>
      </button>

      <!-- Menú de notificaciones -->
      <div v-if="showNotfMenu" class="dropdown-menu notification-menu">
        <h3>Notificaciones</h3>
        <div v-if="notifications.length === 0" class="empty-notifications">
          No hay notificaciones
        </div>
        <div v-else class="notification-list">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="notification-item"
            :class="{ unread: !notification.read }"
          >
            <div class="notification-content">
              <p class="notification-text">{{ notification.message }}</p>
              <span class="notification-time">
                {{ formatTime(notification.timestamp) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Botón de usuario -->
      <button class="icon-btn user-btn" @click="toggleUserMenu">
        <i class="fas fa-user-circle"></i>
        <span class="user-email">{{ userEmail }}</span>
      </button>

      <!-- Menú de usuario -->
      <div v-if="showUserMenu" class="dropdown-menu user-menu">
        <div class="user-info">
          <p>{{ userEmail }}</p>
        </div>
        <hr />
        <ul class="menu-options">
          <li @click="openChangePassword">
            <i class="fas fa-key"></i> Cambiar contraseña
          </li>
          <li @click="logout">
            <i class="fas fa-sign-out-alt"></i> Cerrar sesión
          </li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";

// ✅ Usamos route.meta.title
const route = useRoute();
const title = computed(() => route.meta.title || "Panel Principal");

const props = defineProps({
  userEmail: {
    type: String,
    default: "Usuario",
  },
});

const emit = defineEmits(["toggleSidebar", "openPasswordModal", "logout"]);

const showUserMenu = ref(false);
const showNotfMenu = ref(false);
const notifications = ref([]);

const unreadNotifications = computed(() => {
  return notifications.value.filter((n) => !n.read).length;
});

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
  showNotfMenu.value = false;
};

const toggleNotfMenu = () => {
  showNotfMenu.value = !showNotfMenu.value;
  showUserMenu.value = false;
};

const openChangePassword = () => {
  showUserMenu.value = false;
  emit("openPasswordModal");
};

const logout = () => {
  showUserMenu.value = false;
  emit("logout");
};

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString();
};

const handleClickOutside = (event) => {
  if (!event.target.closest(".header-right")) {
    showUserMenu.value = false;
    showNotfMenu.value = false;
  }
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>

<style scoped>
/* Tus estilos aquí */
</style>
