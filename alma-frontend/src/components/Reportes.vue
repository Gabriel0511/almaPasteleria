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

            <div class="filtros-mobile-toggle" v-if="isMobile" @click="mostrarFiltros = !mostrarFiltros">
              <i class="fas" :class="mostrarFiltros ? 'fa-chevron-up' : 'fa-filter'"></i>
              {{ mostrarFiltros ? "Ocultar Filtros" : "Mostrar Filtros" }}
            </div>

            <div class="filtros-derecha" :class="{ 'filtros-visible': mostrarFiltros }">
              <div class="filtro-group">
                <label for="fecha-inicio">Fecha Inicio</label>
                <input id="fecha-inicio" type="date" v-model="filtros.fechaInicio" class="filtro-input" />
              </div>

              <div class="filtro-group">
                <label for="fecha-fin">Fecha Fin</label>
                <input id="fecha-fin" type="date" v-model="filtros.fechaFin" class="filtro-input" />
              </div>

              <div class="filtro-group">
                <label for="proveedor">Proveedor</label>
                <select id="proveedor" v-model="filtros.proveedorId" class="filtro-select">
                  <option value="">Todos los proveedores</option>
                  <option v-for="proveedor in proveedores" :key="proveedor.id" :value="proveedor.id">
                    {{ proveedor.nombre }}
                  </option>
                </select>
              </div>

              <button @click="aplicarFiltros" class="btn-agregar">
                <i class="fas fa-filter"></i>
                Aplicar
              </button>

              <button @click="limpiarFiltros" class="btn-agregar" style="background-color: #6c757d">
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

            <!-- Estado de carga para stock -->
            <div v-if="loading" class="estadistica-badge loading">
              <i class="fas fa-spinner fa-spin"></i>
              Cargando estado de stock...
            </div>

            <!-- CORRECCIÓN: Mostrar estado crítico si hay insumos que reponer -->
            <div v-else-if="insumosReponer > 0" class="estadistica-badge critico">
              <i class="fas fa-exclamation-triangle"></i>
              {{ insumosReponer }} necesitan reposición
            </div>

            <!-- CORRECCIÓN: Mostrar estado normal solo si NO hay insumos que reponer -->
            <div v-else class="estadistica-badge normal">
              <i class="fas fa-check-circle"></i>
              Stock en orden
            </div>
          </div>

          <!-- Botón para desplegar/ocultar la tabla -->
          <div class="tabla-toggle-section">
            <button @click="toggleTabla" class="btn-desplegar-tabla" :class="{ 'activo': tablaVisible }">
              <i class="fas" :class="tablaVisible ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              {{ tablaVisible ? 'Ocultar Tabla de Reportes' : 'Mostrar Tabla de Reportes' }}
              <span class="badge-contador">
                {{ reporteFiltrado.length }}
              </span>
            </button>
          </div>

          <!-- Tabla de Reportes (ahora colapsable) -->
          <div class="card reporte-table tabla-reportes-colapsable" :class="{ 'visible': tablaVisible }">
            <div class="table-header-reportes">
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
                  <tr v-for="item in reporteFiltrado" :key="item.id"
                    :class="{ 'fila-stock-bajo': item.necesitaReposicion }">
                    <td class="columna-insumo-nombre">
                      {{ item.nombre }}
                      <span class="categoria-insumo">({{ item.categoria }})</span>
                    </td>
                    <td class="columna-stock-usado">
                      {{ formatDecimal(item.stockUsado) }} {{ item.unidad }}
                    </td>
                    <td class="columna-stock-actual">
                      {{ formatDecimal(item.stockActual) }} {{ item.unidad }}
                    </td>
                    <td class="columna-stock-minimo">
                      {{ formatDecimal(item.stockMinimo) }} {{ item.unidad }}
                    </td>
                    <td class="columna-reposicion">
                      <span class="badge" :class="item.necesitaReposicion ? 'alert' : 'success'">
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
              <div v-else-if="reporteFiltrado.length === 0" class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No hay datos para mostrar con los filtros actuales</p>
              </div>
            </div>
          </div>

          <!-- Botón Generar PDF -->
          <div class="seccion-pdf" v-if="tablaVisible && reporteFiltrado.length > 0">
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

// Estado para controlar visibilidad de la tabla
const tablaVisible = ref(false);

// Método para alternar el sidebar desde el header
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};

