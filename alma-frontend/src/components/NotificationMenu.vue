<!-- NotificationMenu.vue - VERSIÓN MEJORADA -->
<template>
  <div class="notification-menu-container">
    <i class="fas fa-bell notification-icon" @click="toggleMenu">
      <span v-if="totalNotificaciones > 0" class="notification-badge">
        {{ totalNotificaciones }}
      </span>
    </i>

    <div v-if="isOpen" class="notification-menu">
      <div class="menu-header">
        <h3>Notificaciones</h3>
        <button
          v-if="notificacionesNoLeidas.length > 0"
          @click="marcarTodasComoLeidas"
          class="btn-marcar-todas"
        >
          Marcar todas como leídas
        </button>
      </div>

      <div class="notification-list">
        <div
          v-if="notificacionesFiltradas.length === 0"
          class="empty-notifications"
        >
          <i class="fas fa-bell-slash"></i>
          <p>No hay notificaciones</p>
        </div>

        <div
          v-for="notif in notificacionesFiltradas"
          :key="notif.id"
          class="notification-item"
          :class="[notif.type, { unread: !notif.leida }]"
          @click="handleNotificationClick(notif)"
        >
          <div class="notification-icon-type">
            <i class="fas" :class="getNotificationIcon(notif.type)"></i>
          </div>

          <div class="notification-content">
            <div class="notification-header">
              <strong class="notification-title">{{ notif.title }}</strong>
              <span class="notification-time">{{
                formatTime(notif.timestamp)
              }}</span>
            </div>
            <p class="notification-message">{{ notif.message }}</p>

            <!-- Acciones específicas por tipo -->
            <div v-if="notif.item" class="notification-actions">
              <button @click.stop="reponerStock(notif.item)" class="btn-action">
                <i class="fas fa-bolt"></i> Reponer Stock
              </button>
            </div>
            <div v-else-if="notif.receta" class="notification-actions">
              <button
                @click.stop="editarReceta(notif.receta)"
                class="btn-action"
              >
                <i class="fas fa-edit"></i> Editar Receta
              </button>
            </div>
            <div v-else-if="notif.pedido" class="notification-actions">
              <button @click.stop="verPedido(notif.pedido)" class="btn-action">
                <i class="fas fa-eye"></i> Ver Pedido
              </button>
            </div>
          </div>

          <button
            @click.stop="eliminarNotificacion(notif.id)"
            class="btn-eliminar"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <div class="menu-footer">
        <div class="filter-tabs">
          <button
            v-for="filter in filters"
            :key="filter.key"
            @click="filterActive = filter.key"
            :class="{ active: filterActive === filter.key }"
            class="filter-tab"
          >
            {{ filter.label }} ({{ getFilterCount(filter.key) }})
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const notificationSystem = inject("notifications");

const props = defineProps({
  notificacionesStock: {
    type: Array,
    default: () => [],
  },
  notificacionesRecetas: {
    type: Array,
    default: () => [],
  },
  notificacionesPedidos: {
    type: Array,
    default: () => [],
  },
});

const isOpen = ref(false);
const filterActive = ref("all");
const notificacionesLeidas = ref(new Set());

// Filtros disponibles
const filters = [
  { key: "all", label: "Todas" },
  { key: "unread", label: "No leídas" },
  { key: "critical", label: "Críticas" },
  { key: "warning", label: "Advertencias" },
  { key: "info", label: "Información" },
];

