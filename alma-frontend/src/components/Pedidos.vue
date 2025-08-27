<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <main class="main-content">
      <header class="header">
        <div></div>
        <div class="logo">
          <img src="/src/Logo2.png" alt="Logo Pastelería" />
        </div>
        <div class="icon-buttons">
          <NotificationMenu :notifications="notifications" />
          <UserMenu
            :user-email="userEmail"
            @change-password="openChangePassword"
            @logout="logout"
          />
        </div>
      </header>

      <section class="content pedidos-content">
        <!-- Filtros de pedidos -->
        <div class="filtros-pedidos">
          <div class="filtro-group">
            <label for="fecha-filtro">Filtrar por fecha:</label>
            <input
              type="date"
              id="fecha-filtro"
              v-model="fechaFiltro"
              @change="filtrarPorFecha"
            />
          </div>

          <div class="filtro-group">
            <label for="estado-filtro">Filtrar por estado:</label>
            <select
              id="estado-filtro"
              v-model="estadoFiltro"
              @change="filtrarPorEstado"
            >
              <option value="">Todos los estados</option>
              <option
                v-for="estado in estadosPedido"
                :key="estado"
                :value="estado"
              >
                {{ estado }}
              </option>
            </select>
          </div>

          <button class="btn-nuevo-pedido" @click="nuevoPedido">
            <i class="fas fa-plus"></i> Nuevo Pedido
          </button>
        </div>

        <!-- Card principal de pedidos -->
        <div class="card pedidos-card">
          <h3 class="card-title">Gestión de Pedidos</h3>

          <div v-if="loadingPedidos" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i> Cargando pedidos...
          </div>

          <div v-else-if="pedidosFiltrados.length === 0" class="empty-state">
            No hay pedidos que coincidan con los filtros seleccionados
          </div>

          <div v-else class="pedidos-list">
            <div
              v-for="pedido in pedidosFiltrados"
              :key="pedido.id"
              class="pedido-item"
            >
              <div class="pedido-header">
                <div class="pedido-info">
                  <span class="pedido-id">#{{ pedido.id }}</span>
                  <span class="cliente-nombre">{{
                    pedido.cliente.nombre
                  }}</span>
                  <span class="pedido-fecha"
                    >Entrega: {{ formatDate(pedido.fecha_entrega) }}</span
                  >
                  <span class="pedido-fecha"
                    >Fabricación:
                    {{ formatDate(pedido.fecha_fabricacion) }}</span
                  >
                </div>
                <div class="pedido-acciones">
                  <span class="estado-badge" :class="pedido.estado">{{
                    pedido.estado
                  }}</span>
                  <button
                    class="btn-accion"
                    @click="editarPedido(pedido.id)"
                    title="Editar pedido"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="btn-accion"
                    @click="eliminarPedido(pedido.id)"
                    title="Eliminar pedido"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <div class="pedido-detalles">
                <div
                  v-for="detalle in pedido.detalles"
                  :key="detalle.id"
                  class="detalle-item"
                >
                  <span
                    >{{ detalle.receta.nombre }} (x{{ detalle.cantidad }})</span
                  >
                  <span>{{
                    formatDecimal(detalle.precio * detalle.cantidad)
                  }}</span>
                </div>

                <div
                  v-if="
                    pedido.ingredientes_extra &&
                    pedido.ingredientes_extra.length > 0
                  "
                  class="ingredientes-extra"
                >
                  <p><strong>Ingredientes extra:</strong></p>
                  <ul>
                    <li
                      v-for="extra in pedido.ingredientes_extra"
                      :key="extra.id"
                    >
                      {{ extra.insumo.nombre }}:
                      {{ formatDecimal(extra.cantidad) }}
                      {{ extra.insumo.unidad_medida.abreviatura }}
                    </li>
                  </ul>
                </div>

                <div class="pedido-total">
                  <strong>Total: {{ formatDecimal(pedido.total) }}</strong>
                </div>
              </div>

              <div class="estado-actions">
                <button
                  v-if="pedido.estado === 'pendiente'"
                  @click="actualizarEstadoPedido(pedido.id, 'en preparación')"
                  class="btn-estado"
                >
                  Marcar como en preparación
                </button>
                <button
                  v-if="pedido.estado === 'en preparación'"
                  @click="actualizarEstadoPedido(pedido.id, 'entregado')"
                  class="btn-estado"
                >
                  Marcar como entregado
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

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
  </div>
