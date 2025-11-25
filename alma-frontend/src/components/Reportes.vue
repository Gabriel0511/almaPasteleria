<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <div class="reportes-container">
          <!-- Encabezado y Filtros -->
          <div class="principal-content">
            <h1 class="reportes-card-title1">Reportes</h1>

            <div
              class="reportes-filtros-mobile-toggle"
              v-if="isMobile"
              @click="mostrarFiltros = !mostrarFiltros"
            >
              <i
                class="fas"
                :class="mostrarFiltros ? 'fa-chevron-up' : 'fa-filter'"
              ></i>
              {{ mostrarFiltros ? "Ocultar Filtros" : "Mostrar Filtros" }}
            </div>

            <div
              class="reportes-filtros-derecha"
              :class="{ 'reportes-filtros-visible': mostrarFiltros }"
            >
              <div class="reportes-filtro-group">
                <label for="fecha-inicio">Fecha Inicio</label>
                <input
                  id="fecha-inicio"
                  type="date"
                  v-model="filtros.fechaInicio"
                  class="reportes-filtro-input"
                />
              </div>

              <div class="reportes-filtro-group">
                <label for="fecha-fin">Fecha Fin</label>
                <input
                  id="fecha-fin"
                  type="date"
                  v-model="filtros.fechaFin"
                  class="reportes-filtro-input"
                />
              </div>

              <div class="reportes-filtro-group">
                <label for="proveedor">Proveedor</label>
                <select
                  id="proveedor"
                  v-model="filtros.proveedorId"
                  class="reportes-filtro-select"
                >
                  <option value="">Todos los proveedores</option>
                  <option
                    v-for="proveedor in proveedores"
                    :key="proveedor.id"
                    :value="proveedor.id"
                  >
                    {{ proveedor.nombre }}
                  </option>
                </select>
              </div>
              <button
                @click="limpiarFiltros"
                class="reportes-btn-agregar"
                style="background-color: #6c757d"
              >
                <i class="fas fa-eraser"></i>
                Limpiar
              </button>
            </div>
          </div>

          <!-- Pestañas para las 4 tablas -->
          <div class="tabs-container">
            <div class="tabs-header">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="cambiarTab(tab.id)"
                class="tab-button"
                :class="{ active: tabActiva === tab.id }"
              >
                <i :class="tab.icono"></i>
                {{ tab.nombre }}
                <span class="badge-contador">
                  {{ obtenerContador(tab.id) }}
                </span>
              </button>
            </div>

            <!-- Contenido de las pestañas -->
            <div class="tabs-content">
              <!-- Pestaña 1: Reporte de Insumos -->
              <div v-show="tabActiva === 'reporte-insumos'" class="tab-pane">
                <!-- Tabla de Reportes -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">Reporte de Insumos utilizados</h3>
                    <!-- Botón Generar PDF para reportes -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="reporteFiltrado.length > 0"
                    >
                      <button
                        @click="generarPDF"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDF"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Insumo</th>
                          <th>Stock Usado</th>
                          <th>Stock Actual</th>
                          <th>Stock Mínimo</th>
                          <th>¿Reponer?</th>
                          <th>Proveedor</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in reporteFiltrado"
                          :key="item.id"
                          :class="{
                            'reportes-fila-stock-bajo': item.necesitaReposicion,
                          }"
                        >
                          <td class="reportes-columna-insumo-nombre">
                            {{ item.nombre }}
                            <span class="reportes-categoria-insumo"
                              >({{ item.categoria }})</span
                            >
                          </td>
                          <td class="reportes-columna-stock-usado">
                            {{ formatDecimal(item.stockUsado) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-stock-actual">
                            {{ formatDecimal(item.stockActual) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-stock-minimo">
                            {{ formatDecimal(item.stockMinimo) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-reposicion">
                            <span
                              class="reportes-badge"
                              :class="
                                item.necesitaReposicion ? 'alert' : 'success'
                              "
                            >
                              {{ item.necesitaReposicion ? "SÍ" : "NO" }}
                            </span>
                          </td>
                          <td class="reportes-columna-proveedor">
                            {{ item.proveedor || "Sin proveedor" }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loading" class="reportes-loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando reporte...</p>
                    </div>
                    <div
                      v-else-if="reporteFiltrado.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-inbox"></i>
                      <p>
                        No hay insumos con stock usado en el período
                        seleccionado
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pestaña 2: Lista de Compras -->
              <div v-show="tabActiva === 'lista-compras'" class="tab-pane">
                <!-- Tabla de Lista de Compras -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">
                      📋 Lista de Compras - Próxima Semana
                    </h3>
                    <!-- Botón Generar PDF para lista de compras -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="listaComprasFiltrada.length > 0"
                    >
                      <button
                        @click="generarPDFListaCompras"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDFListaCompras"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Insumo</th>
                          <th>Stock Actual</th>
                          <th>Stock Mínimo</th>
                          <th>Pedidos</th>
                          <th>Compra sugerida</th>
                          <th>Proveedor</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in listaComprasFiltrada"
                          :key="'compra-' + item.id"
                          :class="{
                            'reportes-fila-urgente': item.totalComprar > 0,
                          }"
                        >
                          <td class="reportes-columna-insumo-nombre">
                            {{ item.nombre }}
                            <span class="reportes-categoria-insumo"
                              >({{ item.categoria }})</span
                            >
                          </td>
                          <td class="reportes-columna-stock-actual">
                            {{ formatDecimal(item.stockActual) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-stock-minimo">
                            {{ formatDecimal(item.stockMinimo) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-pedidos">
                            {{ formatDecimal(item.pedidos) }} {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-total-comprar">
                            <strong
                              >{{ formatDecimal(item.totalComprar) }}
                              {{ item.unidad }}</strong
                            >
                          </td>
                          <td class="reportes-columna-proveedor">
                            {{ item.proveedor || "Sin proveedor" }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div
                      v-if="loadingListaCompras"
                      class="reportes-loading-state"
                    >
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando lista de compras...</p>
                    </div>
                    <div
                      v-else-if="listaComprasFiltrada.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-check-circle"></i>
                      <p>
                        No hay insumos para comprar con los filtros actuales
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pestaña 3: Recetas Hechas -->
              <div v-show="tabActiva === 'recetas-hechas'" class="tab-pane">
                <!-- Tabla de Recetas Hechas -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">🍽️ Recetas Hechas - Historial</h3>
                    <div class="reportes-fecha-info">
                      <span v-if="filtros.fechaInicio && filtros.fechaFin">
                        Mostrando preparaciones del
                        {{ formatearFecha(filtros.fechaInicio) }} al
                        {{ formatearFecha(filtros.fechaFin) }}
                      </span>
                      <span v-else> Mostrando todas las preparaciones </span>
                    </div>
                    <!-- Botón Generar PDF para recetas hechas -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="recetasHechasFiltradas.length > 0"
                    >
                      <button
                        @click="generarPDFRecetas"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDFRecetas"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Receta</th>
                          <th>Total Preparado</th>
                          <th>Costo Total</th>
                          <th>Fecha de preparación</th>
                          <th>Precio Venta</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in recetasHechasFiltradas"
                          :key="'receta-' + item.id"
                        >
                          <td class="reportes-columna-receta-nombre">
                            {{ item.nombre }}
                          </td>
                          <td class="reportes-columna-cantidad">
                            {{ item.cantidad }}
                            {{ item.cantidad === 1 ? "vez" : "veces" }}
                          </td>
                          <td class="reportes-columna-costo">
                            ${{ formatDecimal(item.costo_total) }}
                          </td>
                          <td class="reportes-columna-fecha">
                            {{ formatearFecha(item.ultima_preparacion) }}
                          </td>
                          <td class="reportes-columna-precio">
                            ${{ formatDecimal(item.precio_venta) }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingRecetas" class="reportes-loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando preparaciones...</p>
                    </div>
                    <div
                      v-else-if="recetasHechasFiltradas.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-utensils"></i>
                      <p>No hay preparaciones en el período seleccionado</p>
                      <small>
                        Las preparaciones aparecerán aquí después de usar el
                        botón "Preparar"
                      </small>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pestaña 4: Pedidos -->
              <div v-show="tabActiva === 'pedidos'" class="tab-pane">
                <!-- Tabla de Pedidos -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">📦 Pedidos Entregados</h3>
                    <div class="reportes-fecha-info">
                      <span v-if="filtros.fechaInicio && filtros.fechaFin">
                        Mostrando pedidos del
                        {{ formatearFecha(filtros.fechaInicio) }} al
                        {{ formatearFecha(filtros.fechaFin) }}
                      </span>
                      <span v-else>
                        Mostrando todos los pedidos entregados
                      </span>
                    </div>
                    <!-- Botón Generar PDF para pedidos -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="pedidosFiltrados.length > 0"
                    >
                      <button
                        @click="generarPDFPedidos"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDFPedidos"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Pedido ID</th>
                          <th>Cliente</th>
                          <th>Recetas</th>
                          <th>Fecha Entrega</th>
                          <th>Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in pedidosFiltrados"
                          :key="'pedido-' + item.id"
                          :class="{
                            'reportes-fila-pedido-urgente':
                              item.estado === 'pendiente',
                          }"
                        >
                          <td class="reportes-columna-pedido-id">
                            #{{ item.id }}
                          </td>
                          <td class="reportes-columna-cliente">
                            {{ item.cliente }}
                          </td>
                          <td class="reportes-columna-recetas">
                            <div class="recetas-pedido-detalle">
                              {{ getRecetasText(item.detalles) }}
                            </div>
                            <!-- Mostrar ingredientes extra si existen -->
                            <div
                              v-if="hasIngredientesExtra(item.detalles)"
                              class="ingredientes-extra-detalle"
                            >
                              <small>
                                <strong>Ingredientes extra:</strong>
                                {{ getIngredientesExtraText(item.detalles) }}
                              </small>
                            </div>
                          </td>
                          <td class="reportes-columna-fecha">
                            {{ formatearFecha(item.fecha_entrega) }}
                          </td>
                          <td class="reportes-columna-total">
                            ${{ formatDecimal(item.total) }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingPedidos" class="reportes-loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando pedidos...</p>
                    </div>
                    <div
                      v-else-if="pedidosFiltrados.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-shopping-bag"></i>
                      <p>No hay pedidos para la fecha seleccionada</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";

const router = useRouter();

// Referencia al sidebar para controlarlo desde el header
const sidebarRef = ref(null);

// Estado para controlar la pestaña activa
const tabActiva = ref("reporte-insumos");

// Definición de las pestañas
const tabs = ref([
  {
    id: "reporte-insumos",
    nombre: "Reporte de Insumos",
    icono: "fas fa-boxes",
  },
  {
    id: "lista-compras",
    nombre: "Lista de Compras",
    icono: "fas fa-shopping-cart",
  },
  { id: "recetas-hechas", nombre: "Recetas Hechas", icono: "fas fa-utensils" },
  { id: "pedidos", nombre: "Pedidos", icono: "fas fa-clipboard-list" },
]);

// Método para cambiar de pestaña
const cambiarTab = (tabId) => {
  tabActiva.value = tabId;
};

// Método para obtener el contador de elementos por pestaña
const obtenerContador = (tabId) => {
  switch (tabId) {
    case "reporte-insumos":
      return reporteFiltrado.value.length;
    case "lista-compras":
      return listaComprasFiltrada.value.length;
    case "recetas-hechas":
      return recetasHechasFiltradas.value.length;
    case "pedidos":
      return pedidosFiltrados.value.length;
    default:
      return 0;
  }
};

// Método para alternar el sidebar desde el header
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};

// ----------------------
// 🔹 Estado y Datos
// ----------------------
const reportes = ref([]);
const listaCompras = ref([]);
const recetasHechas = ref([]);
const pedidos = ref([]);
const proveedores = ref([]);
const loading = ref(true);
const loadingListaCompras = ref(false);
const loadingRecetas = ref(false);
const loadingPedidos = ref(false);
const generandoPDF = ref(false);
const generandoPDFListaCompras = ref(false);
const generandoPDFRecetas = ref(false);
const generandoPDFPedidos = ref(false);
const mostrarFiltros = ref(false);
const isMobile = ref(false);
const fechaHoy = ref(new Date().toISOString().split("T")[0]);

// Filtros
const filtros = ref({
  fechaInicio: "",
  fechaFin: "",
  proveedorId: "",
});

// ----------------------
// 🔹 Computed Properties
// ----------------------
const pedidosFiltrados = computed(() => {
  // Filtrar solo pedidos entregados en el frontend
  const pedidosEntregados = pedidos.value.filter(
    (pedido) => pedido.estado === "entregado"
  );

  // Aplicar filtro de fecha si existe
  if (filtros.value.fechaInicio && filtros.value.fechaFin) {
    return pedidosEntregados.filter((pedido) => {
      const fechaEntrega = new Date(pedido.fecha_entrega);
      const fechaInicio = new Date(filtros.value.fechaInicio);
      const fechaFin = new Date(filtros.value.fechaFin);

      return fechaEntrega >= fechaInicio && fechaEntrega <= fechaFin;
    });
  }

  return pedidosEntregados;
});

const reporteFiltrado = computed(() => {
  let filtered = [...reportes.value];

  // Filtrar por proveedor
  if (filtros.value.proveedorId) {
    filtered = filtered.filter(
      (item) => item.proveedorId === parseInt(filtros.value.proveedorId)
    );
  }

  filtered = filtered.filter((item) => item.stockUsado > 0);

  return filtered;
});

const listaComprasFiltrada = computed(() => {
  let filtered = [...listaCompras.value];

  // Filtrar por proveedor
  if (filtros.value.proveedorId) {
    filtered = filtered.filter(
      (item) => item.proveedorId === parseInt(filtros.value.proveedorId)
    );
  }

  // Mostrar solo los insumos que necesitan compra
  return filtered.filter((item) => item.totalComprar > 0);
});

const recetasHechasFiltradas = computed(() => {
  return recetasHechas.value;
});

const insumosReponer = computed(() => {
  return reporteFiltrado.value.filter((item) => item.necesitaReposicion).length;
});

// ----------------------
// 🔹 Métodos
// ----------------------
const aplicarFiltros = () => {
  // Recargar datos con los filtros aplicados
  fetchReportes();
  fetchListaCompras();
  fetchRecetasHechas();
  fetchPedidos();
};

const limpiarFiltros = () => {
  filtros.value = {
    fechaInicio: "",
    fechaFin: "",
    proveedorId: "",
  };

  fetchReportes();
  fetchListaCompras();
  fetchRecetasHechas();
  fetchPedidos();
};

const formatDecimal = (value) => {
  if (!value) return "0";
  // Eliminar ceros decimales innecesarios
  const num = parseFloat(value);
  return num % 1 === 0 ? num.toString() : num.toFixed(3).replace(/\.?0+$/, "");
};

const formatearFecha = (fecha) => {
  if (!fecha) return "";

  try {
    // Si la fecha ya es un string en formato YYYY-MM-DD
    if (typeof fecha === "string" && /^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
      const [year, month, day] = fecha.split("-");
      const fechaUTC = new Date(Date.UTC(year, month - 1, day));

      const opciones = {
        year: "numeric",
        month: "long",
        day: "numeric",
        timeZone: "UTC",
      };
      return fechaUTC.toLocaleDateString("es-ES", opciones);
    }

    // Si es una fecha ISO (con tiempo)
    const fechaObj = new Date(fecha);
    if (isNaN(fechaObj.getTime())) {
      return "Fecha inválida";
    }

    const opciones = {
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    return fechaObj.toLocaleDateString("es-ES", opciones);
  } catch (error) {
    console.error("Error formateando fecha:", error, fecha);
    return "Fecha inválida";
  }
};

const getRecetasText = (detalles) => {
  if (!detalles || detalles.length === 0) {
    return "Sin recetas";
  }

  return detalles
    .map((detalle) => {
      const recetaNombre = detalle.receta?.nombre || "Receta no disponible";
      const cantidad = detalle.cantidad || 1;
      return `${recetaNombre} (x${cantidad})`;
    })
    .join(", ");
};

const hasIngredientesExtra = (detalles) => {
  if (!detalles) return false;
  return detalles.some(
    (detalle) =>
      detalle.ingredientes_extra && detalle.ingredientes_extra.length > 0
  );
};

const getIngredientesExtraText = (detalles) => {
  if (!detalles) return "";

  const ingredientesExtra = [];
  detalles.forEach((detalle) => {
    if (detalle.ingredientes_extra && detalle.ingredientes_extra.length > 0) {
      detalle.ingredientes_extra.forEach((ing) => {
        const insumoNombre = ing.insumo?.nombre || "Insumo no disponible";
        const cantidad = ing.cantidad || 0;
        const unidad = ing.unidad_medida?.abreviatura || "u";
        ingredientesExtra.push(`${insumoNombre}: ${cantidad} ${unidad}`);
      });
    }
  });

  return ingredientesExtra.join(", ");
};

const getEstadoText = (estado) => {
  const estados = {
    pendiente: "Pendiente",
    listo: "Listo",
    entregado: "Entregado",
  };
  return estados[estado] || estado;
};

const getClaseEstadoPedido = (estado) => {
  const clasesEstados = {
    entregado: "success",
    pendiente: "warning",
    listo: "info",
  };
  return clasesEstados[estado] || "default";
};

const getClaseEstadoReceta = (estado) => {
  const clasesEstados = {
    Completado: "success",
    "En proceso": "warning",
    Cancelado: "alert",
  };
  return clasesEstados[estado] || "default";
};

const generarPDF = async () => {
  try {
    generandoPDF.value = true;

    // Construir parámetros de filtro para el PDF
    const params = {};
    if (filtros.value.fechaInicio)
      params.fecha_inicio = filtros.value.fechaInicio;
    if (filtros.value.fechaFin) params.fecha_fin = filtros.value.fechaFin;
    if (filtros.value.proveedorId)
      params.proveedor_id = filtros.value.proveedorId;

    // Hacer la petición para generar el PDF
    const response = await axios.get("/api/reportes/generar-pdf/", {
      params: params,
      responseType: "blob", // Importante para descargar archivos
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `reporte_insumos_${new Date().toISOString().split("T")[0]}.pdf`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDF.value = false;
  }
};

const generarPDFListaCompras = async () => {
  try {
    generandoPDFListaCompras.value = true;

    // Construir parámetros de filtro para el PDF
    const params = {};
    if (filtros.value.fechaInicio)
      params.fecha_inicio = filtros.value.fechaInicio;
    if (filtros.value.fechaFin) params.fecha_fin = filtros.value.fechaFin;
    if (filtros.value.proveedorId)
      params.proveedor_id = filtros.value.proveedorId;

    // Hacer la petición para generar el PDF de lista de compras
    const response = await axios.get(
      "/api/reportes/generar-pdf-lista-compras/",
      {
        params: params,
        responseType: "blob",
      }
    );

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `lista_compras_${new Date().toISOString().split("T")[0]}.pdf`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF de lista de compras:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDFListaCompras.value = false;
  }
};

const generarPDFRecetas = async () => {
  try {
    generandoPDFRecetas.value = true;

    const params = {};
    if (filtros.value.fechaInicio)
      params.fecha_inicio = filtros.value.fechaInicio;
    if (filtros.value.fechaFin) params.fecha_fin = filtros.value.fechaFin;

    const response = await axios.get("/api/recetas-por-fecha/pdf/", {
      params: params,
      responseType: "blob",
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    // Nombre del archivo basado en las fechas de filtro
    let fileName = "recetas_hechas";
    if (filtros.value.fechaInicio && filtros.value.fechaFin) {
      fileName = `recetas_${filtros.value.fechaInicio}_a_${filtros.value.fechaFin}`;
    } else {
      fileName = `recetas_${new Date().toISOString().split("T")[0]}`;
    }

    link.setAttribute("download", `${fileName}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF de recetas:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDFRecetas.value = false;
  }
};

const generarPDFPedidos = async () => {
  try {
    generandoPDFPedidos.value = true;

    // Usar la misma endpoint con los mismos filtros
    const response = await axios.get("/api/pedidos/entregados/", {
      params: {
        fecha_inicio: filtros.value.fechaInicio,
        fecha_fin: filtros.value.fechaFin,
      },
      responseType: "blob",
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `pedidos_entregados_${new Date().toISOString().split("T")[0]}.pdf`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF de pedidos:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDFPedidos.value = false;
  }
};

const fetchRecetasHoy = async () => {
  try {
    loadingRecetas.value = true;

    // Usar la fecha seleccionada en el filtro (por defecto hoy)
    const fecha = fechaRecetas.value || new Date().toISOString().split("T")[0];

    const response = await axios.get("/api/recetas-por-fecha/", {
      params: { fecha: fecha },
    });

    if (!response.data) {
      throw new Error("No se recibieron datos del servidor para recetas");
    }

    console.log("📊 Recetas del historial recibidas:", response.data);

    // Mapear los datos de la respuesta
    recetasHechas.value = response.data.recetas.map((item) => ({
      id: item.id,
      receta_id: item.receta_id,
      nombre: item.nombre,
      cantidad: item.cantidad,
      fecha: item.fecha,
      hora: item.hora,
      estado: item.estado,
      rinde: item.rinde,
      unidad_rinde: item.unidad_rinde,
      costo_total: item.costo_total,
      precio_venta: item.precio_venta,
    }));

    console.log(
      `📊 Recetas cargadas para ${fecha}: ${recetasHechas.value.length}`
    );
  } catch (error) {
    console.error("Error al cargar recetas del historial:", error);
    recetasHechas.value = [];
  } finally {
    loadingRecetas.value = false;
  }
};

// ----------------------
// 🔹 Fetch Datos
// ----------------------
const fetchReportes = async () => {
  try {
    loading.value = true;

    const params = {};
    if (filtros.value.fechaInicio)
      params.fecha_inicio = filtros.value.fechaInicio;
    if (filtros.value.fechaFin) params.fecha_fin = filtros.value.fechaFin;
    if (filtros.value.proveedorId)
      params.proveedor_id = filtros.value.proveedorId;

    const response = await axios.get("/api/reportes/insumos/", { params });

    // ✅ VERIFICAR que la respuesta tenga datos
    if (!response.data) {
      throw new Error("No se recibieron datos del servidor");
    }

    reportes.value = response.data.map((item) => ({
      id: item.id,
      nombre: item.nombre,
      categoria: item.categoria,
      stockUsado: item.stock_usado || 0, // ✅ CORREGIDO: stock_usado
      stockActual: item.stock_actual,
      stockMinimo: item.stock_minimo,
      unidad: item.unidad_medida?.abreviatura || "u",
      necesitaReposicion: item.necesita_reposicion,
      proveedor: item.proveedor?.nombre || "Sin proveedor",
      proveedorId: item.proveedor?.id || null,
    }));
  } catch (error) {
    console.error("Error al cargar reportes:", error);
    reportes.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchListaCompras = async () => {
  try {
    loadingListaCompras.value = true;

    const params = {};
    if (filtros.value.fechaInicio)
      params.fecha_inicio = filtros.value.fechaInicio;
    if (filtros.value.fechaFin) params.fecha_fin = filtros.value.fechaFin;
    if (filtros.value.proveedorId)
      params.proveedor_id = filtros.value.proveedorId;

    const response = await axios.get("/api/reportes/lista-compras/", {
      params,
    });

    if (!response.data) {
      throw new Error(
        "No se recibieron datos del servidor para lista de compras"
      );
    }

    listaCompras.value = response.data.map((item) => ({
      id: item.id,
      nombre: item.nombre,
      categoria: item.categoria,
      stockActual: item.stock_actual,
      stockMinimo: item.stock_minimo,
      pedidos: item.pedidos || 0,
      totalComprar: item.total_comprar || 0,
      unidad: item.unidad_medida?.abreviatura || "u",
      proveedor: item.proveedor?.nombre || "Sin proveedor",
      proveedorId: item.proveedor?.id || null,
      diaCompra: item.dia_compra || "Sin asignar",
    }));
  } catch (error) {
    console.error("Error al cargar lista de compras:", error);
    listaCompras.value = [];
  } finally {
    loadingListaCompras.value = false;
  }
};

const fetchRecetasHechas = async () => {
  try {
    loadingRecetas.value = true;

    const params = {};
    if (filtros.value.fechaInicio)
      params.fecha_inicio = filtros.value.fechaInicio;
    if (filtros.value.fechaFin) params.fecha_fin = filtros.value.fechaFin;

    console.log(
      "📊 Haciendo petición a /api/recetas-por-fecha/ con params:",
      params
    );

    const response = await axios.get("/api/recetas-por-fecha/", {
      params: params,
    });

    console.log("📊 Respuesta recibida:", response.data);

    if (!response.data) {
      throw new Error(
        "No se recibieron datos del servidor para recetas hechas"
      );
    }

    // Si el backend devuelve un error, mostrarlo
    if (response.data.error) {
      console.error("Error del backend:", response.data.error);
      recetasHechas.value = [];
      return;
    }

    recetasHechas.value = response.data.recetas.map((item) => ({
      id: item.id,
      nombre: item.nombre,
      cantidad: item.cantidad,
      rinde: item.rinde,
      unidad_rinde: item.unidad_rinde,
      costo_total: item.costo_total,
      precio_venta: item.precio_venta,
      veces_hecha_hoy: item.veces_hecha_hoy,
      ultima_preparacion: item.ultima_preparacion,
    }));

    console.log("📊 Datos procesados:", recetasHechas.value);
  } catch (error) {
    console.error("Error al cargar preparaciones:", error);
    recetasHechas.value = [];
  } finally {
    loadingRecetas.value = false;
  }
};

const fetchPedidos = async () => {
  try {
    loadingPedidos.value = true;

    // Obtener todos los pedidos (no solo los entregados, para poder filtrar en frontend)
    const response = await axios.get("/api/pedidos/", {
      params: {
        fecha_inicio: filtros.value.fechaInicio,
        fecha_fin: filtros.value.fechaFin,
      },
    });

    if (!response.data) {
      throw new Error("No se recibieron datos del servidor para pedidos");
    }

    console.log("Datos de pedidos recibidos:", response.data);

    pedidos.value = response.data.map((item) => ({
      id: item.id,
      cliente: item.cliente?.nombre || "Cliente no disponible",
      total: item.total || 0,
      fecha_entrega: item.fecha_entrega,
      fecha_pedido: item.fecha_pedido,
      detalles: item.detalles || [],
      estado: item.estado || "pendiente",
    }));
  } catch (error) {
    console.error("Error al cargar pedidos:", error);
    pedidos.value = [];
  } finally {
    loadingPedidos.value = false;
  }
};

const fetchProveedores = async () => {
  try {
    const response = await axios.get("/api/proveedores/");
    proveedores.value = response.data;
  } catch (error) {
    console.error("Error al cargar proveedores:", error);
  }
};

// Detectar cambios de tamaño de pantalla
onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
  // Mostrar filtros por defecto en desktop, ocultar en móvil
  mostrarFiltros.value = !isMobile.value;
});

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
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
    fetchReportes(),
    fetchListaCompras(),
    fetchRecetasHechas(),
    fetchPedidos(),
    fetchProveedores(),
  ]).catch((error) => {
    console.error("Error cargando datos:", error);
    if (error.response?.status === 401) {
      router.push("/login");
    }
  });
});

watch(
  () => [filtros.value.fechaInicio, filtros.value.fechaFin],
  ([newFechaInicio, newFechaFin]) => {
    if (newFechaInicio || newFechaFin) {
      fetchRecetasHechas();
    }
  }
);
</script>

<style scoped>
/* -------------------- PESTAÑAS -------------------- */
.tabs-container {
  margin-top: 20px;
  width: 100%;
}

.tabs-header {
  display: flex;
  background: white;
  border-radius: 10px 10px 0 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
}

.tab-button {
  flex: 1;
  min-width: 200px;
  background: #f8f9fa;
  border: none;
  padding: 15px 20px;
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background: #e9ecef;
  color: var(--color-primary);
}

.tab-button.active {
  background: white;
  color: var(--color-primary);
  border-bottom: 3px solid var(--color-primary);
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.05);
}

.tabs-content {
  background: white;
  border-radius: 0 0 10px 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  min-height: 400px;
}

.tab-pane {
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

/* Badge para contador en pestañas - ESPECÍFICO PARA REPORTES */
.tab-button .badge-contador {
  background-color: var(--color-primary);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* -------------------- ESTILOS PARA ESTADÍSTICAS - ESPECÍFICOS REPORTES -------------------- */
.reportes-estadisticas {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  width: 100%;
}

.reportes-estadisticas .reportes-estadistica-badge {
  flex: 1;
  min-width: 200px;
  justify-content: center;
  padding: 12px 16px;
  font-size: 0.9rem;
  border-radius: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

/* Nuevo estilo para el estado de loading en estadísticas */
.reportes-estadistica-badge.loading {
  background: linear-gradient(135deg, #6c757d, #868e96);
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reportes-estadistica-badge.loading i {
  font-size: 0.9rem;
}

.reportes-estadistica-badge.total {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
}

.reportes-estadistica-badge.critico {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  animation: pulse 2s infinite;
}

.reportes-estadistica-badge.normal {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

/* TOGGLE FILTROS CELULAR - ESPECÍFICO PARA REPORTES */
.reportes-filtros-mobile-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: var(--color-primary);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  justify-content: center;
  margin-bottom: 15px;
  width: 100%;
}

.reportes-filtros-derecha {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  width: 100%;
  margin-bottom: 20px;
}

.reportes-btn-agregar {
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px 16px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 44px;
  margin-top: auto;
}

.reportes-btn-agregar:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.reportes-btn-agregar:active {
  transform: translateY(0);
}

/* Ocultar filtros en móvil cuando no están activos */
@media (max-width: 768px) {
  .reportes-filtros-derecha:not(.reportes-filtros-visible) {
    display: none;
  }

  .reportes-filtros-derecha.reportes-filtros-visible {
    display: flex;
  }

  .tabs-header {
    flex-direction: column;
  }

  .tab-button {
    min-width: unset;
    border-radius: 0;
    border-bottom: 1px solid #dee2e6;
  }

  .tab-button.active {
    border-bottom: 3px solid var(--color-primary);
  }
}

/* -------------------- TABLA DE REPORTES - STICKY FUNCIONAL -------------------- */
.reportes-card {
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: var(--color-background);
  border-radius: 10px;
  box-shadow: 10px 8px 10px #aaa;
  padding: 8px;
  padding-top: 2px;
  overflow-y: auto;
}

.reportes-table-header {
  flex-shrink: 0;
  padding: 15px;
  border-bottom: 1px solid #eee;
  background: var(--color-background);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reportes-fecha-info {
  font-size: 0.9rem;
  color: #6c757d;
}

/* CONTENEDOR DE SCROLL PRINCIPAL - CLAVE PARA STICKY */
.reportes-table-scroll-container {
  flex: 1;
  overflow: auto;
  position: relative;
  min-height: 400px; /* Altura mínima */
  max-height: 600px; /* Altura máxima */
  height: auto; /* Se ajusta entre min y max */
}

/* TABLA PRINCIPAL */
.reportes-table-content {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  background: white;
  margin: 0;
  position: relative;
}

/* THEAD STICKY - FUNCIONA PORQUE EL CONTENEDOR TIENE SCROLL */
.reportes-table-content thead {
  position: sticky;
  top: 0;
  z-index: 100;
}

.reportes-table-content th {
  background: linear-gradient(135deg, var(--color-primary), #6d4c41);
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  color: white;
  border-bottom: 2px solid #5a3f36;
  position: sticky;
  top: 0;
  z-index: 101;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.reportes-table-content td {
  padding: 10px 8px;
  border-bottom: 1px solid #eee;
  text-align: left;
  background: white;
}

.reportes-table-content tr:hover td {
  background-color: rgba(123, 90, 80, 0.05);
}

/* Centrar las columnas específicas */
.reportes-table-content th:nth-child(2),
.reportes-table-content th:nth-child(3),
.reportes-table-content th:nth-child(4),
.reportes-table-content th:nth-child(5),
.reportes-table-content td:nth-child(2),
.reportes-table-content td:nth-child(3),
.reportes-table-content td:nth-child(4),
.reportes-table-content td:nth-child(5) {
  text-align: center;
}

/* Filas con stock bajo */
.reportes-fila-stock-bajo td {
  background-color: rgba(220, 53, 69, 0.05);
  border-left: 3px solid var(--color-danger);
}

.reportes-fila-stock-bajo:hover td {
  background-color: rgba(220, 53, 69, 0.1);
}

/* Filas urgentes en lista de compras */
.reportes-fila-urgente td {
  background-color: rgba(40, 167, 69, 0.05);
  border-left: 3px solid var(--color-success);
}

.reportes-fila-urgente:hover td {
  background-color: rgba(40, 167, 69, 0.1);
}

/* Filas urgentes en pedidos */
.reportes-fila-pedido-urgente td {
  background-color: rgba(255, 193, 7, 0.05);
  border-left: 3px solid var(--color-warning);
}

.reportes-fila-pedido-urgente:hover td {
  background-color: rgba(255, 193, 7, 0.1);
}

/* Columnas específicas */
.reportes-columna-insumo-nombre,
.reportes-columna-receta-nombre {
  font-weight: 500;
  color: var(--color-text);
}

.reportes-categoria-insumo {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}

.reportes-columna-stock-usado,
.reportes-columna-stock-actual,
.reportes-columna-stock-minimo,
.reportes-columna-pedidos,
.reportes-columna-cantidad,
.reportes-columna-total {
  font-family: monospace;
  font-weight: 500;
}

.reportes-columna-total-comprar {
  font-family: monospace;
  font-weight: 600;
  color: var(--color-success);
  text-align: center;
}

.reportes-columna-reposicion,
.reportes-columna-estado {
  text-align: center;
}

.reportes-columna-proveedor,
.reportes-columna-empleado,
.reportes-columna-cliente {
  color: #555;
}

.reportes-columna-fecha,
.reportes-columna-hora {
  text-align: center;
}

/* Estilos para los detalles de recetas en reportes */
.recetas-pedido-detalle {
  max-width: 300px;
  line-height: 1.4;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.ingredientes-extra-detalle {
  background: #f8f9fa;
  padding: 6px 8px;
  border-radius: 4px;
  border-left: 3px solid var(--color-primary);
  font-size: 0.75rem;
  color: #666;
  margin-top: 4px;
}

.ingredientes-extra-detalle strong {
  color: var(--color-primary);
}

.reportes-columna-recetas {
  max-width: 350px;
  word-wrap: break-word;
}

/* Ajustar el contenedor de scroll para mejor visualización */
.reportes-table-scroll-container {
  flex: 1;
  overflow: auto;
  position: relative;
  min-height: 400px;
  max-height: 600px;
  height: auto;
}

/* Badges específicos para reportes */
.reportes-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.reportes-badge.alert {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.reportes-badge.success {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.reportes-badge.warning {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

.reportes-badge.info {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.reportes-badge.default {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
}

/* Badges para días de compra */
.reportes-badge-dia {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
  color: white;
}

.reportes-dia-lunes {
  background: linear-gradient(135deg, #007bff, #0056b3);
}

.reportes-dia-martes {
  background: linear-gradient(135deg, #6f42c1, #563d7c);
}

.reportes-dia-jueves {
  background: linear-gradient(135deg, #e83e8c, #d91a72);
}

.reportes-dia-viernes {
  background: linear-gradient(135deg, #fd7e14, #e55a00);
}

.reportes-dia-default {
  background: linear-gradient(135deg, #6c757d, #495057);
}

/* -------------------- BOTÓN PDF -------------------- */
.reportes-btn-generar-pdf {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.reportes-btn-generar-pdf:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
}

.reportes-btn-generar-pdf:active {
  transform: translateY(0);
}

.reportes-estado-generando-pdf {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary);
  font-weight: 500;
}

/* -------------------- LOADING -------------------- */
.reportes-loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-primary);
  width: 100%;
}

.reportes-loading-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

/* -------------------- ESTADO VACÍO -------------------- */
.reportes-empty-state {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 1rem;
  width: 100%;
}

.reportes-empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.reportes-empty-state p {
  margin: 0;
  font-size: 1.1rem;
}

/* -------------------- MEJORAS RESPONSIVE -------------------- */
@media (max-width: 768px) {
  .reportes-estadisticas {
    flex-direction: column;
    gap: 10px;
  }

  .reportes-estadisticas .reportes-estadistica-badge {
    min-width: unset;
  }

  .reportes-filtros-derecha {
    flex-direction: column;
    align-items: stretch;
  }

  .reportes-filtro-group {
    width: 100%;
  }

  .reportes-filtro-input,
  .reportes-filtro-select {
    width: 100%;
  }

  .reportes-seccion-pdf {
    flex-direction: column;
    gap: 10px;
  }

  .reportes-btn-generar-pdf {
    width: 100%;
    justify-content: center;
  }

  /* Ajustes para tabla en móvil */
  .reportes-table-scroll-container {
    max-height: 60vh;
  }

  .reportes-table-content {
    font-size: 0.8rem;
  }

  .reportes-table-content th,
  .reportes-table-content td {
    padding: 8px 4px;
  }

  .reportes-categoria-insumo {
    display: block;
    font-size: 0.7rem;
  }

  .reportes-table-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}

/* Scrollbar personalizado */
.reportes-table-scroll-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.reportes-table-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.reportes-table-scroll-container::-webkit-scrollbar-thumb {
  background: var(--color-primary);
  border-radius: 4px;
}

.reportes-table-scroll-container::-webkit-scrollbar-thumb:hover {
  background: #6d4c41;
}

/* Animación de pulso para alertas */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(220, 53, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
  }
}

/* Título específico para reportes */
.reportes-card-title1 {
  color: var(--color-primary);
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 2px 4px rgba(123, 90, 80, 0.1);
}

/* Filtros específicos para reportes */
.reportes-filtro-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.reportes-filtro-input,
.reportes-filtro-select {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  height: 46px;
  transition: all 0.3s ease;
  background: white;
  min-width: 200px;
}

.reportes-filtro-input:focus,
.reportes-filtro-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(123, 90, 80, 0.1);
  transform: translateY(-1px);
}
</style>
