<template>
  <header class="header">
    <!-- Botón hamburguesa para móviles -->
    <button
      class="hamburger-btn-mobile"
      @click="$emit('toggle-sidebar')"
      v-if="isMobile"
    >
      <i class="fas fa-bars"></i>
    </button>

    <div class="header-left">
      <br />
      <div class="date-text">
        <i class="fas fa-calendar-alt date-icon"></i>
        <div class="date-content">
          <div class="date-day">{{ dayOfWeek }}</div>
          <div class="date-full">{{ formattedDate }}</div>
        </div>
      </div>
      <div class="logo" @click="goToHome">
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

      <!-- En el template de Header.vue, MODIFICAR la sección de notificaciones: -->
      <div v-if="showNotfMenu" class="dropdown-menu notification-menu">
        <div class="notification-header">
          <h3>Notificaciones</h3>
        </div>

        <div
          v-if="todasLasNotificaciones.length === 0"
          class="empty-notifications"
        >
          <i class="fas fa-bell-slash"></i>
          <p>No hay notificaciones</p>
        </div>

        <div v-else class="notification-list">
          <div
            <div
              v-for="notification in todasLasNotificaciones"
              :key="notification.id"
              class="notification-item"
              :class="[notification.type, { unread: !notification.read }]"
              @click="handleNotificationClick(notification)"
            >
              <div class="notification-content">
                <div class="notification-title-row">
                  <!-- Mover el icono aquí, al lado del título -->
                  <div class="notification-icon">
                    <i
                      class="fas"
                      :class="{
                        'fa-exclamation-triangle': notification.type === 'critical',
                        'fa-exclamation-circle': notification.type === 'warning',
                        'fa-info-circle': notification.type === 'info',
                        'fa-check-circle': notification.type === 'success',
                      }"
                    ></i>
                  </div>
                  <strong class="notification-title">{{ notification.title }}</strong>
                  <span class="notification-time">
                    {{ formatTime(notification.timestamp) }}
                  </span>
                </div>
                <p class="notification-text">{{ notification.message }}</p>

              <!-- Acciones rápidas -->
              <div
                v-if="notification.item && !notification.read"
                class="notification-actions"
              >
                <button
                  @click.stop="router.push('/stock')"
                  class="btn-action-small"
                >
                  <i class="fas fa-box"></i> Ver Stock
                </button>
              </div>
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
import { ref, computed, onMounted, onUnmounted, inject, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

const route = useRoute();
const router = useRouter();
const notificationSystem = inject("notifications");

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
const notificacionesStock = ref([]);
const notificacionesRecetas = ref([]);
const notificacionesPedidos = ref([]);

const isMobile = ref(false);
const emit = defineEmits(["toggle-sidebar"]);

// MODIFICAR: Fecha actual sin "de" antes del año
const currentDate = ref(new Date());
const dayOfWeek = computed(() => {
  return currentDate.value.toLocaleDateString('es-ES', { 
    weekday: 'long' 
  });
});
const formattedDate = computed(() => {
  const day = currentDate.value.getDate();
  const month = currentDate.value.toLocaleDateString('es-ES', { 
    month: 'long' 
  });
  const year = currentDate.value.getFullYear();
  
  return `${day} de ${month} ${year}`; // ← Quitamos el "de" antes del año
});


const checkScreenSize = () => {
  isMobile.value = window.innerWidth <= 768;
};

const toggleMobileSidebar = () => {
  emit("toggle-sidebar");
};

onMounted(() => {
  checkScreenSize();
  window.addEventListener("resize", checkScreenSize);
  
  // AGREGAR: Actualizar la fecha cada día
  const updateDate = () => {
    currentDate.value = new Date();
  };
  
  // Actualizar a medianoche
  const now = new Date();
  const midnight = new Date(now);
  midnight.setHours(24, 0, 0, 0);
  const timeUntilMidnight = midnight - now;
  
  setTimeout(() => {
    updateDate();
    // Actualizar cada 24 horas
    setInterval(updateDate, 24 * 60 * 60 * 1000);
  }, timeUntilMidnight);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkScreenSize);
});

// AGREGAR: Método para ir a la página principal
const goToHome = () => {
  router.push("/inicio");
};

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
  return todasLasNotificaciones.value.filter((n) => !n.read).length;
});

