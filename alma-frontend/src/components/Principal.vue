<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content principal-content">
        <section class="content">
          <!-- Stock -->
          <div class="card stock">
            <div class="stock-header-container">
              <div class="card-header sticky-header">
                <h3 class="card-title">📦 Stock</h3>

                <div class="stock-controls">
                  <div class="filtro-container">
                    <select
                      v-model="categoriaSeleccionada"
                      class="category-select"
                    >
                      <option value="">Todas las categorías</option>
                      <option
                        v-for="cat in categoriasStock"
                        :key="cat"
                        :value="cat"
                      >
                        {{ cat }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Resumen rápido -->
            <div class="recetas-total">
              <span class="total-text">Total insumos:</span>
              <span class="total-count">{{
                stockFiltradoPorCategoria.length
              }}</span>
              <span class="total-text">Bajo stock:</span>
              <span class="total-count alert">{{
                insumosBajoStockFiltrados
              }}</span>
            </div>

            <div class="stock-list-container">
              <ul class="stock-list">
                <li
                  v-for="item in stockPaginado"
                  :key="item.id"
                  :class="{
                    'low-stock': item.bajoStock,
                    'stock-item-activo': item.bajoStock,
                  }"
                  class="stock-item"
                  @click="irAStockConBusqueda(item.nombre)"
                >
                  <div class="stock-info-container">
                    <div class="stock-icon">
                      {{ getStockIcon(item.categoria) }}
                    </div>
                    <div class="stock-info">
                      <span class="item-name">{{ item.nombre }}</span>
                      <span class="item-category">{{ item.categoria }}</span>
                    </div>
                  </div>

                  <div class="stock-data">
                    <div class="stock-cantidad">
                      <span class="data-label">Stock Actual</span>
                      <span
                        class="item-quantity"
                        :class="{ 'low-stock-text': item.bajoStock }"
                      >
                        {{ formatDecimal(item.cantidad) }} {{ item.unidad }}
                      </span>
                    </div>
                    <div class="stock-minimo">
                      <span class="data-label">Stock Mínimo</span>
                      <span class="item-minimum">
                        {{ formatDecimal(item.stock_minimo) }} {{ item.unidad }}
                      </span>
                    </div>
                  </div>
                </li>
              </ul>

              <!-- Estado vacío -->
              <div
                v-if="stockFiltradoPorCategoria.length === 0"
                class="stock-empty"
              >
                <div class="empty-icon">📦</div>
                <p class="empty-text">No hay insumos en esta categoría</p>
              </div>
            </div>

            <!-- Paginación -->
            <div v-if="totalPaginas > 1" class="paginacion">
              <button
                @click="paginaAnterior"
                :disabled="paginaActual === 1"
                class="btn-paginacion"
                :class="{ 'btn-disabled': paginaActual === 1 }"
              >
                ‹ Anterior
              </button>

              <div class="paginacion-info">
                Página {{ paginaActual }} de {{ totalPaginas }}
              </div>

              <button
                @click="paginaSiguiente"
                :disabled="paginaActual === totalPaginas"
                class="btn-paginacion"
                :class="{ 'btn-disabled': paginaActual === totalPaginas }"
              >
                Siguiente ›
              </button>
            </div>
          </div>

          <!-- Cards del medio -->
          <div class="middle-cards">
            <!-- Card de Entregar Hoy -->
            <div class="card tasks entregar-hoy">
              <div class="entregar-hoy-header-container">
                <div class="card-header sticky-header">
                  <h3 class="card-title">📦 Entregar Hoy</h3>
                  <span
                    class="badge"
                    :class="
                      entregarHoyOrdenados.length > 0 ? 'alert' : 'success'
                    "
                  >
                    {{ entregarHoyOrdenados.length }}
                  </span>
                </div>
              </div>

              <div class="entregar-hoy-list">
                <div
                  v-if="entregarHoyOrdenados.length === 0"
                  class="empty-state"
                >
                  🎉 No hay pedidos para entregar hoy
                </div>

                <div
                  v-for="task in entregarHoyOrdenados"
                  :key="task.id"
                  class="task-item"
                  :class="task.estado"
                >
                  <label class="task-checkbox">
                    <input
                      type="checkbox"
                      :checked="task.estado === 'entregado'"
                      :disabled="task.estado === 'entregado'"
                      @click.prevent="confirmarEntrega(task)"
                    />
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
                      <span class="fecha"
                        >Entrega: {{ formatFecha(task.fecha_entrega) }}</span
                      >
                      <span class="recetas">
                        {{ getRecetasText(task.detalles) }}
                      </span>
                    </div>

                    <div
                      v-if="task.estado === 'listo'"
                      class="alert-preparacion"
                    >
                      ⚠️ Listo para entregar
                    </div>
                    <div
                      v-if="task.estado === 'entregado'"
                      class="entregado-info"
                    >
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
                  <span
                    class="badge"
                    :class="hacerHoyOrdenados.length > 0 ? 'alert' : 'success'"
                  >
                    {{ hacerHoyOrdenados.length }}
                  </span>
                </div>
              </div>

              <div class="hacer-hoy-list">
                <div v-if="hacerHoyOrdenados.length === 0" class="empty-state">
                  ✅ No hay pedidos pendientes para los próximos 3 días
                </div>

                <div
                  v-for="task in hacerHoyOrdenados"
                  :key="task.id"
                  class="task-item"
                  :class="task.estado"
                >
                  <label class="task-checkbox">
                    <input
                      type="checkbox"
                      :checked="task.estado === 'listo'"
                      :disabled="
                        task.estado === 'listo' || task.estado === 'entregado'
                      "
                      @click.prevent="confirmarPreparacion(task)"
                    />
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
                      <span
                        class="fecha"
                        :class="{
                          destacada: isHoy(task.fecha_entrega),
                          atrasado: isAtrasado(task.fecha_entrega),
                        }"
                      >
                        📅 {{ formatFecha(task.fecha_entrega) }}
                        <span
                          v-if="isAtrasado(task.fecha_entrega)"
                          class="atrasado-badge"
                        >
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

                    <div
                      v-if="task.estado === 'listo'"
                      class="preparacion-info"
                    >
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
              <h3 class="card-title">📋 Recetas del Día</h3>
              <form autocomplete="off" class="search-form">
                <input
                  autocomplete="off"
                  v-model="searchTerm"
                  type="text"
                  placeholder="🔍 Buscar receta..."
                  class="search-input"
                />
              </form>
            </div>

            <!-- Total del día -->
            <div class="recetas-total">
              <span class="total-text">Total Recetas:</span>
              <span class="total-count">{{ totalRecetas }}</span>
              <span class="total-text">Total preparado hoy:</span>
              <span class="total-count">{{ totalRecetasHoy }}</span>
            </div>

            <div class="recetas-list-container">
              <ul class="recetas-list">
                <li
                  v-for="receta in recetasPaginadas"
                  :key="receta.id"
                  class="receta-item"
                  :class="{ 'receta-activa': receta.veces_hecha > 0 }"
                >
                  <div class="receta-info-container">
                    <div class="receta-icon">
                      {{ getRecetaIcon(receta.nombre) }}
                    </div>
                    <div class="receta-info">
                      <span class="receta-nombre">{{ receta.nombre }}</span>
                      <span class="receta-rinde">
                        (Rinde {{ receta.rinde }}
                        {{
                          singularizeUnidad(receta.rinde, receta.unidad_rinde)
                        }})
                      </span>
                    </div>
                  </div>

                  <div class="contador-container">
                    <span class="contador-label">Hechas hoy:</span>
                    <div class="contador">
                      <button
                        @click="decrementarContador(receta)"
                        :disabled="!receta.veces_hecha"
                        class="btn-contador btn-menos"
                        :class="{ 'btn-disabled': !receta.veces_hecha }"
                      >
                        −
                      </button>
                      <span
                        class="contador-value"
                        :class="{
                          'contador-cero': receta.veces_hecha === 0,
                          'contador-activo': receta.veces_hecha > 0,
                        }"
                      >
                        {{ receta.veces_hecha || 0 }}
                      </span>
                      <button
                        @click="incrementarContador(receta)"
                        class="btn-contador btn-mas"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </li>
              </ul>

              <!-- Estado vacío -->
              <div v-if="filteredRecetas.length === 0" class="recetas-empty">
                <div class="empty-icon">🔍</div>
                <p class="empty-text">No se encontraron recetas</p>
                <p class="empty-subtext">
                  Intenta con otros términos de búsqueda
                </p>
              </div>
            </div>

            <!-- Paginación -->
            <div v-if="totalPaginasRecetas > 1" class="paginacion">
              <button
                @click="paginaAnteriorRecetas"
                :disabled="paginaActualRecetas === 1"
                class="btn-paginacion"
                :class="{ 'btn-disabled': paginaActualRecetas === 1 }"
              >
                ‹ Anterior
              </button>

              <div class="paginacion-info">
                Página {{ paginaActualRecetas }} de {{ totalPaginasRecetas }}
              </div>

              <button
                @click="paginaSiguienteRecetas"
                :disabled="paginaActualRecetas === totalPaginasRecetas"
                class="btn-paginacion"
                :class="{
                  'btn-disabled': paginaActualRecetas === totalPaginasRecetas,
                }"
              >
                Siguiente ›
              </button>
            </div>
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
          <button
            @click="confirmAction"
            class="confirm-button"
            :class="{
              danger: modalType === 'entrega',
              warning: modalType === 'preparacion',
            }"
          >
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