// Combinar todas las notificaciones
const todasLasNotificaciones = computed(() => {
  return [
    ...props.notificacionesStock,
    ...props.notificacionesRecetas,
    ...props.notificacionesPedidos,
  ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
});

// Notificaciones filtradas
const notificacionesFiltradas = computed(() => {
  let filtered = todasLasNotificaciones.value;

  switch (filterActive.value) {
    case "unread":
      filtered = filtered.filter((n) => !notificacionesLeidas.value.has(n.id));
      break;
    case "critical":
    case "warning":
    case "info":
      filtered = filtered.filter((n) => n.type === filterActive.value);
      break;
  }

  return filtered;
});

const notificacionesNoLeidas = computed(() => {
  return todasLasNotificaciones.value.filter(
    (n) => !notificacionesLeidas.value.has(n.id)
  );
});

const totalNotificaciones = computed(() => notificacionesNoLeidas.value.length);

const getFilterCount = (filterKey) => {
  switch (filterKey) {
    case "all":
      return todasLasNotificaciones.value.length;
    case "unread":
      return notificacionesNoLeidas.value.length;
    case "critical":
      return todasLasNotificaciones.value.filter((n) => n.type === "critical")
        .length;
    case "warning":
      return todasLasNotificaciones.value.filter((n) => n.type === "warning")
        .length;
    case "info":
      return todasLasNotificaciones.value.filter((n) => n.type === "info")
        .length;
    default:
      return 0;
  }
};

const getNotificationIcon = (type) => {
  const icons = {
    critical: "fa-exclamation-triangle",
    warning: "fa-exclamation-circle",
    info: "fa-info-circle",
    success: "fa-check-circle",
  };
  return icons[type] || "fa-bell";
};

const formatTime = (timestamp) => {
  const now = new Date();
  const diffMs = now - new Date(timestamp);
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return "Ahora";
  if (diffMins < 60) return `Hace ${diffMins} min`;
  if (diffHours < 24) return `Hace ${diffHours} h`;
  return new Date(timestamp).toLocaleDateString();
};

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const handleNotificationClick = (notif) => {
  notificacionesLeidas.value.add(notif.id);

  // Navegar según el tipo de notificación
  if (notif.item) {
    router.push("/stock");
  } else if (notif.receta) {
    router.push("/recetas");
  } else if (notif.pedido) {
    router.push("/pedidos");
  }
};

const marcarTodasComoLeidas = () => {
  todasLasNotificaciones.value.forEach((notif) => {
    notificacionesLeidas.value.add(notif.id);
  });
};

const eliminarNotificacion = (id) => {
  notificacionesLeidas.value.add(id);
};

const reponerStock = (item) => {
  // Implementar lógica para reponer stock
  router.push("/stock");
  isOpen.value = false;
};

const editarReceta = (receta) => {
  // Implementar lógica para editar receta
  router.push("/recetas");
  isOpen.value = false;
};

const verPedido = (pedido) => {
  // Implementar lógica para ver pedido
  router.push("/pedidos");
  isOpen.value = false;
};
</script>

<style scoped>
.notification-menu-container {
  position: relative;
}

.notification-icon {
  position: relative;
  cursor: pointer;
  font-size: 1.2rem;
  color: #6c757d;
  transition: color 0.3s ease;
}

.notification-icon:hover {
  color: var(--color-primary);
}

.notification-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #e74c3c;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.notification-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 400px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.menu-header {
  padding: 15px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-header h3 {
  margin: 0;
  color: var(--color-primary);
}

.btn-marcar-todas {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-marcar-todas:hover {
  color: var(--color-primary);
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  max-height: 350px;
}

.empty-notifications {
  padding: 40px 20px;
  text-align: center;
  color: #6c757d;
}

.empty-notifications i {
  font-size: 2rem;
  margin-bottom: 10px;
  opacity: 0.5;
}

.notification-item {
  display: flex;
  padding: 12px 15px;
  border-bottom: 1px solid #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item.unread {
  background-color: #f0f7ff;
  border-left: 3px solid var(--color-primary);
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

.notification-icon-type {
  margin-right: 12px;
  color: #6c757d;
}

.notification-item.critical .notification-icon-type {
  color: #e74c3c;
}

.notification-item.warning .notification-icon-type {
  color: #f39c12;
}

.notification-item.info .notification-icon-type {
  color: #3498db;
}

.notification-content {
  flex: 1;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 5px;
}

.notification-title {
  font-size: 0.9rem;
  margin: 0;
}

.notification-time {
  font-size: 0.7rem;
  color: #6c757d;
}

.notification-message {
  font-size: 0.8rem;
  margin: 0 0 8px 0;
  color: #495057;
  line-height: 1.3;
}

.notification-actions {
  margin-top: 8px;
}

.btn-action {
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

.btn-action:hover {
  background: #8b6b61;
}

.btn-eliminar {
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.notification-item:hover .btn-eliminar {
  opacity: 1;
}

.btn-eliminar:hover {
  color: #e74c3c;
}

.menu-footer {
  padding: 10px 15px;
  border-top: 1px solid #e9ecef;
}

.filter-tabs {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.filter-tab {
  background: none;
  border: 1px solid #e9ecef;
  padding: 4px 8px;
  border-radius: 15px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.filter-tab:hover:not(.active) {
  background: #f8f9fa;
}

/* Responsive */
@media (max-width: 768px) {
  .notification-menu {
    width: 320px;
    right: -50px;
  }
}

@media (max-width: 480px) {
  .notification-menu {
    width: 280px;
    right: -80px;
  }
}
</style>
