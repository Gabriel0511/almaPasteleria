<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <div class="reportes-container">
          <!-- Encabezado y Filtros -->
          <div class="principal-content">
            <h1 class="card-title1">📊 Reportes de Insumos</h1>

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

          <!-- Estadísticas de Reporte -->
          <div class="estadisticas-reporte">
            <div class="estadistica-badge total">
              <i class="fas fa-boxes"></i>
              {{ reporteFiltrado.length }} Insumos en reporte
            </div>
            <div class="estadistica-badge critico" v-if="insumosReponer > 0">
              <i class="fas fa-exclamation-triangle"></i>
              {{ insumosReponer }} necesitan reposición
            </div>
            <div class="estadistica-badge normal" v-else>
              <i class="fas fa-check-circle"></i>
              Stock en orden
            </div>
          </div>

          <!-- Tabla de Reportes -->
          <div class="card reporte-table">
            <div class="table-header">
              <h3 class="card-title">Reporte de Insumos</h3>
            </div>
            <div class="table-container">
              <table class="reporte-table-content">
                <thead>
                  <tr>
                    <th>Insumo</th>
                    <th>Stock Usado</th>
                    <th>Stock Actual</th>
                    <th>Stock Mínimo</th>
                    <th>Reponer?</th>
                    <th>Proveedor</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="item in reporteFiltrado"
                    :key="item.id"
                    :class="{ 'low-stock-row': item.necesitaReposicion }"
                  >
                    <td class="insumo-nombre">
                      {{ item.nombre }}
                      <span class="insumo-categoria"
                        >({{ item.categoria }})</span
                      >
                    </td>
                    <td class="stock-usado">
                      {{ formatDecimal(item.stockUsado) }} {{ item.unidad }}
                    </td>
                    <td class="stock-actual">
                      {{ formatDecimal(item.stockActual) }} {{ item.unidad }}
                    </td>
                    <td class="stock-minimo">
                      {{ formatDecimal(item.stockMinimo) }} {{ item.unidad }}
                    </td>
                    <td class="reposicion">
                      <span
                        class="badge"
                        :class="item.necesitaReposicion ? 'alert' : 'success'"
                      >
                        {{ item.necesitaReposicion ? "SÍ" : "NO" }}
                      </span>
                    </td>
                    <td class="proveedor">
                      {{ item.proveedor || "Sin proveedor" }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="loading" class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Cargando reporte...</p>
              </div>
              <div v-else-if="reporteFiltrado.length === 0" class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No hay datos para mostrar con los filtros actuales</p>
              </div>
            </div>
          </div>

          <!-- Botón Generar PDF -->
          <div class="pdf-section">
            <button @click="generarPDF" class="btn-pdf">
              <i class="fas fa-file-pdf"></i>
              Generar Reporte PDF
            </button>

            <div v-if="generandoPDF" class="pdf-loading">
              <i class="fas fa-spinner fa-spin"></i>
              Generando PDF...
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
const proveedores = ref([]);
const loading = ref(true);
const generandoPDF = ref(false);
const mostrarFiltros = ref(false);
const isMobile = ref(false);

// Filtros
const filtros = ref({
  fechaInicio: "",
  fechaFin: "",
  proveedorId: "",
});

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

const insumosReponer = computed(() => {
  return reporteFiltrado.value.filter((item) => item.necesitaReposicion).length;
});

// ----------------------
// 🔹 Métodos
// ----------------------
const aplicarFiltros = () => {
  // Recargar datos con los filtros aplicados
  fetchReportes();
};

const limpiarFiltros = () => {
  filtros.value = {
    fechaInicio: "",
    fechaFin: "",
    proveedorId: "",
  };
  fetchReportes();
};

const formatDecimal = (value) => {
  if (!value) return "0";
  // Eliminar ceros decimales innecesarios
  const num = parseFloat(value);
  return num % 1 === 0 ? num.toString() : num.toFixed(3).replace(/\.?0+$/, "");
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

    // ✅ MEJORAR el fallback
    try {
      const insumosResponse = await axios.get("/api/insumos/");
      if (insumosResponse.data && insumosResponse.data.insumos) {
        reportes.value = insumosResponse.data.insumos.map((item) => ({
          id: item.id,
          nombre: item.nombre,
          categoria: item.categoria?.nombre || "Sin categoría",
          stockUsado: 0, // No disponible sin el endpoint de reportes
          stockActual: item.stock_actual,
          stockMinimo: item.stock_minimo,
          unidad: item.unidad_medida?.abreviatura || "u",
          necesitaReposicion: item.necesita_reposicion,
          proveedor: item.proveedor?.nombre || "Sin proveedor",
          proveedorId: item.proveedor?.id || null,
        }));
      } else {
        reportes.value = [];
      }
    } catch (fallbackError) {
      console.error("Error en fallback:", fallbackError);
      reportes.value = [];
    }
  } finally {
    loading.value = false;
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

// ----------------------
// 🔹 Montaje Inicial
// ----------------------
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  Promise.all([fetchReportes(), fetchProveedores()]).catch((error) => {
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

/* -------------------- ESTILOS PARA ESTADÍSTICAS -------------------- */
.estadisticas-reporte {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.estadisticas-reporte .estadistica-badge {
  flex: 1;
  min-width: 200px;
  justify-content: center;
  padding: 12px 16px;
  font-size: 0.9rem;
}

/* TOGGLE FILTROS CELULAR */
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
}

.filtros-derecha {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

/* Ocultar filtros en móvil cuando no están activos */
@media (max-width: 768px) {
  .filtros-derecha:not(.filtros-visible) {
    display: none;
  }

  .filtros-derecha.filtros-visible {
    display: flex;
  }
}

/* -------------------- TABLA DE REPORTES -------------------- */
.card.reporte-table {
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.table-header {
  flex-shrink: 0;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.table-container {
  flex: 1;
  overflow-y: auto;
}

.reporte-table-content {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.reporte-table-content th {
  background-color: rgba(123, 90, 80, 0.1);
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  color: var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  position: sticky;
  top: 0;
  z-index: 10;
}

.reporte-table-content td {
  padding: 10px 8px;
  border-bottom: 1px solid #eee;
}

.reporte-table-content tr:hover {
  background-color: rgba(123, 90, 80, 0.05);
}

/* Filas con stock bajo */
.low-stock-row {
  background-color: rgba(220, 53, 69, 0.05) !important;
  border-left: 3px solid var(--color-danger);
}

.low-stock-row:hover {
  background-color: rgba(220, 53, 69, 0.1) !important;
}

/* Columnas específicas */
.insumo-nombre {
  font-weight: 500;
  color: var(--color-text);
}

.insumo-categoria {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}

.stock-usado,
.stock-actual,
.stock-minimo {
  text-align: right;
  font-family: monospace;
  font-weight: 500;
}

.reposicion {
  text-align: center;
}

.proveedor {
  color: #555;
}

/* -------------------- BOTÓN PDF -------------------- */
.pdf-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background-color: var(--color-background);
  border-radius: 10px;
  margin-top: 20px;
}

.btn-pdf {
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

.btn-pdf:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
}

.btn-pdf:active {
  transform: translateY(0);
}

.pdf-loading {
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

/* -------------------- MEJORAS PARA TABLA EN MÓVILES -------------------- */
@media (max-width: 768px) {
  .reportes-container {
    padding: 0 5px;
  }

  .principal-content {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
    margin-bottom: 20px;
  }

  .card-title1 {
    font-size: 1.5rem;
    text-align: center;
    width: 100%;
  }

  .filtros-derecha {
    flex-direction: column;
    width: 100%;
    gap: 12px;
  }

  .filtro-group {
    width: 100%;
  }

  .filtro-input,
  .filtro-select {
    min-width: 100%;
    width: 100%;
    font-size: 16px; /* Previene zoom en iOS */
  }

  .btn-agregar {
    width: 100%;
    justify-content: center;
    padding: 12px;
    font-size: 1rem;
    min-height: 44px; /* Tamaño táctil mínimo */
  }

  /* Estadísticas en columna */
  .estadisticas-reporte {
    flex-direction: column;
    gap: 10px;
  }

  .estadisticas-reporte .estadistica-badge {
    min-width: 100%;
    justify-content: flex-start;
  }

  /* Tabla scroll horizontal mejorado */
  .table-container {
    border: 1px solid #eee;
    border-radius: 8px;
    overflow-x: auto;
  }

  .reporte-table-content {
    min-width: 700px; /* Ancho mínimo para mantener legibilidad */
  }

  .reporte-table-content th,
  .reporte-table-content td {
    padding: 12px 8px;
    font-size: 0.85rem;
  }

  /* Mejorar visibilidad de filas en móvil */
  .low-stock-row {
    border-left: 4px solid var(--color-danger);
  }

  /* Sección PDF en columna */
  .pdf-section {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .btn-pdf {
    width: 100%;
    justify-content: center;
  }
}

/* -------------------- MEJORAS PARA TABLETS -------------------- */
@media (max-width: 1024px) and (min-width: 769px) {
  .filtros-derecha {
    flex-wrap: wrap;
    justify-content: flex-start;
  }

  .filtro-group {
    min-width: 180px;
  }

  .estadisticas-reporte {
    gap: 12px;
  }

  .estadisticas-reporte .estadistica-badge {
    min-width: 180px;
    flex: 0 1 calc(50% - 12px);
  }
}

/* -------------------- MEJORAS PARA PANTALLAS MUY PEQUEÑAS -------------------- */
@media (max-width: 480px) {
  .reportes-container {
    padding: 0;
  }

  .card.reporte-table {
    margin-left: 5px;
    margin-right: 5px;
  }

  .card-title1 {
    font-size: 1.3rem;
  }

  .estadistica-badge {
    font-size: 0.75rem;
    padding: 10px 12px;
  }

  .empty-state {
    padding: 2rem 1rem;
  }

  .empty-state i {
    font-size: 2.5rem;
  }

  .reporte-table-content {
    min-width: 650px;
  }

  .insumo-categoria {
    display: block;
    margin-top: 2px;
  }
}

/* -------------------- MEJORAS ESPECÍFICAS PARA TOUCH -------------------- */
@media (hover: none) and (pointer: coarse) {
  .btn-agregar,
  .btn-pdf {
    min-height: 44px;
    padding: 12px 16px;
  }

  .filtro-input,
  .filtro-select {
    min-height: 44px;
    font-size: 16px; /* Previene zoom automático en iOS */
  }

  .reporte-table-content tr {
    min-height: 44px;
  }

  /* Aumentar área táctil para filas de tabla */
  .reporte-table-content td {
    padding-top: 14px;
    padding-bottom: 14px;
  }
}

/* -------------------- MEJORAS DE ACCESIBILIDAD -------------------- */
@media (prefers-reduced-motion: reduce) {
  .btn-agregar,
  .btn-pdf {
    transition: none;
  }

  .estadistica-badge.critico {
    animation: none;
  }
}

/* -------------------- ORIENTACIÓN HORIZONTAL EN MÓVILES -------------------- */
@media (max-height: 500px) and (orientation: landscape) {
  .card.reporte-table {
    max-height: 50vh;
  }

  .estadisticas-reporte {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .estadisticas-reporte .estadistica-badge {
    min-width: auto;
    flex: 1;
  }
}

/* -------------------- MEJORAS PARA MODO OSCURO (si se implementa) -------------------- */
@media (prefers-color-scheme: dark) {
  /* Estas reglas se activarían si implementas modo oscuro */
  .reporte-table-content th {
    background-color: rgba(123, 90, 80, 0.2);
  }

  .low-stock-row {
    background-color: rgba(220, 53, 69, 0.1) !important;
  }
}
</style>