// Referencia al sidebar para controlarlo desde el header
const sidebarRef = ref(null);

// Método para alternar el sidebar desde el header
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
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

// Total de recetas preparadas hoy
const totalRecetasHoy = computed(() => {
  return recetas.value.reduce(
    (total, receta) => total + (receta.veces_hecha || 0),
    0
  );
});

const totalRecetas = computed(() => {
  return recetas.value.length;
});

const getRecetaIcon = (nombreReceta) => {
  const nombre = nombreReceta.toLowerCase();

  if (nombre.includes("gelatina")) return "🍮";
  if (nombre.includes("rogel") || nombre.includes("dulce de leche"))
    return "🥧";
  if (nombre.includes("lemon") || nombre.includes("pie")) return "🍋";
  if (nombre.includes("limonada")) return "🍹";
  if (nombre.includes("pomelada")) return "🍈";
  if (nombre.includes("huevo") || nombre.includes("tostada")) return "🍳";
  if (nombre.includes("panqueque")) return "🥞";
  if (nombre.includes("alfajor")) return "🍪";
  if (nombre.includes("cafe")) return "☕";
  if (nombre.includes("torta") || nombre.includes("cake")) return "🎂";

  return "👨‍🍳";
};

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
  return modalType.value === "entrega" ? "fa-truck" : "fa-utensils";
});

