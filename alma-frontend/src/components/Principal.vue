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
          <i class="fas fa-user"></i>
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
            <label v-for="task in entregarHoy" :key="task.nombre">
              <input type="checkbox" v-model="task.completado" />
              <strong>{{ task.nombre }}</strong> - Estado: {{ task.estado }}
            </label>
          </div>

          <div class="card tasks">
            <h3 class="card-title">Hacer Hoy</h3>
            <label v-for="task in hacerHoy" :key="task.nombre">
              <input type="checkbox" v-model="task.completado" />
              <strong>{{ task.nombre }}</strong> - Estado: {{ task.estado }}
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
                <button @click="decrementarContador(receta)">-</button>
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
// En el script setup de Principal.vue
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();

// Inicializar vecesHecha para cada receta
onMounted(() => {
  recetas.value.forEach((r) => {
    if (r.vecesHecha === undefined) r.vecesHecha = 0;
  });
});

// Métodos para el contador
const incrementarContador = (receta) => {
  receta.vecesHecha++;
  actualizarStock(receta); // si querés actualizar stock al instante
};

const decrementarContador = (receta) => {
  if (receta.vecesHecha > 0) {
    receta.vecesHecha--;
    actualizarStock(receta);
  }
};

// Ejemplo de función para actualizar stock
const actualizarStock = (receta) => {
  // Aquí iría tu lógica para restar insumos según la receta
  console.log(
    `Actualizar stock de ${receta.nombre}, veces hechas: ${receta.vecesHecha}`
  );
};

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
    recetas.value = response.data.map((r) => ({
      ...r,
      vecesHecha: r.vecesHecha || 0, // inicializar contador
    }));
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
