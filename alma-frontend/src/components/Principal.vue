<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header />
      <main class="main-content">
        <section class="content">
          <!-- Stock -->
          <div class="card stock">
            <div class="stock-header-container">
              <h3 class="card-title">
                Stock <br />
                <span v-if="insumosBajoStock > 0" class="badge alert">
                  (Hay {{ insumosBajoStock }} insumos con bajo stock)
                </span>
                <span v-else class="badge success"> (Stock en orden) </span>
              </h3>

              <div class="stock-header">
                <span>
                  Nombre
                  <select v-model="categoriaSeleccionada" class="category-select">
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
              <li v-for="item in stockFiltradoPorCategoria" :key="item.nombre" :class="{ 'low-stock': item.bajoStock }"
                class="stock-item">
                <span class="item-name">{{ item.nombre }}
                  <span class="item-category">({{ item.categoria }})</span></span>
                <span class="item-quantity">{{ formatDecimal(item.cantidad) }} {{ item.unidad }}</span>
              </li>
            </ul>
          </div>

          <!-- Cards del medio -->
          <div class="middle-cards">
            <!-- Card de Entregar Hoy -->
            <div class="card tasks entregar-hoy">
              <div class="entregar-hoy-header-container">
                <div class="card-header sticky-header">
                  <h3 class="card-title">📦 Entregar Hoy</h3>
                  <span class="badge" :class="entregarHoyOrdenados.length > 0 ? 'alert' : 'success'">
                    {{ entregarHoyOrdenados.length }}
                  </span>
                </div>
              </div>

              <div class="entregar-hoy-list">
                <div v-if="entregarHoyOrdenados.length === 0" class="empty-state">
                  🎉 No hay pedidos para entregar hoy
                </div>

                <div v-for="task in entregarHoyOrdenados" :key="task.id" class="task-item" :class="task.estado">
                  <label class="task-checkbox">
                    <input type="checkbox" :checked="task.estado === 'entregado'"
                      :disabled="task.estado === 'entregado'" @change="confirmarEntrega(task)" />
                    <span class="checkmark"></span>
                  </label>
                  <div class="task-content">
                    <div class="task-header">
                      <strong class="cliente-nombre">{{ task.nombre }}</strong>
                      <span class="estado-badge" :class="task.estado">
                        {{ getEstadoText(task.estado) }}
                      </span>
                    </div>

                    <div class="task-details">
                      <span class="fecha">Entrega: {{ formatDate(task.fecha_entrega) }}</span>
                      <span class="recetas">
                        {{ getRecetasText(task.detalles) }}
                      </span>
                    </div>

                    <div v-if="task.estado === 'listo'" class="alert-preparacion">
                      ⚠️ Listo para entregar
                    </div>
                    <div v-if="task.estado === 'entregado'" class="entregado-info">
                      ✅ Entregado hoy
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Card de Hacer Hoy -->
            <div class="card tasks hacer-hoy">
              <div class="hacer-hoy-header-container">
                <div class="card-header sticky-header">
                  <h3 class="card-title">👨‍🍳 Hacer Hoy (Próximos 3 días)</h3>
                  <span class="badge" :class="hacerHoyOrdenados.length > 0 ? 'warning' : 'success'">
                    {{ hacerHoyOrdenados.length }}
                  </span>
                </div>
              </div>

              <div class="hacer-hoy-list">
                <div v-if="hacerHoyOrdenados.length === 0" class="empty-state">
                  ✅ No hay pedidos pendientes para los próximos 3 días
                </div>

                <div v-for="task in hacerHoyOrdenados" :key="task.id" class="task-item" :class="task.estado">
                  <label class="task-checkbox">
                    <input type="checkbox" :checked="task.estado === 'listo'" :disabled="task.estado === 'listo' ||
                      task.estado === 'entregado'
                      " @change="confirmarPreparacion(task)" />
                    <span class="checkmark"></span>
                  </label>

                  <div class="task-content">
                    <div class="task-header">
                      <strong class="cliente-nombre">{{ task.nombre }}</strong>
                      <span class="estado-badge" :class="task.estado">
                        {{ getEstadoText(task.estado) }}
                      </span>
                    </div>

                    <div class="task-details">
                      <span class="fecha" :class="{
                        'destacada': isHoy(task.fecha_entrega),
                        'atrasado': isAtrasado(task.fecha_entrega)
                      }">
                        📅 {{ formatDate(task.fecha_entrega) }}
                        <span v-if="isAtrasado(task.fecha_entrega)" class="atrasado-badge">
                          ⚠️ Atrasado
                        </span>
                      </span>
                      <span class="recetas">
                        {{ getRecetasText(task.detalles) }}
                      </span>
                    </div>

                    <div class="dias-restantes">
                      {{ getDiasRestantes(task.fecha_entrega) }}
                    </div>

                    <div v-if="task.estado === 'listo'" class="preparacion-info">
                      👨‍🍳 Listo
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recetas -->
          <div class="card recetas">
            <div class="recetas-header">
              <h3 class="card-title">📋 Recetas</h3>
              <form autocomplete="off" class="search-form">
                <input autocomplete="off" v-model="searchTerm" type="text" placeholder="🔍 Buscar receta..."
                  class="search-input" />
              </form>
            </div>

            <ul class="recetas-list">
              <li v-for="receta in filteredRecetas" :key="receta.id" class="receta-item">
                <span class="receta-info">
                  {{ receta.nombre }}
                  <span class="receta-rinde">
                    (Rinde {{ receta.rinde }}
                    {{ singularizeUnidad(receta.rinde, receta.unidad_rinde) }})
                  </span>
                </span>
                <div class="contador">
                  <button @click="decrementarContador(receta)" :disabled="!receta.veces_hecha" class="btn-contador">
                    -
                  </button>
                  <span class="contador-value">{{
                    receta.veces_hecha || 0
                  }}</span>
                  <button @click="incrementarContador(receta)" class="btn-contador">
                    +
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </section>
      </main>
    </div>

    <!-- Modal de Confirmación -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content confirm-modal">
        <div class="modal-header">
          <h3 class="modal-title">{{ modalTitle }}</h3>
        </div>

        <div class="modal-body">
          <div class="confirm-icon">
            <i class="fas" :class="modalIcon"></i>
          </div>
          <p class="confirm-message">{{ modalMessage }}</p>
          <div v-if="modalDetails" class="confirm-details">
            {{ modalDetails }}
          </div>
          <div class="confirm-warning">
            <i class="fas fa-exclamation-triangle"></i>
            ⚠️ Esta acción no se puede deshacer
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="cancelAction" class="cancel-button">
            <i class="fas fa-times"></i>
            Cancelar
          </button>
          <button @click="confirmAction" class="confirm-button"
            :class="{ 'danger': modalType === 'entrega', 'warning': modalType === 'preparacion' }">
            <i class="fas" :class="modalConfirmIcon"></i>
            {{ modalConfirmText }}
          </button>
        </div>
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
const notificationSystem = inject("notifications");

