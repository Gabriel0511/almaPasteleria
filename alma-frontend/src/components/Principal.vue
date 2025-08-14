<template>
  <div id="app">
    <aside class="sidebar">
      <button
        v-for="item in menuItems"
        :key="item.text"
        @click="selectMenu(item.text)"
      >
        <i :class="item.icon"></i>
        <span>{{ item.text }}</span>
      </button>
      <div class="footer-icon">
        <i class="fas fa-clipboard-check"></i>
      </div>
    </aside>

    <main class="main">
      <header class="header">
        <div></div>
        <div class="logo">
          <img src="/src/Logo2.png" alt="Logo Pastelería" />
        </div>
        <div class="icon-buttons">
          <div class="notification-icon">
            <i class="fas fa-bell"></i>
            <span class="notification">99</span>
          </div>
          <div class="user-menu-container">
            <i class="fas fa-user user-icon" @click="toggleUserMenu"></i>
            <div v-if="showUserMenu" class="user-menu">
              <div class="menu-header">{{ userEmail }}</div>
              <div class="menu-item" @click="openChangePassword">
                Cambiar contraseña
              </div>
              <div class="menu-item" @click="logout">Cerrar sesión</div>
            </div>
          </div>
        </div>
      </header>

      <section class="content">
        <!-- Stock -->
        <div class="card stock">
          <div class="stock-header-container">
            <h3 class="card-title">
              Stock
              <span v-if="insumosBajoStock > 0" class="badge">
                {{ insumosBajoStock }} bajo stock
              </span>
            </h3>

            <div class="stock-header">
              <span>Nombre</span>
              <span>Cantidad</span>
            </div>
          </div>

          <ul class="stock-list">
            <li
              v-for="item in stock"
              :key="item.nombre"
              :class="{ 'low-stock': item.bajoStock }"
            >
              <span>{{ item.nombre }} ({{ item.categoria }})</span>
              <span>{{ item.cantidad }}</span>
            </li>
          </ul>
        </div>

        <!-- Cards del medio -->
        <div class="middle-cards">
          <div class="card tasks">
            <h3 class="card-title">Entregar Hoy</h3>
            <div v-if="entregarHoy.length === 0" class="empty-state">
              No hay pedidos para entregar hoy
            </div>
            <label v-for="task in entregarHoy" :key="task.id">
              <input
                type="checkbox"
                :checked="task.estado === 'entregado'"
                @change="
                  actualizarEstadoPedido(task.id, 'entregado', 'entregarHoy')
                "
              />
              <strong>{{ task.nombre }}</strong>
              <span class="pedido-info">
                - Estado: {{ task.estado }} -
                <span v-for="detalle in task.detalles" :key="detalle.id">
                  {{ detalle.receta.nombre }} (x{{ detalle.cantidad }})
                </span>
              </span>
            </label>
          </div>

          <div class="card tasks">
            <h3 class="card-title">Hacer Hoy</h3>
            <div v-if="hacerHoy.length === 0" class="empty-state">
              No hay pedidos para fabricar hoy
            </div>
            <label v-for="task in hacerHoy" :key="task.id">
              <input
                type="checkbox"
                :checked="task.estado === 'en preparación'"
                @change="
                  actualizarEstadoPedido(task.id, 'en preparación', 'hacerHoy')
                "
              />
              <strong>{{ task.nombre }}</strong>
              <span class="pedido-info">
                - Estado: {{ task.estado }} - Entrega:
                {{ formatDate(task.fecha_entrega) }} -
                <span v-for="detalle in task.detalles" :key="detalle.id">
                  {{ detalle.receta.nombre }} (x{{ detalle.cantidad }})
                </span>
              </span>
            </label>
          </div>
        </div>

        <!-- Recetas -->
        <div class="card recetas">
          <h3 class="card-title">Recetas</h3>
          <input
            v-model="searchTerm"
            type="text"
            placeholder="Buscar receta..."
          />

          <ul class="recetas-list">
            <li v-for="receta in filteredRecetas" :key="receta.id">
              <span>{{ receta.nombre }}</span>
              <div class="contador">
                <button
                  @click="decrementarContador(receta)"
                  :disabled="!receta.vecesHecha"
                >
                  -
                </button>
                <span>{{ receta.vecesHecha || 0 }}</span>
                <button @click="incrementarContador(receta)">+</button>
              </div>
            </li>
          </ul>
        </div>
      </section>
    </main>
  </div>

  <!-- modal para cambiar contraseña -->
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
        <button @click="changePassword" class="confirm-button">Aceptar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();

