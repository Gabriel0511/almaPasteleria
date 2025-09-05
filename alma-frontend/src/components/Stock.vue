<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header
        :userEmail="userEmail"
        title="Panel Principal"
        @openPasswordModal="showPasswordModal = true"
        @logout="logout"
      />

      <main class="main-content">
        <h3 class="card-title">
          Stock
          <span v-if="insumosBajoStock > 0" class="badge">
            (Hay {{ insumosBajoStock }} insumos con bajo stock)
          </span>
        </h3>
        <!-- Buscador + Filtro -->
        <div class="stock-header">
          <span>
            Buscar:
            <input
              v-model="searchTerm"
              type="text"
              placeholder="Buscar insumo..."
              class="form-input"
            />
          </span>
          <span>
            Categoría:
            <select v-model="categoriaSeleccionada">
              <option value="">Todas</option>
              <option v-for="cat in categoriasStock" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </span>
        </div>

        <section class="content">
          <div class="card stock">
            <div class="stock-header-container">
              <div class="stock-header">
                <span>Nombre</span>
                <span>Cantidad</span>
              </div>
            </div>

            <ul class="stock-list">
              <li
                v-for="item in stockFiltradoPorCategoria"
                :key="item.nombre"
                :class="{ 'low-stock': item.bajoStock }"
              >
                <span>{{ item.nombre }} ({{ item.categoria }})</span>
                <span
                  >{{ formatDecimal(item.cantidad) }} {{ item.unidad }}</span
                >
              </li>
            </ul>
          </div>
        </section>

        <!-- Acciones -->
        <div class="stock-actions">
          <button class="btn-success">Nueva Compra</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted } from "vue"; // Añadir imports necesarios
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import axios from "axios";

const router = useRouter();

// 🔹 Añadir estas variables que faltan
const userEmail = ref("Usuario");
const showPasswordModal = ref(false);
const stock = ref([]);
const insumosBajoStock = computed(() => {
  return stock.value.filter((item) => item.bajoStock).length;
});
const categoriaSeleccionada = ref("");
const categoriasStock = computed(() => {
  const categorias = stock.value.map((item) => item.categoria);
  return [...new Set(categorias)];
});
const searchTerm = ref("");

const handleNavigation = (route) => {
  router.push(route);
};

// 🔹 Añadir función de logout
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

// 🔹 Añadir función para formatear decimales (si no la tienes)
const formatDecimal = (value) => {
  return Number(value).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

// 🔹 Añadir computed para filtrar stock
const stockFiltradoPorCategoria = computed(() => {
  if (!categoriaSeleccionada.value) return stock.value;
  return stock.value.filter(
    (item) => item.categoria === categoriaSeleccionada.value
  );
});

// 🔹 Añadir mounted hook para cargar datos
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  // Cargar datos del usuario y stock
  Promise.all([
    axios.get("/api/auth/perfil/").then((res) => {
      userEmail.value = res.data.email || "Usuario";
    }),
    fetchStock(),
  ]).catch((error) => {
    console.error("Error cargando datos:", error);
    if (error.response?.status === 401) {
      logout();
    }
  });
});

// 🔹 Añadir función para fetch stock
const fetchStock = async () => {
  try {
    const response = await axios.get("/api/insumos/");
    stock.value = response.data.insumos
      .map((insumo) => ({
        nombre: insumo.nombre,
        cantidad: insumo.stock_actual,
        unidad: insumo.unidad_medida.abreviatura,
        bajoStock: insumo.necesita_reposicion,
        categoria: insumo.categoria?.nombre || "Sin categoría",
      }))
      .sort((a, b) => {
        if (a.bajoStock && !b.bajoStock) return -1;
        if (!a.bajoStock && b.bajoStock) return 1;
        return 0;
      });
  } catch (err) {
    console.error("Error en fetchStock:", err);
    if (err.response?.status === 401) {
      logout();
    }
  }
};
</script>