const handleNavigation = (route) => {
  router.push(route);
};

const categoriaSeleccionada = ref("");
const categoriasStock = computed(() => {
  const categorias = stock.value.map((item) => item.categoria);
  return [...new Set(categorias)];
});

const stockFiltradoPorCategoria = computed(() => {
  if (!categoriaSeleccionada.value) return stock.value;
  return stock.value.filter(
    (item) => item.categoria === categoriaSeleccionada.value
  );
});

// ----------------------
// 🔹 Modal de Confirmación
// ----------------------
const showConfirmModal = ref(false);
const modalTitle = ref("");
const modalMessage = ref("");
const modalDetails = ref("");
const modalType = ref(""); // 'entrega' o 'preparacion'
const modalAction = ref(null);
const currentTask = ref(null);

const modalIcon = computed(() => {
  return modalType.value === 'entrega'
    ? 'fa-truck'
    : 'fa-utensils';
});

const modalConfirmIcon = computed(() => {
  return modalType.value === 'entrega'
    ? 'fa-check-circle'
    : 'fa-play-circle';
});

const modalConfirmText = computed(() => {
  return modalType.value === 'entrega'
    ? 'Sí, Entregar'
    : 'Sí, Iniciar Preparación';
});

// Método para confirmar entrega
const confirmarEntrega = (task) => {
  if (task.estado === 'entregado') return;

  currentTask.value = task;
  modalType.value = 'entrega';
  modalTitle.value = 'Confirmar Entrega';
  modalMessage.value = `¿Estás seguro que quieres marcar como ENTREGADO el pedido?`;
  modalDetails.value = `Cliente: ${task.nombre}`;
  modalAction.value = () => marcarComoEntregado(task);

  showConfirmModal.value = true;
};

