<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <div class="reportes-container">
          <!-- Encabezado y Filtros -->
          <div class="principal-content">
            <h1 class="card-title1">Reportes de Insumos</h1>

            <div
              class="filtros-mobile-toggle"
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
              class="filtros-derecha"
              :class="{ 'filtros-visible': mostrarFiltros }"
            >
              <div class="filtro-group">
                <label for="fecha-inicio">Fecha Inicio</label>
                <input
                  id="fecha-inicio"
                  type="date"
                  v-model="filtros.fechaInicio"
                  class="filtro-input"
                />
              </div>

              <div class="filtro-group">
                <label for="fecha-fin">Fecha Fin</label>
                <input
                  id="fecha-fin"
                  type="date"
                  v-model="filtros.fechaFin"
                  class="filtro-input"
                />
              </div>

              <div class="filtro-group">
                <label for="proveedor">Proveedor</label>
                <select
                  id="proveedor"
                  v-model="filtros.proveedorId"
                  class="filtro-select"
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

              <button @click="aplicarFiltros" class="btn-agregar">
                <i class="fas fa-filter"></i>
                Aplicar
              </button>

              <button
                @click="limpiarFiltros"
                class="btn-agregar"
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
                <div class="card reporte-table">
                  <div class="table-header-reportes">
                    <h3 class="card-title">Reporte de Insumos</h3>
                  </div>
                  <div class="table-scroll-container">
                    <table class="reporte-table-content">
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
                            'fila-stock-bajo': item.necesitaReposicion,
                          }"
                        >
                          <td class="columna-insumo-nombre">
                            {{ item.nombre }}
                            <span class="categoria-insumo"
                              >({{ item.categoria }})</span
                            >
                          </td>
                          <td class="columna-stock-usado">
                            {{ formatDecimal(item.stockUsado) }}
                            {{ item.unidad }}
                          </td>
                          <td class="columna-stock-actual">
                            {{ formatDecimal(item.stockActual) }}
                            {{ item.unidad }}
                          </td>
                          <td class="columna-stock-minimo">
                            {{ formatDecimal(item.stockMinimo) }}
                            {{ item.unidad }}
                          </td>
                          <td class="columna-reposicion">
                            <span
                              class="badge"
                              :class="
                                item.necesitaReposicion ? 'alert' : 'success'
                              "
                            >
                              {{ item.necesitaReposicion ? "SÍ" : "NO" }}
                            </span>
                          </td>
                          <td class="columna-proveedor">
                            {{ item.proveedor || "Sin proveedor" }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loading" class="loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando reporte...</p>
                    </div>
                    <div
                      v-else-if="reporteFiltrado.length === 0"
                      class="empty-state"
                    >
                      <i class="fas fa-inbox"></i>
                      <p>No hay datos para mostrar con los filtros actuales</p>
                    </div>
                  </div>
                </div>

                <!-- Botón Generar PDF para reportes -->
                <div class="seccion-pdf" v-if="reporteFiltrado.length > 0">
                  <button @click="generarPDF" class="btn-generar-pdf">
                    <i class="fas fa-file-pdf"></i>
                    Generar Reporte PDF
                  </button>

                  <div v-if="generandoPDF" class="estado-generando-pdf">
                    <i class="fas fa-spinner fa-spin"></i>
                    Generando PDF...
                  </div>
                </div>
              </div>

              <!-- Pestaña 2: Lista de Compras -->
              <div v-show="tabActiva === 'lista-compras'" class="tab-pane">
                <!-- Tabla de Lista de Compras -->
                <div class="card reporte-table">
                  <div class="table-header-reportes">
                    <h3 class="card-title">
                      📋 Lista de Compras - Próxima Semana
                    </h3>
                  </div>
                  <div class="table-scroll-container">
                    <table class="reporte-table-content">
                      <thead>
                        <tr>
                          <th>Insumo</th>
                          <th>Stock Actual</th>
                          <th>Stock Mínimo</th>
                          <th>Pedidos</th>
                          <th>Total a Comprar</th>
                          <th>Proveedor</th>
                          <th>Día Compra</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in listaComprasFiltrada"
                          :key="'compra-' + item.id"
                          :class="{ 'fila-urgente': item.totalComprar > 0 }"
                        >
                          <td class="columna-insumo-nombre">
                            {{ item.nombre }}
                            <span class="categoria-insumo"
                              >({{ item.categoria }})</span
                            >
                          </td>
                          <td class="columna-stock-actual">
                            {{ formatDecimal(item.stockActual) }}
                            {{ item.unidad }}
                          </td>
                          <td class="columna-stock-minimo">
                            {{ formatDecimal(item.stockMinimo) }}
                            {{ item.unidad }}
                          </td>
                          <td class="columna-pedidos">
                            {{ formatDecimal(item.pedidos) }} {{ item.unidad }}
                          </td>
                          <td class="columna-total-comprar">
                            <strong
                              >{{ formatDecimal(item.totalComprar) }}
                              {{ item.unidad }}</strong
                            >
                          </td>
                          <td class="columna-proveedor">
                            {{ item.proveedor || "Sin proveedor" }}
                          </td>
                          <td class="columna-dia-compra">
                            <span
                              class="badge-dia"
                              :class="getClaseDiaCompra(item.diaCompra)"
                            >
                              {{ item.diaCompra }}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingListaCompras" class="loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando lista de compras...</p>
                    </div>
                    <div
                      v-else-if="listaComprasFiltrada.length === 0"
                      class="empty-state"
                    >
                      <i class="fas fa-check-circle"></i>
                      <p>
                        No hay insumos para comprar con los filtros actuales
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Botón Generar PDF para lista de compras -->
                <div class="seccion-pdf" v-if="listaComprasFiltrada.length > 0">
                  <button
                    @click="generarPDFListaCompras"
                    class="btn-generar-pdf"
                    style="
                      background: linear-gradient(135deg, #28a745, #20c997);
                    "
                  >
                    <i class="fas fa-file-pdf"></i>
                    Generar Lista de Compras PDF
                  </button>

                  <div
                    v-if="generandoPDFListaCompras"
                    class="estado-generando-pdf"
                  >
                    <i class="fas fa-spinner fa-spin"></i>
                    Generando PDF...
                  </div>
                </div>
              </div>

              <!-- Pestaña 3: Recetas Hechas -->
              <div v-show="tabActiva === 'recetas-hechas'" class="tab-pane">
                <!-- Tabla de Recetas Hechas -->
                <div class="card reporte-table">
                  <div class="table-header-reportes">
                    <h3 class="card-title">🍽️ Recetas Hechas</h3>
                    <div class="fecha-info">
                      <span
                        >Mostrando recetas del: {{ fechaRecetasTexto }}</span
                      >
                    </div>
                  </div>
                  <div class="table-scroll-container">
                    <table class="reporte-table-content">
                      <thead>
                        <tr>
                          <th>Receta</th>
                          <th>Cantidad</th>
                          <th>Fecha</th>
                          <th>Hora</th>
                          <th>Estado</th>
                          <th>Empleado</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in recetasHechasFiltradas"
                          :key="'receta-' + item.id"
                        >
                          <td class="columna-receta-nombre">
                            {{ item.nombre }}
                          </td>
                          <td class="columna-cantidad">
                            {{ item.cantidad }}
                          </td>
                          <td class="columna-fecha">
                            {{ formatearFecha(item.fecha) }}
                          </td>
                          <td class="columna-hora">
                            {{ item.hora }}
                          </td>
                          <td class="columna-estado">
                            <span
                              class="badge"
                              :class="getClaseEstadoReceta(item.estado)"
                            >
                              {{ item.estado }}
                            </span>
                          </td>
                          <td class="columna-empleado">
                            {{ item.empleado || "No asignado" }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingRecetas" class="loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando recetas...</p>
                    </div>
                    <div
                      v-else-if="recetasHechasFiltradas.length === 0"
                      class="empty-state"
                    >
                      <i class="fas fa-utensils"></i>
                      <p>No hay recetas para la fecha seleccionada</p>
                    </div>
                  </div>
                </div>

                <!-- Botón Generar PDF para recetas hechas -->
                <div
                  class="seccion-pdf"
                  v-if="recetasHechasFiltradas.length > 0"
                >
                  <button
                    @click="generarPDFRecetas"
                    class="btn-generar-pdf"
                    style="
                      background: linear-gradient(135deg, #007bff, #0056b3);
                    "
                  >
                    <i class="fas fa-file-pdf"></i>
                    Generar Reporte de Recetas PDF
                  </button>

                  <div v-if="generandoPDFRecetas" class="estado-generando-pdf">
                    <i class="fas fa-spinner fa-spin"></i>
                    Generando PDF...
                  </div>
                </div>
              </div>

              <!-- Pestaña 4: Pedidos -->
              <div v-show="tabActiva === 'pedidos'" class="tab-pane">
                <!-- Tabla de Pedidos -->
                <div class="card reporte-table">
                  <div class="table-header-reportes">
                    <h3 class="card-title">📦 Pedidos</h3>
                    <div class="fecha-info">
                      <span
                        >Mostrando pedidos del: {{ fechaPedidosTexto }}</span
                      >
                    </div>
                  </div>
                  <div class="table-scroll-container">
                    <table class="reporte-table-content">
                      <thead>
                        <tr>
                          <th>Pedido ID</th>
                          <th>Cliente</th>
                          <th>Total</th>
                          <th>Fecha</th>
                          <th>Estado</th>
                          <th>Método Pago</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in pedidosFiltrados"
                          :key="'pedido-' + item.id"
                          :class="{
                            'fila-pedido-urgente': item.estado === 'Pendiente',
                          }"
                        >
                          <td class="columna-pedido-id">#{{ item.id }}</td>
                          <td class="columna-cliente">
                            {{ item.cliente }}
                          </td>
                          <td class="columna-total">
                            ${{ formatDecimal(item.total) }}
                          </td>
                          <td class="columna-fecha">
                            {{ formatearFecha(item.fecha) }}
                          </td>
                          <td class="columna-estado">
                            <span
                              class="badge"
                              :class="getClaseEstadoPedido(item.estado)"
                            >
                              {{ item.estado }}
                            </span>
                          </td>
                          <td class="columna-metodo-pago">
                            {{ item.metodoPago }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingPedidos" class="loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando pedidos...</p>
                    </div>
                    <div
                      v-else-if="pedidosFiltrados.length === 0"
                      class="empty-state"
                    >
                      <i class="fas fa-shopping-bag"></i>
                      <p>No hay pedidos para la fecha seleccionada</p>
                    </div>
                  </div>
                </div>

                <!-- Botón Generar PDF para pedidos -->
                <div class="seccion-pdf" v-if="pedidosFiltrados.length > 0">
                  <button
                    @click="generarPDFPedidos"
                    class="btn-generar-pdf"
                    style="
                      background: linear-gradient(135deg, #6f42c1, #563d7c);
                    "
                  >
                    <i class="fas fa-file-pdf"></i>
                    Generar Reporte de Pedidos PDF
                  </button>

                  <div v-if="generandoPDFPedidos" class="estado-generando-pdf">
                    <i class="fas fa-spinner fa-spin"></i>
                    Generando PDF...
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
import { ref, computed, onMounted } from "vue";
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

// Filtros
const filtros = ref({
  fechaInicio: "",
  fechaFin: "",
  proveedorId: "",
});

// Fechas para recetas y pedidos (por defecto hoy)
const fechaRecetas = ref(new Date().toISOString().split("T")[0]);
const fechaPedidos = ref(new Date().toISOString().split("T")[0]);

// ----------------------
// 🔹 Computed Properties
// ----------------------
const reporteFiltrado = computed(() => {
  let filtered = [...reportes.value];

  // Filtrar por proveedor
  if (filtros.value.proveedorId) {
    filtered = filtered.filter(
      (item) => item.proveedorId === parseInt(filtros.value.proveedorId)
    );
  }

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
  return recetasHechas.value.filter(
    (receta) => receta.fecha === fechaRecetas.value
  );
});

const pedidosFiltrados = computed(() => {
  return pedidos.value.filter((pedido) => pedido.fecha === fechaPedidos.value);
});

const fechaRecetasTexto = computed(() => {
  return formatearFecha(fechaRecetas.value);
});

const fechaPedidosTexto = computed(() => {
  return formatearFecha(fechaPedidos.value);
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
  fechaRecetas.value = new Date().toISOString().split("T")[0];
  fechaPedidos.value = new Date().toISOString().split("T")[0];

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
  const opciones = { year: "numeric", month: "long", day: "numeric" };
  return new Date(fecha).toLocaleDateString("es-ES", opciones);
};

const getClaseDiaCompra = (dia) => {
  const clasesDias = {
    Lunes: "dia-lunes",
    Martes: "dia-martes",
    Jueves: "dia-jueves",
    Viernes: "dia-viernes",
  };
  return clasesDias[dia] || "dia-default";
};

const getClaseEstadoReceta = (estado) => {
  const clasesEstados = {
    Completado: "success",
    "En proceso": "warning",
    Cancelado: "alert",
  };
  return clasesEstados[estado] || "default";
};

const getClaseEstadoPedido = (estado) => {
  const clasesEstados = {
    Completado: "success",
    Pendiente: "warning",
    Cancelado: "alert",
    "En camino": "info",
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

    // Hacer la petición para generar el PDF de recetas
    const response = await axios.get("/api/reportes/generar-pdf-recetas/", {
      params: { fecha: fechaRecetas.value },
      responseType: "blob",
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `recetas_${fechaRecetas.value}.pdf`);
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

    // Hacer la petición para generar el PDF de pedidos
    const response = await axios.get("/api/reportes/generar-pdf-pedidos/", {
      params: { fecha: fechaPedidos.value },
      responseType: "blob",
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `pedidos_${fechaPedidos.value}.pdf`);
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

    const response = await axios.get("/api/reportes/recetas-hechas/", {
      params: { fecha: fechaRecetas.value },
    });

    if (!response.data) {
      throw new Error(
        "No se recibieron datos del servidor para recetas hechas"
      );
    }

    recetasHechas.value = response.data.map((item) => ({
      id: item.id,
      nombre: item.nombre,
      cantidad: item.cantidad,
      fecha: item.fecha,
      hora: item.hora,
      estado: item.estado,
      empleado: item.empleado || "No asignado",
    }));
  } catch (error) {
    console.error("Error al cargar recetas hechas:", error);
    recetasHechas.value = [];
  } finally {
    loadingRecetas.value = false;
  }
};

const fetchPedidos = async () => {
  try {
    loadingPedidos.value = true;

    const response = await axios.get("/api/reportes/pedidos/", {
      params: { fecha: fechaPedidos.value },
    });

    if (!response.data) {
      throw new Error("No se recibieron datos del servidor para pedidos");
    }

    pedidos.value = response.data.map((item) => ({
      id: item.id,
      cliente: item.cliente,
      total: item.total,
      fecha: item.fecha,
      estado: item.estado,
      metodoPago: item.metodo_pago,
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
</script>

<style scoped>
/* ==================== ESTILOS ESPECÍFICOS PARA REPORTES.VUE ==================== */

.reportes-container {
  padding: 0 10px;
}

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

/* Badge para contador en pestañas */
.tab-button .badge-contador {
  background-color: var(--color-primary);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* -------------------- ESTILOS PARA ESTADÍSTICAS -------------------- */
.estadisticas-reporte {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  width: 100%;
}

.estadisticas-reporte .estadistica-badge {
  flex: 1;
  min-width: 200px;
  justify-content: center;
  padding: 12px 16px;
  font-size: 0.9rem;
}

/* Nuevo estilo para el estado de loading en estadísticas */
.estadistica-badge.loading {
  background: linear-gradient(135deg, #6c757d, #868e96);
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.estadistica-badge.loading i {
  font-size: 0.9rem;
}

.estadistica-badge.total {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
}

.estadistica-badge.critico {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  animation: pulse 2s infinite;
}

.estadistica-badge.normal {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

/* TOGGLE FILTROS CELULAR - mantener nombres existentes */
.filtros-mobile-toggle {
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

.filtros-derecha {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  width: 100%;
}

.btn-agregar {
  margin-top: auto;
  height: 44px;
}

/* Ocultar filtros en móvil cuando no están activos */
@media (max-width: 768px) {
  .filtros-derecha:not(.filtros-visible) {
    display: none;
  }

  .filtros-derecha.filtros-visible {
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
.card.reporte-table {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.table-header-reportes {
  flex-shrink: 0;
  padding: 15px;
  border-bottom: 1px solid #eee;
  background: var(--color-background);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fecha-info {
  font-size: 0.9rem;
  color: #6c757d;
}

/* CONTENEDOR DE SCROLL PRINCIPAL - CLAVE PARA STICKY */
.table-scroll-container {
  flex: 1;
  overflow: auto;
  position: relative;
  max-height: calc(70vh - 60px); /* Altura del contenedor menos el header */
}

/* TABLA PRINCIPAL */
.reporte-table-content {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  background: white;
  margin: 0;
  position: relative;
}

/* THEAD STICKY - FUNCIONA PORQUE EL CONTENEDOR TIENE SCROLL */
.reporte-table-content thead {
  position: sticky;
  top: 0;
  z-index: 100;
}

.reporte-table-content th {
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

.reporte-table-content td {
  padding: 10px 8px;
  border-bottom: 1px solid #eee;
  text-align: left;
  background: white;
}

.reporte-table-content tr:hover td {
  background-color: rgba(123, 90, 80, 0.05);
}

/* Centrar las columnas específicas */
.reporte-table-content th:nth-child(2),
.reporte-table-content th:nth-child(3),
.reporte-table-content th:nth-child(4),
.reporte-table-content th:nth-child(5),
.reporte-table-content td:nth-child(2),
.reporte-table-content td:nth-child(3),
.reporte-table-content td:nth-child(4),
.reporte-table-content td:nth-child(5) {
  text-align: center;
}

/* Filas con stock bajo */
.fila-stock-bajo td {
  background-color: rgba(220, 53, 69, 0.05);
  border-left: 3px solid var(--color-danger);
}

.fila-stock-bajo:hover td {
  background-color: rgba(220, 53, 69, 0.1);
}

/* Filas urgentes en lista de compras */
.fila-urgente td {
  background-color: rgba(40, 167, 69, 0.05);
  border-left: 3px solid var(--color-success);
}

.fila-urgente:hover td {
  background-color: rgba(40, 167, 69, 0.1);
}

/* Filas urgentes en pedidos */
.fila-pedido-urgente td {
  background-color: rgba(255, 193, 7, 0.05);
  border-left: 3px solid var(--color-warning);
}

.fila-pedido-urgente:hover td {
  background-color: rgba(255, 193, 7, 0.1);
}

/* Columnas específicas */
.columna-insumo-nombre,
.columna-receta-nombre {
  font-weight: 500;
  color: var(--color-text);
}

.categoria-insumo {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}

.columna-stock-usado,
.columna-stock-actual,
.columna-stock-minimo,
.columna-pedidos,
.columna-cantidad,
.columna-total {
  font-family: monospace;
  font-weight: 500;
}

.columna-total-comprar {
  font-family: monospace;
  font-weight: 600;
  color: var(--color-success);
  text-align: center;
}

.columna-reposicion,
.columna-estado {
  text-align: center;
}

.columna-proveedor,
.columna-empleado,
.columna-cliente,
.columna-metodo-pago {
  color: #555;
}

.columna-dia-compra,
.columna-fecha,
.columna-hora {
  text-align: center;
}

.columna-pedido-id {
  font-weight: 600;
  color: var(--color-primary);
}

/* Badges específicos para reportes */
.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.badge.alert {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.badge.success {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.badge.warning {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

.badge.info {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.badge.default {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
}

/* Badges para días de compra */
.badge-dia {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
  color: white;
}

.dia-lunes {
  background: linear-gradient(135deg, #007bff, #0056b3);
}

.dia-martes {
  background: linear-gradient(135deg, #6f42c1, #563d7c);
}

.dia-jueves {
  background: linear-gradient(135deg, #e83e8c, #d91a72);
}

.dia-viernes {
  background: linear-gradient(135deg, #fd7e14, #e55a00);
}

.dia-default {
  background: linear-gradient(135deg, #6c757d, #495057);
}

/* -------------------- BOTÓN PDF -------------------- */
.seccion-pdf {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background-color: var(--color-background);
  border-radius: 10px;
  margin-top: 20px;
  width: 100%;
}

.btn-generar-pdf {
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

.btn-generar-pdf:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
}

.btn-generar-pdf:active {
  transform: translateY(0);
}

.estado-generando-pdf {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary);
  font-weight: 500;
}

/* -------------------- LOADING -------------------- */
.loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-primary);
  width: 100%;
}

.loading-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

/* -------------------- ESTADO VACÍO -------------------- */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 1rem;
  width: 100%;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 1.1rem;
}

/* -------------------- MEJORAS RESPONSIVE -------------------- */
@media (max-width: 768px) {
  .estadisticas-reporte {
    flex-direction: column;
    gap: 10px;
  }

  .estadisticas-reporte .estadistica-badge {
    min-width: unset;
  }

  .filtros-derecha {
    flex-direction: column;
    align-items: stretch;
  }

  .filtro-group {
    width: 100%;
  }

  .filtro-input,
  .filtro-select {
    width: 100%;
  }

  .seccion-pdf {
    flex-direction: column;
    gap: 10px;
  }

  .btn-generar-pdf {
    width: 100%;
    justify-content: center;
  }

  /* Ajustes para tabla en móvil */
  .table-scroll-container {
    max-height: 60vh;
  }

  .reporte-table-content {
    font-size: 0.8rem;
  }

  .reporte-table-content th,
  .reporte-table-content td {
    padding: 8px 4px;
  }

  .categoria-insumo {
    display: block;
    font-size: 0.7rem;
  }

  .table-header-reportes {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}

/* Scrollbar personalizado */
.table-scroll-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-scroll-container::-webkit-scrollbar-thumb {
  background: var(--color-primary);
  border-radius: 4px;
}

.table-scroll-container::-webkit-scrollbar-thumb:hover {
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
</style>