// ----------------------
// 🔹 Estado del Menú y Usuario
// ----------------------
const menuItems = ref([
  { text: "Inicio", icon: "fas fa-house" },
  { text: "Stock", icon: "fas fa-box" },
  { text: "Pedidos", icon: "fas fa-clipboard-list" },
  { text: "Recetas", icon: "fas fa-book" },
  { text: "Reportes", icon: "fas fa-chart-line" },
]);

const showUserMenu = ref(false);
const showPasswordModal = ref(false);
const userEmail = ref("Usuario");
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

// ----------------------
// 🔹 Stock
// ----------------------
const stock = ref([]);
const loading = ref(true);
const error = ref(null);
const insumosBajoStock = computed(() => {
  return stock.value.filter((item) => item.bajoStock).length;
});

// ----------------------
// 🔹 Recetas
// ----------------------
const recetas = ref([]);
const loadingRecetas = ref(false);
const errorRecetas = ref(null);
const contador = ref(0);

const incrementarContador = async (receta) => {
  try {
    const response = await axios.post(`/api/recetas/${receta.id}/incrementar/`);

    // Actualizar en tiempo real
    receta.vecesHecha = response.data.nuevo_contador;

    if (response.data.stock_actualizado) {
      await fetchStock(); // Actualizar lista de stock
    }
  } catch (err) {
    console.error("Error al incrementar:", err);
    alert(err.response?.data?.error || "Error al incrementar receta");
  }
};

const decrementarContador = async (receta) => {
  try {
    if (receta.vecesHecha <= 0) return;

    const response = await axios.post(`/api/recetas/${receta.id}/decrementar/`);

    // Actualizar en tiempo real
    receta.vecesHecha = response.data.nuevo_contador;

    if (response.data.stock_actualizado) {
      await fetchStock(); // Actualizar lista de stock
    }
  } catch (err) {
    console.error("Error al decrementar:", err);
    alert(err.response?.data?.error || "Error al decrementar receta");
  }
};

// ----------------------
// 🔹 Pedidos
// ----------------------
const entregarHoy = ref([]);
const hacerHoy = ref([]);
const fechaActual = ref(new Date().toLocaleDateString());

const actualizarEstadoPedido = async (pedidoId, nuevoEstado, lista) => {
  try {
    await axios.patch(`/api/pedidos/${pedidoId}/actualizar-estado/`, {
      estado: nuevoEstado,
    });

    // Actualizar el estado localmente
    if (lista === "entregarHoy") {
      const index = entregarHoy.value.findIndex((p) => p.id === pedidoId);
      if (index !== -1) {
        entregarHoy.value[index].estado = nuevoEstado;
      }
    } else if (lista === "hacerHoy") {
      const index = hacerHoy.value.findIndex((p) => p.id === pedidoId);
      if (index !== -1) {
        hacerHoy.value[index].estado = nuevoEstado;
      }
    }
  } catch (err) {
    console.error("Error al actualizar estado:", err);
    alert(err.response?.data?.error || "Error al actualizar el pedido");
  }
};