const todasLasNotificaciones = computed(() => {
  return [
    ...notificacionesStock.value,
    ...notificacionesRecetas.value,
    ...notificacionesPedidos.value,
  ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
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

const cargarNotificacionesStock = async () => {
  try {
    const response = await axios.get("/api/insumos/");
    const insumos = response.data.insumos;

    notificacionesStock.value = [];

    // Stock crítico
    insumos
      .filter((item) => {
        const cantidad = parseFloat(item.stock_actual);
        const minimo = parseFloat(item.stock_minimo);
        return cantidad <= minimo * 0.5;
      })
      .forEach((item) => {
        notificacionesStock.value.push({
          id: `stock-critico-${item.id}`,
          type: "critical",
          title: "Stock Crítico",
          message: `${item.nombre} está en nivel crítico (${item.stock_actual} ${item.unidad_medida.abreviatura})`,
          timestamp: new Date(),
          read: false,
          item: item,
        });
      });

    // Stock bajo
    insumos
      .filter((item) => {
        const cantidad = parseFloat(item.stock_actual);
        const minimo = parseFloat(item.stock_minimo);
        return cantidad <= minimo && cantidad > minimo * 0.5;
      })
      .forEach((item) => {
        notificacionesStock.value.push({
          id: `stock-bajo-${item.id}`,
          type: "warning",
          title: "Stock Bajo",
          message: `${item.nombre} está por debajo del mínimo (${item.stock_actual}/${item.stock_minimo} ${item.unidad_medida.abreviatura})`,
          timestamp: new Date(),
          read: false,
          item: item,
        });
      });
  } catch (error) {
    console.error("Error cargando notificaciones de stock:", error);
  }
};

const cargarNotificacionesRecetas = async () => {
  try {
    const response = await axios.get("/api/recetas/");
    const recetas = response.data;

    // Cargar notificaciones leídas
    const leidasGuardadas = JSON.parse(
      localStorage.getItem("notificacionesLeidas") || "[]"
    );

    notificacionesRecetas.value = recetas
      .filter((receta) => {
        const costo = parseFloat(receta.costo_total) || 0;
        const venta = parseFloat(receta.precio_venta) || 0;
        return venta <= costo;
      })
      .filter((receta) => {
        // Filtrar solo las no marcadas como leídas
        const notificacionId = `receta-no-rentable-${receta.id}`;
        return !leidasGuardadas.includes(notificacionId);
      })
      .map((receta) => ({
        id: `receta-no-rentable-${receta.id}`,
        type: "warning",
        title: `${receta.nombre} NO es rentable.`,
        message: `Perdida de: $${receta.costo_total - receta.precio_venta}`,
        timestamp: new Date(),
        read: false,
        receta: receta,
      }));
  } catch (error) {
    console.error("Error cargando notificaciones de recetas:", error);
  }
};

const cargarNotificacionesPedidos = async () => {
  try {
    const response = await axios.get("/api/pedidos/hoy/");
    const hoy = new Date().toDateString();

    notificacionesPedidos.value = [];

    // Pedidos atrasados
    response.data.hacer_hoy
      .filter((pedido) => {
        const fechaEntrega = new Date(pedido.fecha_entrega).toDateString();
        return fechaEntrega < hoy && pedido.estado !== "entregado";
      })
      .forEach((pedido) => {
        notificacionesPedidos.value.push({
          id: `pedido-atrasado-${pedido.id}`,
          type: "critical",
          title: "Pedido Atrasado",
          message: `Pedido de ${pedido.cliente.nombre} está atrasado`,
          timestamp: new Date(),
          read: false,
          pedido: pedido,
        });
      });

    // Pedidos para hoy
    response.data.entregar_hoy
      .filter((pedido) => {
        const fechaEntrega = new Date(pedido.fecha_entrega).toDateString();
        return fechaEntrega === hoy && pedido.estado !== "entregado";
      })
      .forEach((pedido) => {
        notificacionesPedidos.value.push({
          id: `pedido-hoy-${pedido.id}`,
          type: "info",
          title: "Entrega Hoy",
          message: `Pedido de ${pedido.cliente.nombre} debe entregarse hoy`,
          timestamp: new Date(),
          read: false,
          pedido: pedido,
        });
      });
  } catch (error) {
    console.error("Error cargando notificaciones de pedidos:", error);
  }
};

// AGREGAR: Método para cargar todas las notificaciones
const cargarTodasLasNotificaciones = async () => {
  await Promise.all([
    cargarNotificacionesStock(),
    cargarNotificacionesRecetas(),
    cargarNotificacionesPedidos(),
  ]);
};

// AGREGAR: Método para manejar clic en notificación
const handleNotificationClick = (notification) => {

  // Navegar según el tipo
  if (notification.item) {
    router.push("/stock");
  } else if (notification.receta) {
    router.push("/recetas");
  } else if (notification.pedido) {
    router.push("/pedidos");
  }

  showNotfMenu.value = false;
};


// AGREGAR watcher para recargar notificaciones al cambiar de ruta
watch(
  () => route.path,
  () => {
    // Recargar notificaciones cuando el usuario navega
    cargarTodasLasNotificaciones();
  }
);

// AGREGAR método para forzar actualización (útil desde otros componentes)
const actualizarNotificaciones = () => {
  cargarTodasLasNotificaciones();
};

// Exponer el método para otros componentes
defineExpose({
  actualizarNotificaciones: cargarTodasLasNotificaciones,
});
// Utilidades
const formatTime = (timestamp) => {
  return ""; 
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
  cargarTodasLasNotificaciones();

  // Recargar notificaciones cada 5 minutos
  const interval = setInterval(cargarTodasLasNotificaciones, 5 * 60 * 1000);
  onUnmounted(() => clearInterval(interval));
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
  gap: 15px;
}

.date-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  padding: 0;
  background: none;
  border: none;
  box-shadow: none;
  backdrop-filter: none;
}

.date-icon {
  font-size: 1.6rem;
  color: rgba(255, 255, 255, 0.9);
  opacity: 0.8;
}

.date-content {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.date-day {
  font-size: 1.0rem;
  font-weight: 600;
  text-transform: capitalize;
  opacity: 0.9;
  margin-bottom: 1px;
  white-space: nowrap;
}

.date-full {
  font-size: 1.4rem;
  font-weight: 500;
  text-transform: capitalize;
  white-space: nowrap;
}


.logo {
  cursor: pointer; /* Hace que aparezca la manito al pasar el mouse */
  transition: transform 0.3s ease;
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

/* Encabezado de notificaciones */
.notification-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
  background-color: rgba(123, 90, 80, 0.1);
}

.notification-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--color-primary);
}

/* Ícono de notificación */
.notification-icon {
  margin-right: 0; /* Ya no necesita margen derecho */
  color: #6c757d;
  font-size: 0.9rem; /* Tamaño similar al título */
  display: flex;
  align-items: center;
}

.notification-item.critical .notification-icon {
  color: #e74c3c;
}

.notification-item.warning .notification-icon {
  color: #f39c12;
}

.notification-item.info .notification-icon {
  color: #3498db;
}

.notification-item.success .notification-icon {
  color: #28a745; /* Agregar color para éxito */
}

/* Contenido de notificación mejorado */
.notification-title-row {
  display: flex;
  align-items: center; /* Centra verticalmente los elementos */
  gap: 8px; /* Espacio entre icono, título y hora */
  margin-bottom: 5px;
}

.notification-title {
  font-size: 1.0rem;
  margin: 0;
  color: var(--color-text);
  flex: 1px
}

.notification-time {
  font-size: 0.7rem;
  color: #6c757d;
  white-space: nowrap;
}

.notification-text {
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.3;
  color: #495057;
}

/* Acciones de notificación */
.notification-actions {
  margin-top: 8px;
}

.btn-action-small {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-action-small:hover {
  background: #8b6b61;
}

/* Estados de notificación */
.notification-item.unread {
  background: rgba(52, 152, 219, 0.05);
  border-left: 3px solid #3498db;
}

.notification-item.critical {
  border-left: 3px solid #e74c3c;
}

.notification-item.warning {
  border-left: 3px solid #f39c12;
}

.notification-item.info {
  border-left: 3px solid #3498db;
}

/* Empty state mejorado */
.empty-notifications {
  padding: 40px 20px;
  text-align: center;
  color: #6c757d;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.empty-notifications i {
  font-size: 2rem;
  opacity: 0.5;
}

.empty-notifications p {
  margin: 0;
  font-style: italic;
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .header {
    padding: 10px 15px 10px 60px !important;
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
    padding: 8px 10px 8px 50px !important;
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

/* Botón hamburguesa para móviles en el header */
.hamburger-btn-mobile {
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  padding: 8px;
  margin-right: 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1002;
}

/* Ajustar el header para móviles */
@media (max-width: 768px) {
  .header {
    padding: 10px 15px 10px 60px !important; /* Más padding izquierdo para el botón */
    position: relative;
  }

  .hamburger-btn-mobile {
    display: block;
  }

  .header-left {
    justify-content: center;
    width: 100%;
  }

  .logo {
    position: relative;
    left: auto;
    transform: none;
  }

  .logo img {
    height: 60px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 8px 10px 8px 50px !important;
  }

  .hamburger-btn-mobile {
    left: 10px;
    font-size: 1.3rem;
    padding: 6px;
  }
}
</style>
