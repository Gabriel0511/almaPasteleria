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
          <i class="fas fa-user"></i>
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
          <label v-for="task in entregarHoy" :key="task.nombre">
            <input type="checkbox" v-model="task.completado" />
            <strong>{{ task.nombre }}.</strong> Estado: {{ task.estado }}.
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
          <h3>Hacer Hoy (para 01/05)</h3>
          <label v-for="task in hacerHoy" :key="task.nombre">
            <input type="checkbox" v-model="task.completado" />
            <strong>{{ task.nombre }}.</strong> Estado: {{ task.estado }}.
          </label>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
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

// Datos de stock (ahora viene de la API)
const stock = ref([]);
const loading = ref(true);
const error = ref(null);
// Datos de recetas
const recetas = ref([]);
const loadingRecetas = ref(false);
const errorRecetas = ref(null);

// Datos estáticos (ejemplo)
const entregarHoy = ref([
  { nombre: "Sandra", estado: "Listo", completado: true },
  { nombre: "Nati", estado: "Listo", completado: true },
  { nombre: "José", estado: "Entregado", completado: true },
]);

const hacerHoy = ref([
  { nombre: "Sandra", estado: "Pendiente", completado: false },
  { nombre: "Nati", estado: "En Preparación", completado: false },
  { nombre: "José", estado: "Listo", completado: true },
]);

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

// Obtener datos de stock desde la API
const fetchStock = async () => {
  try {
    loading.value = true;
    error.value = null;

    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("No hay token de acceso");
    }

    const response = await axios.get("/api/insumos/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

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

    // Si es error 401, redirigir a login
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      router.push("/login");
    }
  } finally {
    loading.value = false;
  }
};

// Verificación de autenticación y carga inicial
onMounted(() => {
  const token = localStorage.getItem("access_token");
  console.log("Token en Principal.vue:", token); // Debug

  if (!token) {
    console.log("No hay token, redirigiendo a login");
    router.push("/login");
  } else {
    // Verificar si el token es válido
    axios
      .get("/api/auth/verify/") // Necesitarás implementar este endpoint
      .then(() => {
        fetchStock();
        fetchRecetas();
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        router.push("/login");
      });
  }
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
</style>