// ----------------------
// 🔹 Búsqueda
// ----------------------
const searchTerm = ref("");
const filteredRecetas = computed(() => {
  if (!searchTerm.value) return recetas.value;
  return recetas.value.filter((r) =>
    r.nombre.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

// ----------------------
// 🔹 Funciones de Usuario
// ----------------------
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

const openChangePassword = () => {
  showUserMenu.value = false;
  showPasswordModal.value = true;
};

const changePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    alert("Las contraseñas no coinciden");
    return;
  }

  try {
    await axios.post("/api/auth/change-password/", {
      old_password: currentPassword.value,
      new_password1: newPassword.value,
      new_password2: confirmPassword.value,
    });

    alert("Contraseña cambiada exitosamente");
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
// 🔹 Fetch Datos
// ----------------------
const fetchStock = async () => {
  try {
    loading.value = true;
    error.value = null;

    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("No hay token de acceso");

    const response = await axios.get("/api/insumos/");
    stock.value = response.data.insumos
      .map((insumo) => ({
        nombre: insumo.nombre,
        cantidad: `${insumo.stock_actual} ${insumo.unidad_medida.abreviatura}`,
        bajoStock: insumo.necesita_reposicion,
        categoria: insumo.categoria?.nombre || "Sin categoría",
      }))
      .sort((a, b) => {
        // Los que tienen bajoStock true van primero
        if (a.bajoStock && !b.bajoStock) return -1;
        if (!a.bajoStock && b.bajoStock) return 1;
        return 0; // Mantiene el orden entre los que tienen la misma condición
      });
  } catch (err) {
    error.value = err.response?.data?.detail || "Error al cargar los insumos";
    if (err.response?.status === 401) {
      alert("Tu sesión ha expirado, por favor inicia sesión nuevamente");
      logout();
    }
    console.error("Error en fetchStock:", err);
  } finally {
    loading.value = false;
  }
};

const fetchRecetas = async () => {
  try {
    loadingRecetas.value = true;
    const response = await axios.get("/api/recetas/");
    recetas.value = response.data.map((receta) => ({
      ...receta,
      vecesHecha: receta.veces_hecha, // Usar el valor persistente del backend
    }));
  } catch (err) {
    errorRecetas.value = "Error al cargar las recetas";
    console.error("Error fetching recipes:", err);
  } finally {
    loadingRecetas.value = false;
  }
};
const fetchPedidos = async () => {
  try {
    const response = await axios.get("/api/pedidos/hoy/");
    entregarHoy.value = response.data.entregar_hoy.map((pedido) => ({
      id: pedido.id,
      nombre: pedido.cliente.nombre,
      estado: pedido.estado,
      completado: pedido.estado === "entregado",
      detalles: pedido.detalles,
      fecha_entrega: pedido.fecha_entrega,
    }));

    hacerHoy.value = response.data.hacer_hoy.map((pedido) => ({
      id: pedido.id,
      nombre: pedido.cliente.nombre,
      estado: pedido.estado,
      completado: pedido.estado === "en preparación",
      detalles: pedido.detalles,
      fecha_entrega: pedido.fecha_entrega,
    }));
  } catch (err) {
    console.error("Error fetching pedidos:", err);
  }
};

// ----------------------
// 🔹 Utilidades
// ----------------------
const selectMenu = (item) => {
  alert(`Seleccionaste: ${item}`);
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const options = { day: "2-digit", month: "2-digit", year: "numeric" };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

const updatePedidoStatus = async (pedidoId, nuevoEstado) => {
  try {
    await axios.patch(`/api/pedidos/hoy/${pedidoId}/`, { estado: nuevoEstado });
    fetchPedidos();
  } catch (err) {
    console.error("Error updating pedido:", err);
  }
};

// ----------------------
// 🔹 Montaje Inicial
// ----------------------
onMounted(() => {
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".user-menu-container")) {
      showUserMenu.value = false;
    }
  });

  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  Promise.all([
    axios.get("/api/auth/perfil/").then((res) => {
      userEmail.value = res.data.email || "Usuario";
    }),
    fetchStock(),
    fetchRecetas(),
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

/* ----------------------------- ESTRUCTURA GENERAL ----------------------------- */
body,
html,
#app {
  font-family: sans-serif;
  background-color: #f1d0cb;
  color: #3c3c3c;
  height: 100vh;
  display: flex;
  margin: 0;
}

/* ----------------------------- SIDEBAR ----------------------------- */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 120px;
  background-color: #7b5a50;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 10px;
}

.sidebar button {
  background: none;
  border: none;
  color: #fff;
  margin: 15px 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 14px;
}

.sidebar button i {
  font-size: 20px;
  margin-bottom: 5px;
}

.footer-icon {
  margin-top: auto;
  margin-bottom: 10px;
  color: white;
  font-size: 22px;
}

/* ----------------------------- MAIN & HEADER ----------------------------- */
.main {
  margin-left: 120px;
  padding: 15px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.logo img {
  height: 80px;
  margin-bottom: 10px;
}

.icon-buttons {
  display: flex;
  align-items: center;
  gap: 15px;
}

.icon-buttons i {
  font-size: 20px;
  background-color: white;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
}

.notification-icon {
  position: relative;
}

.notification {
  background-color: red;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 50%;
  position: absolute;
  top: -10px;
  left: -15px;
}

/* ----------------------------- CONTENIDO Y CARDS ----------------------------- */
.content {
  display: grid;
  grid-template-columns: 1fr 0.8fr 1fr;
  /* izquierda, medio, derecha */
  grid-template-areas: "stock middle recetas";
  gap: 20px;
}

.card {
  background-color: #f5dfdd;
  border-radius: 10px;
  box-shadow: 10px 8px 10px #aaa;
  padding: 8px;
  padding-top: 2px;
  overflow-y: auto;
}

.card h3 {
  margin-top: 0;
  font-size: 18px;
}

.card-title {
  text-align: center;
  margin: 0;
  padding: 4px;
  border-bottom: 1px solid #ccc;
}

/* ----------------------------- STOCK ----------------------------- */
.card.stock {
  grid-area: stock;
  max-height: 480px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  /* que solo scrollee la lista */
}

.stock-list {
  overflow-y: auto;
  flex-grow: 1;
  list-style: none;
  padding-left: 10px;
  padding-right: 10px;
}

.stock-list li {
  display: flex;
  justify-content: space-between;
  padding: 4px;
}

.low-stock {
  color: red;
  font-weight: bold;
}

.stock-header-container {
  flex-shrink: 0;
  /* que no se encoja al scrollear */
  background-color: #f5dfdd;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  padding: 10px;
  border-bottom: 1px solid #ccc;
}

/* ----------------------------- MIDDLE CARDS ----------------------------- */
.middle-cards {
  grid-area: middle;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 480px;
  /* altura total disponible para los dos cards */
}

.middle-cards .card {
  flex: 1;
  /* cada card ocupa la mitad del contenedor */
  min-height: 200px;
  /* altura mínima para que no se achiquen demasiado */
  max-height: 400px;
  /* altura máxima para no crecer demasiado */
  overflow-y: auto;
  /* scroll si hay muchos items */
  padding: 8px;
  /* opcional: espacio interno */
  padding-top: 2px;
  border-radius: 10px;
  background-color: #f5dfdd;
  box-shadow: 10px 8px 10px #aaa;
}

.tasks label {
  display: block;
  margin-bottom: 5px;
}

/* ----------------------------- RECETAS ----------------------------- */
.card.recetas {
  grid-area: recetas;
  max-height: 480px;
  display: flex;
  flex-direction: column;
}

.recetas input {
  width: 96%;
  padding: 5px;
  font-size: 14px;
  margin-bottom: 10px;
}

.recetas-list {
  list-style: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
  flex-grow: 1;
}

.recetas-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  border-bottom: 1px solid #ccc;
}

.contador button {
  padding: 4px 8px;
  margin: 0 4px;
  cursor: pointer;
  border: none;
  background-color: #7b5a50;
  color: white;
  border-radius: 5px;
  font-weight: bold;
}

.contador button:hover {
  background-color: #5a3f36;
}

.contador span {
  min-width: 20px;
  text-align: center;
  display: inline-block;
}

.loading-spinner {
  margin-left: 5px;
  color: #7b5a50;
}

.contador button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ----------------------------- LOADING / ERROR ----------------------------- */
.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: red;
  padding: 10px;
  text-align: center;
}

/* ----------------------------- SCROLL PERSONALIZADO ----------------------------- */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f0f0f0;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.user-menu-container {
  position: relative;
  display: inline-block;
}

.user-icon {
  font-size: 20px;
  background-color: white;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: background-color 0.3s;
}

.user-icon:hover {
  background-color: #f0f0f0;
}

.user-menu {
  position: absolute;
  right: 0;
  top: 100%;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 200px;
  z-index: 1000;
  margin-top: 5px;
}

.menu-header {
  padding: 10px 15px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.menu-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #f8f9fa;
}

.menu-item:last-child {
  border-radius: 0 0 8px 8px;
}

/* Estilos para el modal */
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
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
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
}

.confirm-button {
  padding: 8px 16px;
  background-color: #7b5a50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 15px;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 5px;
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .content {
    grid-template-columns: 1fr;
    grid-template-areas:
      "stock"
      "middle"
      "recetas";
  }

  .middle-cards {
    flex-direction: column;
  }

  .recetas input {
    width: 100%;
  }
}
</style>