const modalConfirmIcon = computed(() => {
  return modalType.value === "entrega" ? "fa-check-circle" : "fa-play-circle";
});

const modalConfirmText = computed(() => {
  return modalType.value === "entrega" ? "Sí, Entregar" : "Sí, terminar pedido";
});

const confirmAction = () => {
  if (modalAction.value && currentTask.value) {
    modalAction.value();
  }
  showConfirmModal.value = false;
  if (currentTask.value) {
    currentTask.value.confirmando = false; // Resetear estado de confirmación
  }
  currentTask.value = null;
  modalAction.value = null;
};

const cancelAction = () => {
  showConfirmModal.value = false;
  if (currentTask.value) {
    currentTask.value.confirmando = false; // Resetear estado de confirmación
  }
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
// Variables para paginación
const paginaActual = ref(1);
const itemsPorPagina = 10;

// Computed properties para paginación
const insumosBajoStockFiltrados = computed(() => {
  return stockFiltradoPorCategoria.value.filter((item) => item.bajoStock)
    .length;
});

const totalPaginas = computed(() => {
  return Math.ceil(stockFiltradoPorCategoria.value.length / itemsPorPagina);
});

const stockPaginado = computed(() => {
  const startIndex = (paginaActual.value - 1) * itemsPorPagina;
  const endIndex = startIndex + itemsPorPagina;
  return stockFiltradoPorCategoria.value.slice(startIndex, endIndex);
});

// Métodos de paginación
const paginaSiguiente = () => {
  if (paginaActual.value < totalPaginas.value) {
    paginaActual.value++;
  }
};

const paginaAnterior = () => {
  if (paginaActual.value > 1) {
    paginaActual.value--;
  }
};

// Función para obtener iconos según categoría
const getStockIcon = (categoria) => {
  const cat = categoria.toLowerCase();

  if (cat.includes("harina") || cat.includes("polvo")) return "🌾";
  if (cat.includes("azúcar") || cat.includes("dulce")) return "🍬";
  if (cat.includes("leche") || cat.includes("crema")) return "🥛";
  if (cat.includes("huevo")) return "🥚";
  if (cat.includes("fruta")) return "🍎";
  if (cat.includes("chocolate")) return "🍫";
  if (cat.includes("aceite") || cat.includes("grasa")) return "🫒";
  if (cat.includes("sal") || cat.includes("condimento")) return "🧂";
  if (cat.includes("empaque") || cat.includes("envase")) return "📦";
  if (cat.includes("líquido") || cat.includes("agua")) return "💧";

  return "📦";
};

// Método para ir a la página Stock con búsqueda
const irAStockConBusqueda = (nombreInsumo) => {
  // Navegar a la página Stock.vue y pasar el nombre como parámetro de consulta
  router.push({
    path: "/stock",
    query: { search: nombreInsumo },
  });
};

// ----------------------
// 🔹 Recetas
// ----------------------
const recetas = ref([]);
const loadingRecetas = ref(false);
const errorRecetas = ref(null);
// Variables para paginación de recetas
const paginaActualRecetas = ref(1);
const itemsPorPaginaRecetas = 8; // Menos items porque las recetas son más altas

// Computed properties para paginación de recetas
const totalPaginasRecetas = computed(() => {
  return Math.ceil(filteredRecetas.value.length / itemsPorPaginaRecetas);
});

const recetasPaginadas = computed(() => {
  const startIndex = (paginaActualRecetas.value - 1) * itemsPorPaginaRecetas;
  const endIndex = startIndex + itemsPorPaginaRecetas;
  return filteredRecetas.value.slice(startIndex, endIndex);
});

const inicioPaginaRecetas = computed(() => {
  return (paginaActualRecetas.value - 1) * itemsPorPaginaRecetas + 1;
});

const finPaginaRecetas = computed(() => {
  const endIndex = paginaActualRecetas.value * itemsPorPaginaRecetas;
  return endIndex > filteredRecetas.value.length
    ? filteredRecetas.value.length
    : endIndex;
});

const incrementarContador = async (receta) => {
  try {
    const response = await axios.post(`/api/recetas/${receta.id}/incrementar/`);

    if (response.data.error) {
      notificationSystem.show({
        type: "error",
        title: `❌ Stock insuficiente - ${
          response.data.receta_nombre || receta.nombre
        }`,
        message: response.data.error,
        insuficientes: response.data.insuficientes || [],
        timeout: 15000,
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
        // Usar el mismo formato para errores de catch
        notificationSystem.show({
          type: "error",
          title: `❌ Stock insuficiente - ${receta.nombre}`,
          message: err.response.data.error || "No hay suficiente stock",
          insuficientes: err.response.data.insuficientes,
          timeout: 15000,
        });
        return;
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

// Métodos de paginación de recetas
const paginaSiguienteRecetas = () => {
  if (paginaActualRecetas.value < totalPaginasRecetas.value) {
    paginaActualRecetas.value++;
  }
};

const paginaAnteriorRecetas = () => {
  if (paginaActualRecetas.value > 1) {
    paginaActualRecetas.value--;
  }
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
    if (a.estado !== "entregado" && b.estado === "entregado") return -1;
    if (a.estado === "entregado" && b.estado !== "entregado") return 1;
    // Luego por fecha
    return new Date(a.fecha_entrega) - new Date(b.fecha_entrega);
  });
});

const hacerHoyOrdenados = computed(() => {
  return [...hacerHoy.value].sort((a, b) => {
    // Primero los pendientes, luego los en preparación
    if (a.estado === "pendiente" && b.estado !== "pendiente") return -1;
    if (a.estado !== "pendiente" && b.estado === "pendiente") return 1;
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

    const index = entregarHoy.value.findIndex((p) => p.id === task.id);
    if (index !== -1) {
      entregarHoy.value[index].estado = "entregado";
      entregarHoy.value[index].confirmando = false; // Resetear estado
    }

    notificationSystem.show({
      type: "success",
      title: "¡Pedido entregado!",
      message: `El pedido de ${task.nombre} ha sido marcado como entregado`,
      timeout: 3000,
    });
  } catch (error) {
    console.error("Error al marcar como entregado:", error);
    // En caso de error, también resetear el estado
    const index = entregarHoy.value.findIndex((p) => p.id === task.id);
    if (index !== -1) {
      entregarHoy.value[index].confirmando = false;
    }
  }
};

const empezarPreparacion = async (task) => {
  try {
    await actualizarEstadoPedido(task.id, "listo", "hacerHoy");

    const index = hacerHoy.value.findIndex((p) => p.id === task.id);
    if (index !== -1) {
      hacerHoy.value[index].estado = "listo";
      hacerHoy.value[index].confirmando = false; // Resetear estado
    }

    notificationSystem.show({
      type: "info",
      title: "Pedido Terminado",
      message: `El pedido de ${task.nombre} ahora está listo`,
      timeout: 3000,
    });
  } catch (error) {
    console.error("Error al terminar pedido:", error);
    // En caso de error, también resetear el estado
    const index = hacerHoy.value.findIndex((p) => p.id === task.id);
    if (index !== -1) {
      hacerHoy.value[index].confirmando = false;
    }
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

// Helper methods para pedidos - CORREGIDO
const getEstadoText = (estado) => {
  const estados = {
    pendiente: "Pendiente",
    listo: "Listo",
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
        id: insumo.id,
        nombre: insumo.nombre,
        cantidad: insumo.stock_actual,
        stock_minimo: insumo.stock_minimo || 0,
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
const formatFecha = (fecha) => {
  if (!fecha) return "";

  // Crear fecha en la zona horaria local
  const fechaLocal = new Date(fecha);

  // Ajustar para compensar el offset de zona horaria
  const fechaAjustada = new Date(
    fechaLocal.getTime() + fechaLocal.getTimezoneOffset() * 60000
  );

  return fechaAjustada.toLocaleDateString("es-AR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
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

// Método para confirmar entrega
const confirmarEntrega = (task) => {
  if (task.estado === "entregado" || task.confirmando) return;

  // Prevenir múltiples clics
  task.confirmando = true;

  currentTask.value = task;
  modalType.value = "entrega";
  modalTitle.value = "Confirmar Entrega";
  modalMessage.value = `¿Estás seguro que quieres marcar como ENTREGADO el pedido?`;
  modalDetails.value = `Cliente: ${task.nombre}`;
  modalAction.value = () => marcarComoEntregado(task);

  showConfirmModal.value = true;
};

// Método para confirmar preparación
const confirmarPreparacion = (task) => {
  if (
    task.estado === "listo" ||
    task.estado === "entregado" ||
    task.confirmando
  )
    return;

  // Prevenir múltiples clics
  task.confirmando = true;

  currentTask.value = task;
  modalType.value = "preparacion";
  modalTitle.value = "Terminar pedido";
  modalMessage.value = `¿Estás seguro que quieres terminar el pedido?`;
  modalDetails.value = `Cliente: ${
    task.nombre
  }\nFecha de entrega: ${formatFecha(task.fecha_entrega)}`;
  modalAction.value = () => empezarPreparacion(task);

  showConfirmModal.value = true;
};
</script>

<style scoped>
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

/* -------------------- TAREAS/ITEMS DE PEDIDOS -------------------- */
.task-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border-radius: 10px;
  background: white;
  border-left: 4px solid #ddd;
  transition: all 0.3s ease;
}

.task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.task-item.pendiente {
  border-left-color: #e74c3c;
  background: white;
}

.task-item.listo {
  border-left-color: #27ae60;
  background: white;
}

.task-item.entregado {
  border-left-color: #27ae60;
  background: white;
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

.estado-badge.listo {
  background: #27ae60;
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
  margin-top: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e9ecef;
}

.search-form {
  margin: 0;
}

.search-input {
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  border-radius: 20px;
  width: 250px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #7b5a50;
  box-shadow: 0 0 0 2px rgba(123, 90, 80, 0.1);
}

/* Total del día */
.recetas-total {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--color-primary);
  color: white;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: bold;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.total-text {
  font-size: 0.8rem;
  opacity: 0.9;
}

.total-count {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 1.1rem;
}

/* Contenedor de lista con scroll */
.recetas-list-container {
  max-height: 60vh;
  overflow-y: auto;
}

/* Items de recetas mejorados */
.recetas-list {
  margin: 0;
  padding: 0;
}

/* -------------------- ITEMS DE RECETAS MEJORADOS -------------------- */
.receta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border-radius: 10px;
  border: 2px solid #f8f9fa;
  background: white;
  transition: all 0.3s ease;
  position: relative;
  min-height: 70px;
}

.receta-item:hover {
  border-color: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.receta-item.receta-activa {
  border-color: #27ae60;
  background: #f8fff9;
}

.receta-info-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.receta-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 1.2rem;
}

.receta-item.receta-activa .receta-icon {
  background: #27ae60;
  color: white;
}

.receta-info-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.receta-info {
  display: flex;
  flex-direction: column;
}

.receta-nombre {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.receta-rinde {
  font-size: 0.85rem;
  color: #666;
}

/* -------------------- CONTADOR MEJORADO -------------------- */
/* Contador mejorado */
.contador-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.contador-label {
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
}

.contador {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 0.25rem;
  border: 1px solid #e9ecef;
}

.btn-contador {
  width: 32px;
  height: 32px;
  border: none;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-menos {
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.btn-menos:hover:not(.btn-disabled) {
  background: #e74c3c;
  color: white;
  transform: scale(1.1);
}

.btn-mas {
  color: #27ae60;
  border: 1px solid #27ae60;
}

.btn-mas:hover {
  background: #27ae60;
  color: white;
  transform: scale(1.1);
}

.btn-disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
}

.btn-disabled:hover {
  background: white !important;
  color: #e74c3c !important;
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
  min-width: 40px;
  text-align: center;
  font-size: 1.1rem;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.contador-cero {
  color: #999;
  background: transparent;
}

.contador-activo {
  color: #27ae60;
  background: rgba(39, 174, 96, 0.1);
  font-weight: 800;
}

/* Estado vacío */
.recetas-empty {
  text-align: center;
  padding: 3rem 2rem;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-text {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-subtext {
  font-size: 0.9rem;
  opacity: 0.7;
}

/* Scroll personalizado */
.recetas-list::-webkit-scrollbar {
  width: 6px;
}

.recetas-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.recetas-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.recetas-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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

/* -------------------- STOCK MEJORADO -------------------- */
.stock-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.filtro-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-select {
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  border-radius: 20px;
  width: 250px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.category-select:focus {
  outline: none;
  border-color: #7b5a50;
  box-shadow: 0 0 0 2px rgba(123, 90, 80, 0.1);
}

/* Resumen del stock */
.stock-resumen {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--color-primary);
  color: white;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: bold;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.resumen-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.25rem;
}

.resumen-label {
  font-size: 0.8rem;
  opacity: 0.9;
}

.resumen-value {
  font-size: 1.1rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
}

.resumen-value.alert {
  background: rgba(231, 76, 60, 0.3);
}

/* Lista de stock */
.stock-list-container {
  max-height: 60vh;
  overflow-y: auto;
}

.stock-list {
  margin: 0;
  padding: 0;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  border: 2px solid #f8f9fa;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 60px;
}

.stock-item:hover {
  border-color: #e9ecef;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stock-item.low-stock {
  border-color: #e74c3c;
  background: #fff5f5;
}

.stock-item.stock-item-activo {
  border-color: #e74c3c;
  background: #fff5f5;
}

.stock-item.low-stock:hover {
  background: #ffdf7e;
}

.stock-info-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.stock-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 1rem;
}

.stock-item.low-stock .stock-icon {
  background: #e74c3c;
  color: white;
}

.stock-info {
  display: flex;
  flex-direction: column;
}

.item-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
  margin-bottom: 0.1rem;
}

.item-category {
  font-size: 0.8rem;
  color: #666;
  background: #f8f9fa;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  display: inline-block;
}

/* Datos de stock */
.stock-data {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.stock-cantidad,
.stock-minimo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  min-width: 100px;
}

.data-label {
  font-size: 0.75rem;
  color: #666;
  font-weight: 500;
}

.item-quantity {
  font-weight: bold;
  font-size: 0.95rem;
  color: #2c3e50;
}

.item-quantity.low-stock-text {
  color: #e74c3c;
  font-weight: 800;
}

.item-minimum {
  font-size: 0.9rem;
  color: #666;
}

/* Estado vacío */
.stock-empty {
  text-align: center;
  padding: 2rem 1rem;
  color: #7f8c8d;
}

/* Paginación */
.paginacion {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-top: 1px solid #e9ecef;
  margin-top: 1rem;
}

.btn-paginacion {
  padding: 0.6rem 1.2rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  color: #7b5a50;
}

.btn-paginacion:hover:not(.btn-disabled) {
  background: #7b5a50;
  color: white;
  border-color: #7b5a50;
  transform: translateY(-1px);
}

.btn-disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none !important;
}

.btn-disabled:hover {
  background: white !important;
  color: #7b5a50 !important;
  border-color: #ddd !important;
}

.paginacion-info {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

/* Scroll personalizado */
.stock-list-container::-webkit-scrollbar {
  width: 6px;
}

.stock-list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.stock-list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.stock-list-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* -------------------- CARDS CON HEADER FIJO MEJORADO -------------------- */
.card.entregar-hoy,
.card.hacer-hoy {
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}

.entregar-hoy-header-container,
.hacer-hoy-header-container {
  flex-shrink: 0;
  background: var(--color-background);
  border-radius: 10px 10px 0 0;
}

.entregar-hoy-list,
.hacer-hoy-list {
  overflow-y: auto;
  flex-grow: 1;
  padding: 10px;
  margin: 0;
}

/* Header fijo para todas las cards */
.card-header.sticky-header {
  position: sticky;
  top: 0;
  background: var(--color-background);
  z-index: 10;
  padding: 15px 8px;
  margin: -8px -8px 15px -8px;
  border-radius: 10px 10px 0 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid #e9ecef;
}

/* Asegurar que el contenido de las tareas se vea bien */
.entregar-hoy-list,
.hacer-hoy-list {
  padding: 0 8px 8px 8px;
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
.task-checkbox:hover input:not(:disabled) ~ .checkmark {
  border-color: #7b5a50;
}

/* Cuando el checkbox está checked */
.task-checkbox input:checked ~ .checkmark {
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
.task-checkbox input:checked ~ .checkmark:after {
  display: block;
}

/* Estilos para estado deshabilitado */
.task-checkbox input:disabled ~ .checkmark {
  background: #f0f0f0;
  border-color: #ddd;
  cursor: not-allowed;
}

.task-checkbox input:disabled:checked ~ .checkmark {
  background: #95a5a6;
  border-color: #95a5a6;
}

.task-checkbox input:disabled ~ .checkmark:after {
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

/* ==================== MEDIA QUERIES PARA RESPONSIVE (764px - 1024px) ==================== */

@media (min-width: 764px) and (max-width: 1024px) {
  /* -------------------- LAYOUT GENERAL -------------------- */
  .container {
    padding: 0.5rem;
  }

  /* -------------------- HEADERS DE CARDS -------------------- */
  .card-header {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
    text-align: center;
  }

  .sticky-header {
    padding: 12px 6px;
    margin: -6px -6px 12px -6px;
  }

  /* -------------------- TAREAS/ITEMS DE PEDIDOS -------------------- */
  .task-item {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .cliente-nombre {
    font-size: 1rem;
  }

  .estado-badge {
    font-size: 0.7rem;
    padding: 0.25rem 0.6rem;
    align-self: flex-start;
  }

  .task-details {
    font-size: 0.85rem;
  }

  /* -------------------- HEADER DE RECETAS -------------------- */
  .recetas-header {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }

  .search-input {
    width: 100%;
    max-width: 100%;
  }

  /* -------------------- ITEMS DE RECETAS -------------------- */
  .receta-item {
    flex-direction: row;
    align-items: stretch;
  }

  .receta-info-container {
    justify-content: flex-start;
  }

  .contador-container {
    justify-content: flex-end;
  }

  .contador {
    margin-left: auto;
  }

  .recetas-total {
    flex-direction: row;
    gap: 0.5rem;
    text-align: center;
  }

  .receta-info {
    width: 100%;
  }

  .contador {
    align-self: flex-end;
  }

  /* -------------------- STOCK ITEMS -------------------- */
  .stock-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .filtro-container {
    justify-content: space-between;
  }

  .stock-item {
    flex-direction: row;
    align-items: stretch;
    gap: 1rem;
  }

  .stock-info-container {
    justify-content: flex-start;
  }

  .stock-data {
    justify-content: space-between;
    width: 100%;
  }

  .stock-cantidad,
  .stock-minimo {
    min-width: auto;
    flex: 1;
  }

  .stock-resumen {
    flex-direction: row;
    gap: 0.75rem;
    text-align: center;
  }

  .resumen-item {
    flex-direction: row;
    gap: 0.5rem;
  }

  .paginacion {
    flex-direction: row;
    gap: 0.75rem;
  }

  .btn-paginacion {
    width: 25%;
    text-align: center;
  }

  /* -------------------- CARDS CON SCROLL -------------------- */
  .card.entregar-hoy,
  .card.hacer-hoy {
    max-height: 75vh;
  }

  .entregar-hoy-list,
  .hacer-hoy-list {
    padding: 8px 6px;
  }

  /* -------------------- CHECKBOX -------------------- */
  .task-checkbox {
    padding-left: 28px;
    margin-right: 0.75rem;
  }

  .checkmark {
    height: 18px;
    width: 18px;
  }

  .checkmark:after {
    left: 5px;
    top: 1px;
    width: 4px;
    height: 8px;
  }

  /* -------------------- MODAL DE CONFIRMACIÓN -------------------- */
  .confirm-modal {
    max-width: 90%;
    margin: 1rem;
  }

  .modal-buttons {
    flex-direction: column;
    gap: 0.75rem;
  }

  .modal-buttons button {
    min-width: auto;
    width: 100%;
  }

  .confirm-icon {
    font-size: 2.5rem;
  }

  .modal-title {
    font-size: 1.2rem;
  }

  .confirm-message {
    font-size: 1rem;
  }

  /* -------------------- BADGES Y ETIQUETAS -------------------- */
  .badge {
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
  }

  .atrasado-badge {
    font-size: 0.65rem;
    padding: 1px 4px;
  }

  .dias-restantes {
    font-size: 0.75rem;
  }

  .alert-preparacion,
  .entregado-info,
  .preparacion-info {
    font-size: 0.75rem;
    padding: 0.4rem;
  }

  /* -------------------- CONTADOR MEJORADO -------------------- */
  .btn-contador {
    width: 26px;
    height: 26px;
  }

  .contador-value {
    min-width: 26px;
    font-size: 0.9rem;
  }
}

/* ==================== MEDIA QUERIES ADICIONALES PARA MÓVILES ==================== */

@media (max-width: 763px) {
  /* Estilos específicos para móviles si es necesario */
  .card-header {
    flex-direction: column;
    gap: 0.5rem;
  }

  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .recetas-header {
    flex-direction: row;
    gap: 0.5rem;
  }

  .search-input {
    width: 100%;
  }

  .receta-item {
    flex-direction: row;
    align-items: stretch;
    gap: 1rem;
  }

  .contador-container {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .recetas-total {
    flex-direction: row;
    gap: 0.5rem;
    text-align: center;
  }

  .btn-contador {
    width: 36px;
    height: 36px;
  }

  .contador-value {
    min-width: 36px;
    font-size: 1rem;
  }

  .stock-item {
    flex-direction: row;
    gap: 0.25rem;
  }

  .stock-controls {
    flex-direction: column;
    gap: 0.5rem;
  }

  .filtro-container {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .stock-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    padding: 0.75rem;
  }

  .stock-data {
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }

  .stock-cantidad,
  .stock-minimo {
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }

  .stock-resumen {
    flex-direction: column;
    gap: 0.5rem;
  }

  .paginacion {
    flex-direction: column;
    gap: 0.5rem;
  }

  .btn-paginacion {
    width: 100%;
  }
}

/* ==================== MEDIA QUERIES PARA ESCRITORIO GRANDE ==================== */

@media (min-width: 1025px) {
  /* Estilos específicos para escritorio grande si es necesario */
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
</style>