</template>

<script setup>
import { formatDecimal } from "../helpers/formatters";
import { onMounted, ref, computed, inject } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import Sidebar from "./Sidebar.vue";
import NotificationMenu from "./NotificationMenu.vue";
import UserMenu from "./UserMenu.vue";

const router = useRouter();
const notificationSystem = inject("notifications");

// Notificaciones
const notifications = ref([]);

const handleNavigation = (route) => {
  router.push(route);
};

// ----------------------
// 🔹 Estado del Menú y Usuario
// ----------------------
const showPasswordModal = ref(false);
const userEmail = ref("Usuario");
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

// ----------------------
// 🔹 Gestión de Pedidos
// ----------------------
const pedidos = ref([]);
const loadingPedidos = ref(true);
const fechaFiltro = ref("");
const estadoFiltro = ref("");
const estadosPedido = ["pendiente", "en preparación", "entregado", "cancelado"];

// Computed para filtrar pedidos
const pedidosFiltrados = computed(() => {
  let filtered = [...pedidos.value];

  // Filtrar por fecha si hay selección
  if (fechaFiltro.value) {
    filtered = filtered.filter(
      (pedido) =>
        pedido.fecha_entrega === fechaFiltro.value ||
        pedido.fecha_fabricacion === fechaFiltro.value
    );
  }

  // Filtrar por estado si hay selección
  if (estadoFiltro.value) {
    filtered = filtered.filter(
      (pedido) => pedido.estado === estadoFiltro.value
    );
  }

  return filtered.sort(
    (a, b) => new Date(b.fecha_pedido) - new Date(a.fecha_pedido)
  );
});

// ----------------------
// 🔹 Funciones de Pedidos
// ----------------------
const fetchPedidos = async () => {
  try {
    loadingPedidos.value = true;
    const response = await axios.get("/api/pedidos/");
    pedidos.value = response.data;
  } catch (err) {
    console.error("Error fetching pedidos:", err);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "No se pudieron cargar los pedidos",
      timeout: 4000,
    });
  } finally {
    loadingPedidos.value = false;
  }
};

const filtrarPorFecha = () => {
  // El filtrado se realiza automáticamente a través del computed
};

const filtrarPorEstado = () => {
  // El filtrado se realiza automáticamente a través del computed
};

const actualizarEstadoPedido = async (pedidoId, nuevoEstado) => {
  try {
    await axios.patch(`/api/pedidos/${pedidoId}/actualizar-estado/`, {
      estado: nuevoEstado,
    });

    notificationSystem.show({
      type: "success",
      title: "Estado actualizado",
      message: "El estado del pedido se ha actualizado correctamente",
      timeout: 4000,
    });

    // Actualizar la lista de pedidos
    await fetchPedidos();
  } catch (err) {
    console.error("Error al actualizar estado:", err);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message:
        err.response?.data?.error || "Error al actualizar el estado del pedido",
      timeout: 4000,
    });
  }
};

const nuevoPedido = () => {
  router.push("/pedidos/nuevo");
};

const editarPedido = (id) => {
  router.push(`/pedidos/editar/${id}`);
};

const eliminarPedido = async (id) => {
  if (!confirm("¿Está seguro de que desea eliminar este pedido?")) {
    return;
  }

  try {
    await axios.delete(`/api/pedidos/${id}/`);

    notificationSystem.show({
      type: "success",
      title: "Pedido eliminado",
      message: "El pedido se ha eliminado correctamente",
      timeout: 4000,
    });

    // Actualizar la lista de pedidos
    await fetchPedidos();
  } catch (err) {
    console.error("Error al eliminar pedido:", err);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "No se pudo eliminar el pedido",
      timeout: 4000,
    });
  }
};