// Método para confirmar preparación
const confirmarPreparacion = (task) => {
  if (task.estado === 'listo' || task.estado === 'entregado') return;

  currentTask.value = task;
  modalType.value = 'preparacion';
  modalTitle.value = 'Iniciar Preparación';
  modalMessage.value = `¿Estás seguro que quieres INICIAR LA PREPARACIÓN del pedido?`;
  modalDetails.value = `Cliente: ${task.nombre}\nFecha de entrega: ${formatDate(task.fecha_entrega)}`;
  modalAction.value = () => empezarPreparacion(task);

  showConfirmModal.value = true;
};

const confirmAction = () => {
  if (modalAction.value && currentTask.value) {
    modalAction.value();
  }
  showConfirmModal.value = false;
  currentTask.value = null;
  modalAction.value = null;
};

const cancelAction = () => {
  showConfirmModal.value = false;
  currentTask.value = null;
  modalAction.value = null;
};

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

const incrementarContador = async (receta) => {
  try {
    const response = await axios.post(`/api/recetas/${receta.id}/incrementar/`);

    if (response.data.error) {
      let mensajeError = response.data.error;
      if (
        response.data.insuficientes &&
        response.data.insuficientes.length > 0
      ) {
        mensajeError += "\n\nInsumos insuficientes:";
        response.data.insuficientes.forEach((ins) => {
          mensajeError += `\n- ${ins.nombre}: Necesita ${ins.necesario} ${ins.unidad}, tiene ${ins.disponible} ${ins.unidad}`;
        });
      }

      notificationSystem.show({
        type: "error",
        title: `Stock insuficiente para ${response.data.receta_nombre || receta.nombre
          }`,
        message: mensajeError,
        timeout: 10000,
      });
      return;
    }

    const recetaIndex = recetas.value.findIndex((r) => r.id === receta.id);
    if (recetaIndex !== -1) {
      recetas.value[recetaIndex].veces_hecha = response.data.nuevo_contador;
    }

    if (response.data.stock_actualizado) {
      await fetchStock();
      notificationSystem.show({
        type: "success",
        title: "¡Receta preparada!",
        message:
          response.data.mensaje ||
          `Se ha incrementado el contador de ${receta.nombre}`,
        timeout: 4000,
      });
    }
  } catch (err) {
    let mensajeError = "Error al incrementar receta";
    if (err.response?.data) {
      if (err.response.data.insuficientes) {
        mensajeError = `Stock insuficiente para preparar "${receta.nombre}":\n`;
        err.response.data.insuficientes.forEach((ins) => {
          mensajeError += `\n- ${ins.nombre}: Necesita ${ins.necesario} ${ins.unidad}, tiene ${ins.disponible} ${ins.unidad}`;
        });
      } else if (err.response.data.error) {
        mensajeError = err.response.data.error;
      }
    }

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: mensajeError,
      timeout: 8000,
    });
  }
};

