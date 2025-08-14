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
          <img src="/src/Logo Pasteleria.jpg" alt="Logo Pastelería" />
        </div>
        <div class="icon-buttons">
          <div class="notification-icon">
            <i class="fas fa-bell"></i>
            <span class="notification">3</span>
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
        <div class="card stock">
          <h3>
            Stock
            <span v-if="insumosBajoStock > 0" class="badge">
              {{ insumosBajoStock }} bajo stock
            </span>
          </h3>
          <div v-if="loading" class="loading">Cargando stock...</div>
          <div v-else-if="error" class="error">{{ error }}</div>
          <ul v-else class="stock-list">
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

        <div class="card tasks">
          <h3>Entregar Hoy</h3>
          <div v-if="entregarHoy.length === 0" class="empty-state">
            No hay pedidos para entregar hoy
          </div>
          <label v-for="task in entregarHoy" :key="task.id">
            <input
              type="checkbox"
              v-model="task.completado"
              @change="
                updatePedidoStatus(
                  task.id,
                  task.completado ? 'entregado' : 'en preparación'
                )
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

        <div class="card search-box">
          <input type="text" v-model="searchTerm" placeholder="Buscar..." />
          <ul>
            <li v-for="item in filteredRecetas" :key="item.nombre">
              <strong>{{ item.nombre }}</strong> – ({{ item.cantidad }})+
            </li>
          </ul>
        </div>

        <div class="card tasks">
          <h3>Hacer Hoy (para {{ fechaActual }})</h3>
          <div v-if="hacerHoy.length === 0" class="empty-state">
            No hay pedidos para fabricar hoy
          </div>
          <label v-for="task in hacerHoy" :key="task.id">
            <input
              type="checkbox"
              v-model="task.completado"
              @change="
                updatePedidoStatus(
                  task.id,
                  task.completado ? 'en preparación' : 'pendiente'
                )
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
// En el script setup de Principal.vue
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();

// Datos reactivos
const menuItems = ref([
  { text: "Inicio", icon: "fas fa-house" },
  { text: "Stock", icon: "fas fa-box" },
  { text: "Pedidos", icon: "fas fa-clipboard-list" },
  { text: "Recetas", icon: "fas fa-book" },
  { text: "Reportes", icon: "fas fa-chart-line" },
]);

// Datos de usuario
const showUserMenu = ref(false);
const showPasswordModal = ref(false);
const userEmail = ref("Usuario"); // Puedes obtenerlo del usuario autenticado
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

// Datos de stock
const stock = ref([]);
const loading = ref(true);
const error = ref(null);
const insumosBajoStock = computed(() => {
  return stock.value.filter((item) => item.bajoStock).length;
});

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
    const response = await axios.post("/api/auth/change-password/", {
      old_password: currentPassword.value, // Cambiado de current_password a old_password
      new_password1: newPassword.value, // Cambiado de new_password a new_password1
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

// Cierra el menú al hacer clic fuera de él
onMounted(() => {
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".user-menu-container")) {
      showUserMenu.value = false;
    }
  });
});

// Datos de recetas
const recetas = ref([]);
const loadingRecetas = ref(false);
const errorRecetas = ref(null);

// Datos de pedidos
const entregarHoy = ref([]);
const hacerHoy = ref([]);
const fechaActual = ref(new Date().toLocaleDateString());

const searchTerm = ref("");

// Computed properties
const filteredRecetas = computed(() => {
  if (!searchTerm.value) return recetas.value;
  return recetas.value.filter((r) =>
    r.nombre.toLowerCase().includes(searchTerm.value.toLowerCase())
  );
});

// Métodos
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
    await axios.patch(`/api/pedidos/${pedidoId}/`, {
      estado: nuevoEstado,
    });
    fetchPedidos();
  } catch (err) {
    console.error("Error updating pedido:", err);
  }
};

const fetchPedidos = async () => {
  try {
    const response = await axios.get(`/api/pedidos/hoy/`);

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

const fetchRecetas = async () => {
  try {
    loadingRecetas.value = true;
    const response = await axios.get("/api/recetas/");
    recetas.value = response.data;
  } catch (err) {
    errorRecetas.value = "Error al cargar las recetas";
    console.error("Error fetching recipes:", err);
  } finally {
    loadingRecetas.value = false;
  }
};

const fetchStock = async () => {
  try {
    loading.value = true;
    error.value = null;

    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("No hay token de acceso");
    }

    const response = await axios.get("/api/insumos/");

    stock.value = response.data.insumos.map((insumo) => ({
      nombre: insumo.nombre,
      cantidad: `${insumo.stock_actual} ${insumo.unidad_medida.abreviatura}`,
      bajoStock: insumo.necesita_reposicion,
      categoria: insumo.categoria?.nombre || "Sin categoría",
    }));
  } catch (err) {
    if (err.response?.status === 401) {
      showNotification(
        "Tu sesión ha expirado, por favor inicia sesión nuevamente",
        "error"
      );
    } else {
      showNotification("Error al cargar los insumos", "error");
    }
    console.error("Error en fetchStock:", err);
    error.value = err.response?.data?.detail || "Error al cargar los insumos";

    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      router.push("/login");
    }
  } finally {
    loading.value = false;
  }
};

const logout = async () => {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
      await axios.post("/api/auth/logout/", {
        refresh: refreshToken,
      });
    }
  } catch (err) {
    console.error("Error al cerrar sesión:", err.response?.data || err);
    // Aún así continuamos con la limpieza
  } finally {
    // Limpieza segura aunque falle la petición
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete axios.defaults.headers.common["Authorization"];
    router.push("/login");
  }
};

// Verificación de autenticación y carga inicial
onMounted(() => {
  // Verificación inicial
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  // Cargar datos
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

body,
html,
#app {
  margin: 0;
  font-family: sans-serif;
  background-color: #f1d0cb;
  color: #3c3c3c;
  height: 100vh;
  display: flex;
}

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

.main {
  margin-left: 120px;
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.logo img {
  height: 70px;
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

.content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto;
  gap: 20px;
  flex-grow: 1;
}

.card {
  background-color: #f5dfdd;
  border-radius: 15px;
  box-shadow: 2px 4px 6px #aaa;
  padding: 15px;
  overflow-y: auto;
}

.card h3 {
  margin-top: 0;
  font-size: 18px;
}

.stock-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

.stock-list li {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.low-stock {
  color: red;
  font-weight: bold;
}

.tasks label {
  display: block;
  margin-bottom: 5px;
}

.search-box input {
  width: 100%;
  padding: 5px;
  font-size: 14px;
  margin-bottom: 10px;
}

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

.badge {
  background-color: #ff6b6b;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.8em;
  margin-left: 10px;
}

.stock-list li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.stock-list li:last-child {
  border-bottom: none;
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
</style>