// Método para alternar visibilidad de la tabla
const toggleTabla = () => {
  tablaVisible.value = !tablaVisible.value;
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

/* -------------------- BOTÓN TOGGLE TABLA - ANCHO COMPLETO -------------------- */
.tabla-toggle-section {
  margin: 20px 0;
  display: flex;
  justify-content: center;
  width: 100%;
}

.btn-desplegar-tabla {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 15px 25px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(123, 90, 80, 0.3);
  width: 100%;
  justify-content: center;
  position: relative;
}

.btn-desplegar-tabla:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(123, 90, 80, 0.4);
  background: linear-gradient(135deg, #6d4c41, var(--color-primary));
}

.btn-desplegar-tabla.activo {
  background: linear-gradient(135deg, #5a3f36, var(--color-primary));
}

.btn-desplegar-tabla:active {
  transform: translateY(0);
}

/* Badge específico para el botón de toggle */
.badge-contador {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: absolute;
  right: 20px;
}

/* -------------------- TABLA COLAPSABLE -------------------- */
.tabla-reportes-colapsable {
  max-height: 0;
  overflow: hidden;
  transition: all 0.4s ease;
  margin-bottom: 0;
  opacity: 0;
  width: 100%;
}

.tabla-reportes-colapsable.visible {
  max-height: 80vh;
  opacity: 1;
  margin-bottom: 20px;
}

/* Asegurar que la tabla ocupe espacio cuando está visible */
.card.reporte-table.tabla-reportes-colapsable.visible {
  display: flex;
  flex-direction: column;
  width: 100%;
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
  display: flex;
  flex-direction: column;
  width: 100%;
}

.table-header-reportes {
  flex-shrink: 0;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.table-container-reportes {
  flex: 1;
  overflow-y: auto;
  width: 100%;
}

.tabla-reportes {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.tabla-reportes th {
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

.tabla-reportes td {
  padding: 10px 8px;
  border-bottom: 1px solid #eee;
}

.tabla-reportes tr:hover {
  background-color: rgba(123, 90, 80, 0.05);
}

/* Centrar las columnas específicas */
.tabla-reportes th:nth-child(2),
.tabla-reportes th:nth-child(3),
.tabla-reportes th:nth-child(4),
.tabla-reportes th:nth-child(5),
.tabla-reportes td:nth-child(2),
.tabla-reportes td:nth-child(3),
.tabla-reportes td:nth-child(4),
.tabla-reportes td:nth-child(5) {
  text-align: center;
}

/* Filas con stock bajo */
.fila-stock-bajo {
  background-color: rgba(220, 53, 69, 0.05) !important;
  border-left: 3px solid var(--color-danger);
}

.fila-stock-bajo:hover {
  background-color: rgba(220, 53, 69, 0.1) !important;
}

/* Columnas específicas */
.columna-insumo-nombre {
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
.columna-stock-minimo {
  font-family: monospace;
  font-weight: 500;
}

.columna-reposicion {
  text-align: center;
}

.columna-proveedor {
  color: #555;
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
.estado-cargando {
  text-align: center;
  padding: 3rem;
  color: var(--color-primary);
}

.estado-cargando i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

/* -------------------- ESTADO VACÍO -------------------- */
.estado-vacio {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 1rem;
}

.estado-vacio i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.estado-vacio p {
  margin: 0;
  font-size: 1.1rem;
}

/* -------------------- MEJORAS RESPONSIVE -------------------- */
@media (max-width: 768px) {
  .btn-desplegar-tabla {
    padding: 12px 20px;
    font-size: 1rem;
  }

  .tabla-toggle-section {
    margin: 15px 0;
    padding: 0 5px;
  }

  .badge-contador {
    right: 15px;
  }

  .estadisticas-reporte {
    flex-direction: column;
    gap: 10px;
  }

  .estadisticas-reporte .estadistica-badge {
    min-width: 100%;
  }

  .filtros-derecha {
    flex-direction: column;
    width: 100%;
  }

  .filtro-group {
    width: 100%;
  }

  .filtro-input,
  .filtro-select {
    min-width: 100%;
    width: 100%;
    font-size: 16px;
  }

  .tabla-reportes {
    min-width: 700px;
  }

  .tabla-reportes th,
  .tabla-reportes td {
    padding: 12px 8px;
    font-size: 0.85rem;
  }

  .seccion-pdf {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .btn-generar-pdf {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .btn-desplegar-tabla {
    padding: 14px 16px;
    font-size: 0.95rem;
  }

  .badge-contador {
    right: 12px;
    font-size: 11px;
  }

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

  .estado-vacio {
    padding: 2rem 1rem;
  }

  .estado-vacio i {
    font-size: 2.5rem;
  }

  .tabla-reportes {
    min-width: 650px;
  }

  .categoria-insumo {
    display: block;
    margin-top: 2px;
  }
}

/* Para pantallas muy grandes, limitar el ancho máximo si es necesario */
@media (min-width: 1200px) {
  .btn-desplegar-tabla {
    max-width: 1200px;
  }
}

/* -------------------- MEJORAS ESPECÍFICAS PARA TOUCH -------------------- */
@media (hover: none) and (pointer: coarse) {

  .btn-desplegar-tabla,
  .btn-generar-pdf {
    min-height: 44px;
    padding: 12px 16px;
  }

  .filtro-input,
  .filtro-select {
    min-height: 44px;
    font-size: 16px;
  }

  .tabla-reportes tr {
    min-height: 44px;
  }

  .tabla-reportes td {
    padding-top: 14px;
    padding-bottom: 14px;
  }
}

/* -------------------- MEJORAS DE ACCESIBILIDAD -------------------- */
@media (prefers-reduced-motion: reduce) {

  .btn-desplegar-tabla,
  .btn-generar-pdf {
    transition: none;
  }

  .estadistica-badge.critico {
    animation: none;
  }

  .estadistica-badge.loading i {
    animation: none;
  }
}

/* -------------------- ORIENTACIÓN HORIZONTAL EN MÓVILES -------------------- */
@media (max-height: 500px) and (orientation: landscape) {
  .card.reporte-table.tabla-reportes-colapsable.visible {
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

/* Animación de pulso para el badge crítico */
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