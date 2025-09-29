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

<style scoped>
/* ----------------------------- HEADER PRINCIPAL ----------------------------- */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30px 20px 25px 150px;
  background-color: var(--color-primary);
  box-shadow: 0 2px 4px var(--color-background);
  position: relative;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo img {
  height: 80px;
  width: auto;
  transition: transform 0.3s ease;
}

.logo img:hover {
  transform: scale(1.05);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  position: relative;
  height: 100%; /* Aseguramos que tome toda la altura */
}

/* ----------------------------- BOTONES DE ICONOS ----------------------------- */
.icon-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: white;
  position: relative;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.icon-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.icon-btn i {
  font-size: 1.3rem;
  color: white;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.user-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.user-email {
  color: white;
  font-size: 0.9rem;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ----------------------------- BADGE DE NOTIFICACIONES ----------------------------- */
.notification-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  background: var(--color-danger);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.7rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7);
  }
  70% {
    transform: scale(1.05);
    box-shadow: 0 0 0 4px rgba(220, 53, 69, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
  }
}

/* ----------------------------- MENÚS DESPLEGABLES ----------------------------- */
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 10px;
  box-shadow: 10px 8px 10px #aaa;
  border: 1px solid #ddd;
  min-width: 300px;
  z-index: 1001;
  animation: slideDown 0.3s ease;
  margin-top: 10px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-menu::before {
  content: "";
  position: absolute;
  top: -8px;
  right: 20px;
  width: 16px;
  height: 16px;
  background: white;
  transform: rotate(45deg);
  border-left: 1px solid #ddd;
  border-top: 1px solid #ddd;
}

/* ----------------------------- MENÚ DE NOTIFICACIONES ----------------------------- */
.notification-menu {
  right: 178px;
  top: calc(100% + 5px);
  margin-top: 0;
}

.notification-menu::before {
  right: 15px; /* Ajustamos la flechita para que esté centrada */
}

.notification-menu h3 {
  padding: 15px 20px;
  margin: 0;
  font-size: 1.2rem;
  color: var(--color-primary);
  border-bottom: 1px solid #ddd;
  background-color: rgba(123, 90, 80, 0.1);
}

.empty-notifications {
  padding: 40px 20px;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
  cursor: pointer;
}

.notification-item:hover {
  background-color: rgba(123, 90, 80, 0.05);
}

.notification-item.unread {
  background: rgba(52, 152, 219, 0.05);
  border-left: 3px solid #3498db;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.notification-text {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.4;
  color: var(--color-text);
}

.notification-time {
  font-size: 0.75rem;
  color: #6c757d;
}

/* ----------------------------- MENÚ DE USUARIO ----------------------------- */
.user-menu {
  right: 60px;
  top: calc(100% + 5px);
  margin-top: 0;
}

.user-menu::before {
  right: 15px;
}

.user-info {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #ddd;
}

.user-info p {
  margin: 0;
  font-weight: 600;
  color: var(--color-primary);
  font-size: 1rem;
}

.user-menu hr {
  margin: 0;
  border: none;
  border-top: 1px solid #ddd;
}

.menu-options {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-options li {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: var(--color-text);
}

.menu-options li:hover {
  background-color: rgba(123, 90, 80, 0.1);
  color: var(--color-primary);
}

.menu-options li i {
  color: var(--color-primary);
  width: 16px;
  text-align: center;
}

/* ----------------------------- MODAL CAMBIAR CONTRASEÑA ----------------------------- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--color-white);
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 10px 8px 10px #aaa;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: var(--color-primary);
  font-size: 1.3rem;
  text-align: center;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: var(--color-text);
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.cancel-button {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  color: var(--color-text);
}

.cancel-button:hover {
  background-color: #e0e0e0;
}

.confirm-button {
  padding: 8px 16px;
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.confirm-button:hover {
  background-color: #5a3f36;
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .header {
    padding: 10px 15px;
  }

  .logo img {
    height: 60px;
  }

  .header-right {
    gap: 10px;
  }

  .user-email {
    display: none;
  }

  .dropdown-menu {
    min-width: 280px;
    right: -10px;
  }

  .notification-menu {
    right: 50px;
  }

  .modal-content {
    margin: 20px;
    padding: 15px;
  }

  .modal-buttons {
    flex-direction: column;
  }

  .cancel-button,
  .confirm-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 8px 10px;
  }

  .dropdown-menu {
    min-width: 250px;
    right: -15px;
  }

  .notification-menu {
    right: 40px;
  }

  .notification-item {
    padding: 12px 15px;
  }

  .user-menu {
    min-width: 200px;
  }

  .menu-options li {
    padding: 10px 15px;
  }
}
</style>
