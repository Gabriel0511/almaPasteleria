<template>
  <div class="notification-container">
    <div
      v-for="notification in notifications"
      :key="notification.id"
      :class="['notification', notification.type]"
      @click="removeNotification(notification.id)"
    >
      <i :class="notification.icon"></i>
      <div class="notification-content">
        <h4>{{ notification.title }}</h4>
        <p>{{ notification.message }}</p>

        <!-- Lista de insumos insuficientes -->
        <ul
          v-if="
            notification.insuficientes && notification.insuficientes.length > 0
          "
        >
          <li v-for="item in notification.insuficientes" :key="item.nombre">
            <span class="item-name">{{ item.nombre }}:</span>
            <span class="item-quantity"
              >{{ formatDecimal(item.disponible) }}
              {{ item.unidad }} disponible(s)</span
            >
            <span class="item-needed"
              >(se necesitan {{ formatDecimal(item.necesario) }})</span
            >
          </li>
        </ul>

        <!-- Lista de insumos devueltos -->
        <ul
          v-if="
            notification.insumos_devueltos &&
            notification.insumos_devueltos.length > 0
          "
          class="returned-items"
        >
          <li v-for="item in notification.insumos_devueltos" :key="item.nombre">
            <span class="item-name">{{ item.nombre }}:</span>
            <span class="item-quantity"
              >+{{ formatDecimal(item.cantidad) }}
              {{ item.unidad }} devuelto(s)</span
            >
          </li>
        </ul>
      </div>
      <button class="close-btn" @click="removeNotification(notification.id)">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { formatDecimal } from "../helpers/formatters";

const notifications = ref([]);
let nextId = 1;

const showNotification = (notificationData) => {
  const id = nextId++;
  const notification = {
    id,
    type: notificationData.type || "info",
    title: notificationData.title,
    message: notificationData.message,
    insuficientes: notificationData.insuficientes || [],
    icon: getIconForType(notificationData.type),
    timeout: notificationData.timeout || 5000,
  };

  notifications.value.push(notification);

  // Auto-remove after timeout
  if (notification.timeout > 0) {
    setTimeout(() => {
      removeNotification(id);
    }, notification.timeout);
  }
};

const getIconForType = (type) => {
  const icons = {
    error: "fas fa-exclamation-circle",
    warning: "fas fa-exclamation-triangle",
    success: "fas fa-check-circle",
    info: "fas fa-info-circle",
  };
  return icons[type] || icons.info;
};

const removeNotification = (id) => {
  notifications.value = notifications.value.filter((n) => n.id !== id);
};

// Exponer funciones para usar en otros componentes
defineExpose({
  showNotification,
  removeNotification,
});
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 90px;
  right: 20px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
}

.notification {
  display: flex;
  align-items: flex-start;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  cursor: pointer;
  transition: transform 0.3s ease, opacity 0.3s ease;
  animation: slideIn 0.3s ease;
}

.notification-content ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
  font-size: 13px;
}

.notification-content li {
  margin-bottom: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.item-name {
  font-weight: 600;
  color: #333;
}

.item-quantity {
  color: #666;
}

.item-needed {
  color: #dc3545;
  font-style: italic;
}

.returned-items .item-quantity {
  color: #28a745;
  font-weight: 600;
}

/* Para notificaciones de error, hacer la lista más destacada */
.notification.error ul {
  border-left: 3px solid #dc3545;
  padding-left: 15px;
  margin-left: -5px;
}

/* Para notificaciones de info (devoluciones) */
.notification.info ul {
  border-left: 3px solid #17a2b8;
  padding-left: 15px;
  margin-left: -5px;
}

.notification:hover {
  transform: translateX(-5px);
}

.notification.error {
  border-left-color: #dc3545;
}

.notification.warning {
  border-left-color: #ffc107;
}

.notification.success {
  border-left-color: #28a745;
}

.notification.info {
  border-left-color: #17a2b8;
}

.notification i:first-child {
  font-size: 20px;
  margin-right: 12px;
  margin-top: 2px;
}

.notification.error i:first-child {
  color: #dc3545;
}

.notification.warning i:first-child {
  color: #ffc107;
}

.notification.success i:first-child {
  color: #28a745;
}

.notification.info i:first-child {
  color: #17a2b8;
}

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: bold;
}

.notification-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  line-height: 1.4;
}

.notification-content ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
  font-size: 13px;
}

.notification-content li {
  margin-bottom: 4px;
  color: #666;
}

.close-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
  font-size: 14px;
}

.close-btn:hover {
  color: #666;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .notification-container {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }

  .notification {
    padding: 12px;
  }
}
</style>