// ----------------------
// 🔹 Funciones de Usuario
// ----------------------
const openChangePassword = () => {
  showPasswordModal.value = true;
};

const changePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    notificationSystem.show({
      type: "warning",
      title: "Contraseñas no coinciden",
      message: "Las contraseñas ingresadas no son iguales",
      timeout: 4000,
    });
    return;
  }

  try {
    await axios.post("/api/auth/change-password/", {
      old_password: currentPassword.value,
      new_password1: newPassword.value,
      new_password2: confirmPassword.value,
    });

    notificationSystem.show({
      type: "success",
      title: "¡Contraseña cambiada!",
      message: "Tu contraseña ha sido actualizada exitosamente",
      timeout: 4000,
    });
    showPasswordModal.value = false;
    currentPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  } catch (error) {
    console.error("Error al cambiar contraseña:", error);

    let errorMessage = "Error al cambiar la contraseña";
    if (error.response?.data?.errors) {
      errorMessage = Object.values(error.response.data.errors)
        .flat()
        .join("\n");
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }

    alert(errorMessage);
  }
};

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

// ----------------------
// 🔹 Utilidades
// ----------------------
const formatDate = (dateString) => {
  if (!dateString) return "";
  const options = { day: "2-digit", month: "2-digit", year: "numeric" };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

// ----------------------
// 🔹 Montaje Inicial
// ----------------------
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  Promise.all([
    axios.get("/api/auth/perfil/").then((res) => {
      userEmail.value = res.data.email || "Usuario";
    }),
    fetchPedidos(),
  ]).catch((error) => {
    console.error("Error cargando datos:", error);
    if (error.response?.status === 401) {
      logout();
    }
  });
});
</script>

<style scoped>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css");

/* ----------------------------- CONTENIDO Y CARDS ESPECÍFICOS ----------------------------- */
.pedidos-content {
  padding: 0 20px;
}

.filtros-pedidos {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filtro-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filtro-group label {
  font-weight: bold;
  font-size: 14px;
}

.filtro-group input,
.filtro-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.btn-nuevo-pedido {
  background-color: #7b5a50;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-nuevo-pedido:hover {
  background-color: #5a3f36;
}

/* ----------------------------- CARD DE PEDIDOS ----------------------------- */
.pedidos-card {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.pedidos-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.pedido-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.pedido-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.pedido-id {
  font-weight: bold;
  color: #7b5a50;
}

.cliente-nombre {
  font-weight: bold;
  font-size: 16px;
}

.pedido-fecha {
  font-size: 14px;
  color: #666;
}

.pedido-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
}

.estado-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.estado-badge.pendiente {
  background-color: #fff3cd;
  color: #856404;
}

.estado-badge.en.preparación {
  background-color: #d1ecf1;
  color: #0c5460;
}

.estado-badge.entregado {
  background-color: #d4edda;
  color: #155724;
}

.estado-badge.cancelado {
  background-color: #f8d7da;
  color: #721c24;
}

.btn-accion {
  background: none;
  border: none;
  cursor: pointer;
  color: #7b5a50;
  font-size: 16px;
}

.btn-accion:hover {
  color: #5a3f36;
}

.pedido-detalles {
  margin-bottom: 15px;
}

.detalle-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px dashed #e0e0e0;
}

.ingredientes-extra {
  margin-top: 10px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.ingredientes-extra ul {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.ingredientes-extra li {
  margin-bottom: 3px;
}

.pedido-total {
  text-align: right;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 2px solid #ccc;
  font-size: 16px;
}

.estado-actions {
  display: flex;
  gap: 10px;
}

.btn-estado {
  background-color: #7b5a50;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-estado:hover {
  background-color: #5a3f36;
}

.loading-state {
  text-align: center;
  padding: 20px;
  color: #7b5a50;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
  font-style: italic;
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .filtros-pedidos {
    flex-direction: column;
    align-items: stretch;
  }

  .pedido-header {
    flex-direction: column;
  }

  .pedido-acciones {
    align-self: flex-end;
  }

  .estado-actions {
    flex-direction: column;
  }

  .btn-estado {
    width: 100%;
  }
}
</style>