const decrementarContador = async (receta) => {
  try {
    if (receta.veces_hecha <= 0) {
      notificationSystem.show({
        type: "warning",
        title: "No se puede revertir",
        message: "Esta receta no ha sido preparada aún",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.post(`/api/recetas/${receta.id}/decrementar/`);

    if (response.data.error) {
      notificationSystem.show({
        type: "error",
        title: "Error al decrementar",
        message: response.data.error,
        timeout: 6000,
      });
      return;
    }

    const recetaIndex = recetas.value.findIndex((r) => r.id === receta.id);
    if (recetaIndex !== -1) {
      recetas.value[recetaIndex].veces_hecha = response.data.nuevo_contador;
    }

    if (response.data.stock_actualizado) {
      await fetchStock();

      let mensajeExito =
        response.data.mensaje ||
        `Se ha revertido la preparación de ${receta.nombre}`;
      if (
        response.data.insumos_devueltos &&
        response.data.insumos_devueltos.length > 0
      ) {
        mensajeExito += "\n\nInsumos devueltos al stock:";
        response.data.insumos_devueltos.forEach((ins) => {
          mensajeExito += `\n- ${ins.nombre}: ${ins.cantidad} ${ins.unidad}`;
        });
      }

      notificationSystem.show({
        type: "info",
        title: "Preparación revertida",
        message: mensajeExito,
        timeout: 8000,
      });
    }
  } catch (err) {
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: err.response?.data?.error || "Error al decrementar receta",
      timeout: 6000,
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
// 🔹 Pedidos - Métodos Mejorados
// ----------------------
const entregarHoy = ref([]);
const hacerHoy = ref([]);

// Computed properties para ordenar pedidos
const entregarHoyOrdenados = computed(() => {
  return [...entregarHoy.value].sort((a, b) => {
    // Primero los pendientes, luego los entregados
    if (a.estado !== 'entregado' && b.estado === 'entregado') return -1;
    if (a.estado === 'entregado' && b.estado !== 'entregado') return 1;
    // Luego por fecha
    return new Date(a.fecha_entrega) - new Date(b.fecha_entrega);
  });
});

const hacerHoyOrdenados = computed(() => {
  return [...hacerHoy.value].sort((a, b) => {
    // Primero los pendientes, luego los en preparación
    if (a.estado === 'pendiente' && b.estado !== 'pendiente') return -1;
    if (a.estado !== 'pendiente' && b.estado === 'pendiente') return 1;
    // Luego por fecha más próxima
    return new Date(a.fecha_entrega) - new Date(b.fecha_entrega);
  });
});

// Método para verificar si un pedido está atrasado
const isAtrasado = (fechaEntrega) => {
  const hoy = new Date();
  const entrega = new Date(fechaEntrega);
  return entrega < hoy && !isHoy(fechaEntrega);
};

// Método específico para entregar
const marcarComoEntregado = async (task) => {
  try {
    await actualizarEstadoPedido(task.id, "entregado", "entregarHoy");

    notificationSystem.show({
      type: "success",
      title: "¡Pedido entregado!",
      message: `El pedido de ${task.nombre} ha sido marcado como entregado`,
      timeout: 3000,
    });

    // Recargar datos después de un breve delay
    setTimeout(() => {
      fetchPedidos();
    }, 1000);
  } catch (error) {
    console.error("Error al marcar como entregado:", error);
  }
};

// Método específico para empezar preparación
const empezarPreparacion = async (task) => {
  try {
    await actualizarEstadoPedido(task.id, "listo", "hacerHoy");

    notificationSystem.show({
      type: "info",
      title: "Preparación iniciada",
      message: `El pedido de ${task.nombre} ahora está listo`,
      timeout: 3000,
    });

    // Recargar para que posiblemente se mueva a "Entregar Hoy"
    setTimeout(() => {
      fetchPedidos();
    }, 1000);
  } catch (error) {
    console.error("Error al iniciar preparación:", error);
  }
};

const actualizarEstadoPedido = async (pedidoId, nuevoEstado, lista) => {
  try {
    // Prevenir múltiples clics
    const pedido =
      lista === "entregarHoy"
        ? entregarHoy.value.find((p) => p.id === pedidoId)
        : hacerHoy.value.find((p) => p.id === pedidoId);

    if (pedido.actualizando) return; // Ya se está actualizando

    pedido.actualizando = true; // Marcar como actualizando

    await axios.patch(`/api/pedidos/${pedidoId}/actualizar-estado/`, {
      estado: nuevoEstado,
    });

    // Actualizar estado localmente
    if (lista === "entregarHoy") {
      const index = entregarHoy.value.findIndex((p) => p.id === pedidoId);
      if (index !== -1) {
        entregarHoy.value[index].estado = nuevoEstado;
        entregarHoy.value[index].actualizando = false;
      }
    } else if (lista === "hacerHoy") {
      const index = hacerHoy.value.findIndex((p) => p.id === pedidoId);
      if (index !== -1) {
        hacerHoy.value[index].estado = nuevoEstado;
        hacerHoy.value[index].actualizando = false;
      }
    }
  } catch (err) {
    console.error("Error al actualizar estado:", err);

    // Resetear el estado de actualización en caso de error
    if (lista === "entregarHoy") {
      const index = entregarHoy.value.findIndex((p) => p.id === pedidoId);
      if (index !== -1) entregarHoy.value[index].actualizando = false;
    } else if (lista === "hacerHoy") {
      const index = hacerHoy.value.findIndex((p) => p.id === pedidoId);
      if (index !== -1) hacerHoy.value[index].actualizando = false;
    }

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: err.response?.data?.error || "Error al actualizar el pedido",
      timeout: 6000,
    });
  }
};

// Helper methods para pedidos
const getEstadoText = (estado) => {
  const estados = {
    pendiente: "Pendiente",
    "listo": "Listo",
    entregado: "Entregado",
  };
  return estados[estado] || estado;
};

const getRecetasText = (detalles) => {
  return detalles
    .map((detalle) => `${detalle.receta.nombre} (x${detalle.cantidad})`)
    .join(", ");
};

const getDiasRestantes = (fechaEntrega) => {
  const hoy = new Date();
  const entrega = new Date(fechaEntrega);
  const diffTime = entrega - hoy;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "🎯 ¡Entrega hoy!";
  if (diffDays === 1) return "📌 Mañana";
  if (diffDays === 2) return "⏳ Pasado mañana";
  if (diffDays < 0) return `⚠️ ${Math.abs(diffDays)} día(s) de retraso`;
  return `⏳ En ${diffDays} días`;
};

const isHoy = (fechaEntrega) => {
  const hoy = new Date().toDateString();
  const entrega = new Date(fechaEntrega).toDateString();
  return hoy === entrega;
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
      router.push("/login");
    }
  } finally {
    loading.value = false;
  }
};

const fetchRecetas = async () => {
  try {
    loadingRecetas.value = true;
    const response = await axios.get("/api/recetas/");

    recetas.value = response.data.map((receta) => ({
      id: receta.id,
      nombre: receta.nombre,
      rinde: receta.rinde,
      unidad_rinde: receta.unidad_rinde,
      veces_hecha: receta.veces_hecha || 0,
    }));
  } catch (err) {
    errorRecetas.value = "Error al cargar las recetas";
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
      detalles: pedido.detalles,
      fecha_entrega: pedido.fecha_entrega,
    }));

    hacerHoy.value = response.data.hacer_hoy.map((pedido) => ({
      id: pedido.id,
      nombre: pedido.cliente.nombre,
      estado: pedido.estado,
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

  Promise.all([fetchStock(), fetchRecetas(), fetchPedidos()]).catch((error) => {
    console.error("Error cargando datos:", error);
    if (error.response?.status === 401) {
      router.push("/login");
    }
  });
});
</script>

<style>
/* ==================== ESTILOS ESPECÍFICOS PARA PRINCIPAL.VUE ==================== */

/* -------------------- HEADER DE CARDS MEJORADO -------------------- */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
}

