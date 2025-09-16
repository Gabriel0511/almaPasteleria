<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
       <Header/>
      <main class="main-content">
        <section class="content">
          <!-- Stock -->
          <div class="card stock">
            <div class="stock-header-container">
              <h3 class="card-title">
                Stock <br></br>
                <span v-if="insumosBajoStock > 0" class="badge">
                  (Hay {{ insumosBajoStock }} insumos con bajo stock)
                </span>
              </h3>

              <div class="stock-header">
                <span>
                  Nombre
                  <select v-model="categoriaSeleccionada">
                    <option value="">Todas</option>
                    <option v-for="cat in categoriasStock" :key="cat" :value="cat">
                      {{ cat }}
                    </option>
                  </select>
                </span>
                <span>Cantidad</span>
              </div>
            </div>

            <ul class="stock-list">
              <li v-for="item in stockFiltradoPorCategoria" :key="item.nombre" :class="{ 'low-stock': item.bajoStock }">
                <span>{{ item.nombre }} ({{ item.categoria }})</span>
                <span>{{ formatDecimal(item.cantidad) }} {{ item.unidad }}</span>
              </li>
            </ul>
          </div>

          <!-- Cards del medio -->
          <div class="middle-cards">
            <!-- Card de Entregar Hoy -->
            <div class="card tasks">
              <h3 class="card-title">Entregar Hoy</h3>
              <div v-if="entregarHoy.length === 0" class="empty-state">
                No hay pedidos para entregar hoy
              </div>
              <label v-for="task in entregarHoy" :key="task.id">
                <input type="checkbox" :checked="task.estado === 'entregado'" @change="
                  actualizarEstadoPedido(task.id, 'entregado', 'entregarHoy')
                  " />
                <strong>{{ task.nombre }}</strong>
                <span class="pedido-info">
                  - Estado: {{ task.estado }} - 
                  <span v-for="(detalle, index) in task.detalles" :key="detalle.id">
                    {{ index > 0 ? ', ' : '' }}{{ detalle.receta.nombre }} (x{{ detalle.cantidad }})
                  </span>
                </span>
              </label>
            </div>

            <!-- Card de Hacer Hoy -->
            <div class="card tasks">
              <h3 class="card-title">Hacer Hoy (Próximos 3 días)</h3>
              <div v-if="hacerHoy.length === 0" class="empty-state">
                No hay pedidos para los próximos 3 días
              </div>
              <label v-for="task in hacerHoy" :key="task.id">
                <input type="checkbox" :checked="task.estado === 'en preparación'" @change="
                  actualizarEstadoPedido(task.id, 'en preparación', 'hacerHoy')
                  " />
                <strong>{{ task.nombre }}</strong>
                <span class="pedido-info">
                  - Entrega: {{ formatDate(task.fecha_entrega) }} - Estado: {{ task.estado }} - 
                  <span v-for="(detalle, index) in task.detalles" :key="detalle.id">
                    {{ index > 0 ? ', ' : '' }}{{ detalle.receta.nombre }} (x{{ detalle.cantidad }})
                  </span>
                </span>
              </label>
            </div>
          </div>

          <!-- Recetas -->

          <div class="card recetas">
            <h3 class="card-title">Recetas</h3>
            <form autocomplete="off">
              <input autocomplete="off" v-model="searchTerm" type="text" placeholder="Buscar receta..." />
            </form>
            <ul class="recetas-list">
              <li v-for="receta in filteredRecetas" :key="receta.id">
                <span>
                  {{ receta.nombre }} (Rinde {{ receta.rinde }} {{ singularizeUnidad(receta.rinde, receta.unidad_rinde)
                  }})
                </span>
                <div class="contador">
                  <button @click="decrementarContador(receta)" :disabled="!receta.vecesHecha">
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
import { formatDecimal, parseDecimal } from "../helpers/formatters";
import { onMounted, ref, computed, inject } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";

const router = useRouter();
const notificationSystem = inject('notifications');

const handleNavigation = (route) => {
  router.push(route);
};

const categoriaSeleccionada = ref(""); // "" significa "Todas"
const categoriasStock = computed(() => {
  const categorias = stock.value.map(item => item.categoria);
  return [...new Set(categorias)];
});

// Computed para filtrar stock según categoría seleccionada
const stockFiltradoPorCategoria = computed(() => {
  if (!categoriaSeleccionada.value) return stock.value; // todas
  return stock.value.filter(item => item.categoria === categoriaSeleccionada.value);
});

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

    if (response.data.error) {
      notificationSystem.show({
        type: 'error',
        title: `Stock insuficiente para ${response.data.receta_nombre || receta.nombre}`,
        message: response.data.error,
        insuficientes: response.data.insuficientes || [],
        timeout: 10000
      });
      return;
    }

    receta.vecesHecha = response.data.nuevo_contador;

    if (response.data.stock_actualizado) {
      await fetchStock();
      notificationSystem.show({
        type: 'success',
        title: '¡Receta preparada!',
        message: response.data.mensaje || `Se ha incrementado el contador de ${receta.nombre}`,
        timeout: 4000
      });
    }
  } catch (err) {
    console.error("Error al incrementar:", err);
    notificationSystem.show({
      type: 'error',
      title: 'Error',
      message: err.response?.data?.error || "Error al incrementar receta",
      timeout: 6000
    });
  }
};

const decrementarContador = async (receta) => {
  try {
    if (receta.vecesHecha <= 0) return;

    const response = await axios.post(`/api/recetas/${receta.id}/decrementar/`);

    if (response.data.error) {
      notificationSystem.show({
        type: 'error',
        title: 'Error al decrementar',
        message: response.data.error,
        timeout: 6000
      });
      return;
    }

    receta.vecesHecha = response.data.nuevo_contador;

    if (response.data.stock_actualizado) {
      await fetchStock();
      notificationSystem.show({
        type: 'info',
        title: 'Preparación revertida',
        message: response.data.mensaje || `Se ha decrementado el contador de ${receta.nombre}`,
        insumos_devueltos: response.data.insumos_devueltos || [],
        timeout: 6000
      });
    }
  } catch (err) {
    console.error("Error al decrementar:", err);
    notificationSystem.show({
      type: 'error',
      title: 'Error',
      message: err.response?.data?.error || "Error al decrementar receta",
      timeout: 6000
    });
  }
};

const singularizeUnidad = (rinde, unidad) => {
  if (rinde === 1) {
    if (unidad === "unidades") return "unidad";
    if (unidad === "porciones") return "porción";
  }
  return unidad;
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

    if (lista === "entregarHoy") {
      const index = entregarHoy.value.findIndex((p) => p.id === pedidoId);
      if (index !== -1) {
        entregarHoy.value[index].estado = nuevoEstado;
        if (nuevoEstado === "entregado") {
          entregarHoy.value.splice(index, 1);
        }
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
    error.value = err.response?.data?.detail || "Error al cargar los insumos";
    if (err.response?.status === 401) {
      alert("Tu sesión ha expirado, por favor inicia sesión nuevamente");
      router.push("/login");
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
      vecesHecha: receta.veces_hecha,
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
    fetchStock(),
    fetchRecetas(),
    fetchPedidos(),
  ]).catch((error) => {
    console.error("Error cargando datos:", error);
    if (error.response?.status === 401) {
      router.push("/login");
    }
  });
});
</script>

<style scoped></style>