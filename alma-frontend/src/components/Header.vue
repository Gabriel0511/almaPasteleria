<template>
  <header class="header">
    <div class="header-left">
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

    <!-- Modal para cambiar contraseña -->
    <div v-if="showPasswordModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Cambiar contraseña</h3>
        <div class="form-group">
          <label>Contraseña actual:</label>
          <input type="password" v-model="currentPassword" class="form-input" />
        </div>
        <div class="form-group">
          <label>Nueva contraseña:</label>
          <input type="password" v-model="newPassword" class="form-input" />
        </div>
        <div class="form-group">
          <label>Repita la nueva contraseña:</label>
          <input type="password" v-model="confirmPassword" class="form-input" />
        </div>
        <div class="modal-buttons">
          <button @click="showPasswordModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="changePassword" class="confirm-button">
            Aceptar
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

const route = useRoute();
const router = useRouter();

const title = computed(() => route.meta.title || "Panel Principal");

// Variables reactivas
const userEmail = ref("Usuario");
const showUserMenu = ref(false);
const showNotfMenu = ref(false);
const showPasswordModal = ref(false);
const notifications = ref([]);
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

// Obtener email del usuario
const fetchUserProfile = async () => {
  try {
    const response = await axios.get("/api/auth/perfil/");
    userEmail.value = response.data.email || "Usuario";
  } catch (error) {
    console.error("Error al obtener perfil:", error);
  }
};

// Notificaciones
const unreadNotifications = computed(() => {
  return notifications.value.filter((n) => !n.read).length;
});

// Menús
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
  showNotfMenu.value = false;
};

const toggleNotfMenu = () => {
  showNotfMenu.value = !showNotfMenu.value;
  showUserMenu.value = false;
};

// Cambio de contraseña
const openChangePassword = () => {
  showUserMenu.value = false;
  showPasswordModal.value = true;
};

const changePassword = async () => {
  try {
    if (newPassword.value !== confirmPassword.value) {
      alert("Las contraseñas no coinciden");
      return;
    }

    await axios.post("/api/auth/cambiar-password/", {
      current_password: currentPassword.value,
      new_password: newPassword.value,
    });

    alert("Contraseña cambiada correctamente");
    showPasswordModal.value = false;
    resetPasswordForm();
  } catch (error) {
    console.error("Error al cambiar contraseña:", error);
    alert("Error al cambiar la contraseña");
  }
};

// Logout
const logout = async () => {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
      await axios.post("/api/auth/logout/", { refresh: refreshToken });
    }
  } catch (err) {
    console.error("Error al cerrar sesión:", err.response?.data || err);
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete axios.defaults.headers.common["Authorization"];
    router.push("/login");
  }
};

// Utilidades
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString();
};

const resetPasswordForm = () => {
  currentPassword.value = "";
  newPassword.value = "";
  confirmPassword.value = "";
};

const handleClickOutside = (event) => {
  if (!event.target.closest(".header-right")) {
    showUserMenu.value = false;
    showNotfMenu.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  document.addEventListener("click", handleClickOutside);
  fetchUserProfile();
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});
</script>