/* Header fijo para scroll */
.sticky-header {
  position: sticky;
  top: 0;
  background: var(--color-background);
  z-index: 10;
  padding: 15px 8px;
  margin: -8px -8px 15px -8px;
  border-radius: 10px 10px 0 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* -------------------- BADGES MEJORADOS -------------------- */
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.badge.alert {
  background: #e74c3c;
  color: white;
}

.badge.warning {
  background: #f39c12;
  color: white;
}

.badge.success {
  background: #27ae60;
  color: white;
}

/* -------------------- TAREAS/ITEMS DE PEDIDOS -------------------- */
.task-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border-radius: 10px;
  background: #f8f9fa;
  border-left: 4px solid #ddd;
  transition: all 0.3s ease;
}

.task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.task-item.pendiente {
  border-left-color: #e74c3c;
  background: #fff5f5;
}

.task-item.en.preparación {
  border-left-color: #f39c12;
  background: #fffaf0;
}

.task-item.entregado {
  border-left-color: #27ae60;
  background: #f0fff4;
  opacity: 0.8;
}

.task-content {
  flex: 1;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.cliente-nombre {
  font-size: 1.1rem;
  color: #2c3e50;
}

.estado-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
}

.estado-badge.pendiente {
  background: #e74c3c;
  color: white;
}

.estado-badge.en.preparación {
  background: #f39c12;
  color: white;
}

.estado-badge.entregado {
  background: #27ae60;
  color: white;
}

.task-details {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

.fecha.destacada {
  color: #e74c3c;
  font-weight: bold;
}

.fecha.atrasado {
  color: #dc3545;
  font-weight: bold;
}

.atrasado-badge {
  background: #dc3545;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.7rem;
  margin-left: 5px;
}

.dias-restantes {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #7f8c8d;
  font-weight: bold;
}

.alert-preparacion {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #856404;
}

.entregado-info,
.preparacion-info {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #155724;
  font-weight: bold;
}

.preparacion-info {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 1rem 0;
}

/* -------------------- HEADER DE RECETAS MEJORADO -------------------- */
.recetas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.search-form {
  margin: 0;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 20px;
  width: 250px;
}

/* -------------------- ITEMS DE RECETAS MEJORADOS -------------------- */
.receta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.receta-item:hover {
  background: #f8f9fa;
}

.receta-info {
  flex: 1;
}

.receta-rinde {
  font-size: 0.9rem;
  color: #666;
}

/* -------------------- CONTADOR MEJORADO -------------------- */
.contador {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-contador {
  width: 30px;
  height: 30px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-contador:hover:not(:disabled) {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.btn-contador:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.contador-value {
  font-weight: bold;
  min-width: 30px;
  text-align: center;
}

/* -------------------- STOCK MEJORADO -------------------- */
.stock-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
}

.stock-item.low-stock {
  background: #ffeaa7;
  border-left: 3px solid #e74c3c;
}

.item-name {
  font-weight: 500;
}

.item-category {
  font-size: 0.8rem;
  color: #666;
}

.item-quantity {
  font-weight: bold;
}

.category-select {
  margin-left: 0.5rem;
  padding: 0.25rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* -------------------- CARDS ESPECÍFICAS PARA PEDIDOS -------------------- */
.card.entregar-hoy {
  border-top: 3px solid #27ae60;
}

.card.hacer-hoy {
  border-top: 3px solid #f39c12;
}

/* -------------------- RESPONSIVE ESPECÍFICO -------------------- */
@media (max-width: 768px) {
  .recetas-header {
    flex-direction: column;
    gap: 1rem;
  }

  .search-input {
    width: 100%;
  }

  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .task-item {
    padding: 0.75rem;
  }

  .cliente-nombre {
    font-size: 1rem;
  }

  .sticky-header {
    padding: 10px 8px;
  }
}

@media (max-width: 480px) {
  .estado-badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
  }

  .task-details {
    font-size: 0.8rem;
  }

  .dias-restantes {
    font-size: 0.7rem;
  }
}

/* -------------------- CHECKBOX PERSONALIZADO CORREGIDO -------------------- */
.task-checkbox input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.task-checkbox {
  display: block;
  position: relative;
  padding-left: 35px;
  cursor: pointer;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  margin-right: 1rem;
  margin-top: 0.25rem;
}

/* Checkmark personalizado */
.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: #fff;
  border: 2px solid #ccc;
  border-radius: 4px;
  transition: all 0.3s ease;
}

/* Al pasar el mouse sobre el checkmark */
.task-checkbox:hover input:not(:disabled)~.checkmark {
  border-color: #7b5a50;
}

/* Cuando el checkbox está checked */
.task-checkbox input:checked~.checkmark {
  background: #27ae60;
  border-color: #27ae60;
}

/* Crear el checkmark/indicador (oculto cuando no está checked) */
.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 6px;
  top: 2px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  -webkit-transform: rotate(45deg);
  -ms-transform: rotate(45deg);
  transform: rotate(45deg);
}

/* Mostrar el checkmark cuando está checked */
.task-checkbox input:checked~.checkmark:after {
  display: block;
}

/* Estilos para estado deshabilitado */
.task-checkbox input:disabled~.checkmark {
  background: #f0f0f0;
  border-color: #ddd;
  cursor: not-allowed;
}

.task-checkbox input:disabled:checked~.checkmark {
  background: #95a5a6;
  border-color: #95a5a6;
}

.task-checkbox input:disabled~.checkmark:after {
  border-color: #bdc3c7;
}

/* -------------------- ESTILOS PARA EL MODAL DE CONFIRMACIÓN -------------------- */
.confirm-modal {
  max-width: 450px;
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
  margin-bottom: 20px;
}

.modal-title {
  color: var(--color-primary);
  font-size: 1.4rem;
  margin: 0;
  font-weight: 600;
}

.modal-body {
  padding: 10px 0;
}

.confirm-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
  color: var(--color-primary);
}

.confirm-message {
  font-size: 1.1rem;
  margin-bottom: 15px;
  line-height: 1.5;
  color: #333;
}

.confirm-details {
  background-color: rgba(123, 90, 80, 0.1);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  font-size: 0.95rem;
  white-space: pre-line;
  border-left: 4px solid var(--color-primary);
  text-align: left;
  line-height: 1.4;
}

.confirm-warning {
  background-color: rgba(255, 193, 7, 0.2);
  color: #856404;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  border: 1px solid rgba(255, 193, 7, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.modal-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 25px;
}

.modal-buttons button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s ease;
  min-width: 150px;
  justify-content: center;
  font-size: 0.95rem;
}

.cancel-button {
  background-color: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.cancel-button:hover {
  background-color: #e2e6ea;
  transform: translateY(-2px);
}

.confirm-button.danger {
  background-color: var(--color-danger);
  color: white;
}

.confirm-button.danger:hover {
  background-color: #c82333;
  transform: translateY(-2px);
}

.confirm-button.warning {
  background-color: var(--color-warning);
  color: #000;
}

.confirm-button.warning:hover {
  background-color: #e0a800;
  transform: translateY(-2px);
}

/* Animación de entrada del modal */
.modal-overlay {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.confirm-modal {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.9);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

</style>