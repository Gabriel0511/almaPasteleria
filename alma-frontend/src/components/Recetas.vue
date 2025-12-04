<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <PageHeader
          title="Gestión de Recetas"
          :stats="recetasStats"
          :filters="recetasFilters"
          :active-filter-type="filtroActivo"
          @stat-click="handleStatClick"
          @filter-change="handleFilterChange"
          @clear-filters="limpiarFiltros"
        />

        <!-- Card principal de recetas - ESTILO COMO STOCK -->
        <div class="card recetas-card">
          <div v-if="loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i> Cargando recetas...
          </div>

          <div v-else-if="recetasFiltradas.length === 0" class="empty-state">
            <i class="fas fa-search"></i>
            <p>No hay recetas que coincidan con los filtros seleccionados</p>
          </div>

          <div v-else class="recetas-list">
            <div
              v-for="receta in recetasPaginadas"
              :key="receta.id"
              class="receta-item"
              :class="{
                'no-rentable': receta.precio_venta <= receta.costo_total,
                expanded: recetaDesplegada[receta.id],
              }"
            >
              <!-- Contenedor principal compacto - ESTILO COMO STOCK -->
              <div class="receta-item-compact">
                <!-- Indicador de estado -->
                <div
                  class="estado-indicador"
                  :class="{
                    critico: receta.precio_venta <= receta.costo_total,
                    normal: receta.precio_venta > receta.costo_total,
                  }"
                ></div>

                <!-- Información principal -->
                <div class="info-principal" @click="toggleReceta(receta.id)">
                  <div class="info-header">
                    <h4 class="receta-nombre">{{ receta.nombre }}</h4>
                    <div class="badges-container">
                      <span class="badge-cantidad">
                        {{ (receta.insumos || []).length }} insumos
                      </span>
                      <span
                        class="badge-rentabilidad"
                        :class="
                          receta.precio_venta > receta.costo_total
                            ? 'rentable'
                            : 'no-rentable'
                        "
                      >
                        {{
                          receta.precio_venta > receta.costo_total
                            ? "Rentable"
                            : "No Rentable"
                        }}
                      </span>
                    </div>
                  </div>

                  <div class="info-detalles">
                    <div class="detalle-grupo">
                      <div class="detalle-item">
                        <span class="detalle-label">Rinde:</span>
                        <span class="detalle-valor">
                          {{ receta.rinde }} {{ receta.unidad_rinde }}
                        </span>
                      </div>
                      <div class="detalle-item">
                        <span class="detalle-label">Costo:</span>
                        <span class="detalle-valor">
                          ${{ formatDecimal(receta.costo_total) }}
                        </span>
                      </div>
                      <div class="detalle-item">
                        <span class="detalle-label">Venta:</span>
                        <span class="detalle-valor">
                          ${{ formatDecimal(receta.precio_venta) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Acciones - DENTRO del contenedor compacto -->
                <div class="acciones-container">
                  <button
                    class="btn-accion btn-gestionar"
                    @click="agregarInsumosAReceta(receta)"
                    title="Gestionar insumos"
                  >
                    <i class="fas fa-list"></i>
                  </button>
                  <button
                    class="btn-accion btn-editar"
                    @click="editarReceta(receta)"
                    title="Editar receta"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="btn-accion btn-eliminar"
                    @click="confirmarEliminarReceta(receta)"
                    title="Eliminar receta"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <!-- Desplegable de detalles de la receta - DENTRO del mismo receta-item -->
              <div
                v-if="recetaDesplegada[receta.id]"
                class="receta-detalles-desplegable"
              >
                <div class="detalles-content">
                  <!-- Información de rentabilidad -->
                  <div class="receta-rentabilidad-info">
                    <h4>
                      <i class="fas fa-chart-line"></i> Información de
                      Rentabilidad
                    </h4>
                    <div class="receta-rentabilidad-grid">
                      <div class="rentabilidad-item">
                        <span class="rentabilidad-label">Costo Total:</span>
                        <span class="rentabilidad-valor">
                          ${{ formatDecimal(receta.costo_total) }}
                        </span>
                      </div>
                      <div class="rentabilidad-item">
                        <span class="rentabilidad-label">Precio de Venta:</span>
                        <span class="rentabilidad-valor">
                          ${{ formatDecimal(receta.precio_venta) }}
                        </span>
                      </div>
                      <div class="rentabilidad-item">
                        <span class="rentabilidad-label">Ganancia:</span>
                        <span
                          class="rentabilidad-valor"
                          :class="{
                            positiva: receta.precio_venta > receta.costo_total,
                            negativa: receta.precio_venta <= receta.costo_total,
                          }"
                        >
                          ${{
                            formatDecimal(
                              receta.precio_venta - receta.costo_total
                            )
                          }}
                        </span>
                      </div>
                      <div class="rentabilidad-item">
                        <span class="rentabilidad-label">Margen:</span>
                        <span
                          class="rentabilidad-valor"
                          :class="{
                            positiva: receta.precio_venta > receta.costo_total,
                            negativa: receta.precio_venta <= receta.costo_total,
                          }"
                        >
                          {{
                            receta.costo_total > 0
                              ? formatDecimal(
                                  ((receta.precio_venta - receta.costo_total) /
                                    receta.costo_total) *
                                    100
                                )
                              : "0.00"
                          }}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Lista de insumos -->
                  <div class="receta-insumos-section">
                    <div class="insumos-header">
                      <h4>
                        <i class="fas fa-list"></i> Lista de Insumos ({{
                          (receta.insumos || []).length
                        }})
                      </h4>
                      <button
                        class="btn-agregar-insumo"
                        @click="agregarInsumosAReceta(receta)"
                      >
                        <i class="fas fa-plus"></i> Gestionar Insumos
                      </button>
                    </div>

                    <div class="insumos-list">
                      <div
                        v-for="insumo in receta.insumos || []"
                        :key="insumo.id"
                        class="insumo-item"
                      >
                        <div class="insumo-info">
                          <span class="insumo-nombre">
                            {{ insumo.insumo.nombre }}
                          </span>
                          <span class="insumo-cantidad">
                            {{ formatDecimal(insumo.cantidad) }}
                            {{ insumo.unidad_medida.abreviatura }}
                          </span>
                        </div>
                        <div class="insumo-costo-container">
                          <span
                            class="insumo-costo"
                            v-if="insumo.insumo.precio_unitario != null"
                          >
                            ${{ formatDecimal(calcularCostoInsumo(insumo)) }}
                            <small style="font-size: 0.7rem; opacity: 0.7">
                              (${{
                                formatDecimal(insumo.insumo.precio_unitario)
                              }}/{{ insumo.insumo.unidad_medida.abreviatura }})
                            </small>
                          </span>
                          <span class="insumo-costo" v-else>
                            Sin precio
                            <small style="font-size: 0.7rem; opacity: 0.7">
                              (Precio unitario no definido)
                            </small>
                          </span>
                        </div>
                      </div>
                      <div
                        v-if="(receta.insumos || []).length === 0"
                        class="sin-insumos"
                      >
                        <i class="fas fa-info-circle"></i>
                        <p>Esta receta no tiene insumos asignados</p>
                        <button
                          class="btn-agregar-insumo-small"
                          @click="agregarInsumosAReceta(receta)"
                        >
                          <i class="fas fa-plus"></i> Agregar Insumos
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Alertas de rentabilidad -->
                  <div
                    v-if="receta.precio_venta <= receta.costo_total"
                    class="receta-alerta alerta-no-rentable"
                  >
                    <i class="fas fa-exclamation-circle"></i>
                    <span>
                      ¡Receta no rentable! El precio de venta no cubre los
                      costos.
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Controles de paginación - FUERA del recetas-list pero DENTRO del recetas-card -->
          <div class="pagination-controls" v-if="totalPaginas > 1">
            <div class="pagination-info">
              Mostrando {{ inicioPagina }}-{{ finPagina }} de
              {{ recetasFiltradas.length }} receta(s)
            </div>
            <div class="pagination-buttons">
              <button
                class="pagination-btn"
                :disabled="paginaActual === 1"
                @click="cambiarPagina(paginaActual - 1)"
              >
                <i class="fas fa-chevron-left"></i>
              </button>

              <div class="pagination-numbers">
                <button
                  v-for="pagina in paginasVisibles"
                  :key="pagina"
                  class="pagination-number"
                  :class="{ active: pagina === paginaActual }"
                  @click="cambiarPagina(pagina)"
                >
                  {{ pagina }}
                </button>
                <span
                  v-if="mostrarPuntosSuspensivos"
                  class="pagination-ellipsis"
                  >...</span
                >
              </div>

              <button
                class="pagination-btn"
                :disabled="paginaActual === totalPaginas"
                @click="cambiarPagina(paginaActual + 1)"
              >
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Botón Nueva Receta flotante - FUERA del card -->
        <button class="btn-nueva-receta-flotante" @click="showNuevaRecetaModal">
          <i class="fas fa-plus"></i>
          <span>Nueva Receta</span>
        </button>
      </main>
    </div>

    <!-- MODALES REFACTORIZADOS -->

    <!-- Modal para Nueva/Editar Receta -->
    <BaseModal
      v-model:show="showModalReceta"
      :title="esEdicion ? 'Editar Receta' : 'Nueva Receta'"
      size="medium"
      @close="closeModal"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input
            v-model="formReceta.nombre"
            type="text"
            required
            class="form-input"
            placeholder="Nombre de la receta"
          />
        </div>
        <div class="form-group">
          <label>Rinde:</label>
          <input
            v-model="formReceta.rinde"
            type="number"
            min="1"
            required
            class="form-input"
            placeholder="Cantidad que rinde"
          />
        </div>
        <div class="form-group">
          <label>Unidad de Rinde:</label>
          <select v-model="formReceta.unidad_rinde" required class="form-input">
            <option value="porciones">Porciones</option>
            <option value="unidades">Unidades</option>
          </select>
        </div>
        <div class="form-group">
          <label>Precio de Venta:</label>
          <input
            v-model="formReceta.precio_venta"
            type="number"
            step="1"
            min="0"
            required
            class="form-input"
            placeholder="Precio de venta"
          />
        </div>
      </div>

      <template #footer>
        <ModalButtons
          :confirm-text="esEdicion ? 'Actualizar' : 'Guardar Receta'"
          @cancel="closeModal"
          @confirm="guardarRecetaBasica"
        />
      </template>
    </BaseModal>

    <!-- Modal para Agregar/Eliminar Insumos a Receta -->
    <BaseModal
      v-model:show="showModalInsumos"
      :title="`Gestionar Insumos: ${recetaSeleccionada?.nombre || ''}`"
      size="large"
      @close="showModalInsumos = false"
    >
      <div class="insumos-section">
        <h4>Agregar Nuevo Insumo:</h4>
        <div class="form-grid">
          <div class="form-group">
            <label>Insumo:</label>
            <div class="select-with-button">
              <select
                v-model="nuevoInsumo.insumo_id"
                required
                class="form-input"
                @change="actualizarUnidadNuevoInsumo"
              >
                <option value="">Seleccione un insumo</option>
                <option
                  v-for="item in insumosDisponibles"
                  :key="item.id"
                  :value="item.id"
                >
                  {{ item.nombre }}
                </option>
              </select>
              <button
                type="button"
                class="btn-agregar-nuevo"
                @click="showNuevoInsumoModal = true"
                title="Agregar nuevo insumo"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>Cantidad:</label>
            <input
              v-model="nuevoInsumo.cantidad"
              type="number"
              step="1"
              min="0"
              required
              class="form-input"
              placeholder="0.000"
            />
          </div>
          <div class="form-group">
            <label>Unidad de Medida:</label>
            <select
              v-model="nuevoInsumo.unidad_medida_id"
              required
              class="form-input"
            >
              <option value="">Seleccione una unidad</option>
              <option
                v-for="unidad in unidadesMedida"
                :key="unidad.id"
                :value="unidad.id"
              >
                {{ unidad.nombre }} ({{ unidad.abreviatura }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <button
              class="btn-agregar-insumo-modal"
              @click="agregarInsumoAReceta"
              :disabled="!puedeAgregarInsumo"
            >
              <i class="fas fa-plus"></i> Agregar
            </button>
          </div>
        </div>
      </div>

      <div class="insumos-existente-section">
        <h4>
          Insumos Actuales ({{ recetaSeleccionada?.insumos?.length || 0 }}):
        </h4>
        <div
          v-for="insumo in recetaSeleccionada?.insumos || []"
          :key="insumo.id"
          class="insumo-existente-item"
        >
          <span v-if="!insumo.editando" class="insumo-info">
            {{ insumo.insumo.nombre }} - {{ formatDecimal(insumo.cantidad) }}
            {{ insumo.unidad_medida.abreviatura }}
            <span class="insumo-costo" v-if="insumo.insumo.precio_unitario">
              (Costo: ${{ formatDecimal(calcularCostoInsumo(insumo)) }})
            </span>
          </span>
          <div v-else class="insumo-edit-form">
            <div class="edit-form-grid">
              <div class="form-group">
                <label>Cantidad:</label>
                <input
                  v-model.number="insumo.cantidadEdit"
                  type="number"
                  step="1"
                  min="0"
                  class="form-input-small"
                  placeholder="0.000"
                  @input="formatearCantidadInput($event, insumo)"
                />
              </div>
              <div class="form-group">
                <label>Unidad:</label>
                <select
                  v-model="insumo.unidad_medida_id_edit"
                  class="form-input-small"
                  required
                >
                  <option value="">Seleccione...</option>
                  <option
                    v-for="unidad in unidadesMedida"
                    :key="unidad.id"
                    :value="unidad.id"
                  >
                    {{ unidad.abreviatura }} ({{ unidad.nombre }})
                  </option>
                </select>
              </div>
            </div>
          </div>
          <div class="insumo-acciones">
            <button
              v-if="!insumo.editando"
              class="btn-accion-small"
              @click="activarEdicionInsumo(insumo)"
              title="Editar insumo"
            >
              <i class="fas fa-edit"></i>
            </button>
            <button
              v-else
              class="btn-accion-small btn-confirmar"
              @click="guardarEdicionInsumo(insumo)"
              title="Guardar cambios"
            >
              <i class="fas fa-check"></i>
            </button>
            <button
              v-if="!insumo.editando"
              class="btn-accion-small btn-eliminar-modal"
              @click="eliminarInsumoDeReceta(recetaSeleccionada, insumo)"
              title="Eliminar insumo"
            >
              <i class="fas fa-trash"></i>
            </button>
            <button
              v-else
              class="btn-accion-small btn-cancelar"
              @click="cancelarEdicionInsumo(insumo)"
              title="Cancelar edición"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        <div v-if="!recetaSeleccionada?.insumos?.length" class="sin-insumos">
          <i class="fas fa-info-circle"></i>
          No hay insumos agregados a esta receta
        </div>
      </div>

      <template #footer>
        <ModalButtons
          :show-cancel="false"
          confirm-text="Cerrar"
          @cancel="showModalInsumos = false"
          @confirm="showModalInsumos = false"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nuevo Insumo -->
    <BaseModal
      v-model:show="showNuevoInsumoModal"
      title="Nuevo Insumo"
      size="medium"
      @close="showNuevoInsumoModal = false"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input
            v-model="formNuevoInsumo.nombre"
            type="text"
            required
            class="form-input"
            placeholder="Nombre del insumo"
          />
        </div>
        <div class="form-group">
          <label>Unidad de Medida:</label>
          <select
            v-model="formNuevoInsumo.unidad_medida_id"
            required
            class="form-input"
          >
            <option value="">Seleccione una unidad</option>
            <option
              v-for="unidad in unidadesMedida"
              :key="unidad.id"
              :value="unidad.id"
            >
              {{ unidad.nombre }} ({{ unidad.abreviatura }})
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Stock Mínimo:</label>
          <input
            v-model="formNuevoInsumo.stock_minimo"
            type="number"
            step="1"
            min="0"
            required
            class="form-input"
            placeholder="0.000"
          />
        </div>
        <div class="form-group">
          <label>Precio Unitario:</label>
          <input
            v-model="formNuevoInsumo.precio_unitario"
            type="number"
            step="1"
            min="0"
            class="form-input"
            placeholder="0.00"
          />
        </div>
      </div>

      <template #footer>
        <ModalButtons
          confirm-text="Guardar"
          @cancel="showNuevoInsumoModal = false"
          @confirm="guardarNuevoInsumo"
        />
      </template>
    </BaseModal>

    <!-- Modal de confirmación para eliminar receta -->
    <ConfirmModal
      :show="showConfirmModal"
      title="Confirmar Eliminación"
      :message="`¿Está seguro de que desea eliminar la receta '${recetaAEliminar?.nombre}'?`"
      confirm-text="Eliminar"
      @update:show="showConfirmModal = $event"
      @cancel="showConfirmModal = false"
      @confirm="eliminarReceta"
    />
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted, inject } from "vue";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import BaseModal from "./Modals/BaseModal.vue";
import ModalButtons from "./Modals/ModalButtons.vue";
import ConfirmModal from "./Modals/ConfirmModal.vue";
import PageHeader from "../components/PageHeader.vue";
import axios from "axios";

const router = useRouter();
const notificationSystem = inject("notifications");

const recetas = ref([]);
const insumosDisponibles = ref([]);
const unidadesMedida = ref([]);
const searchTerm = ref("");
const loading = ref(true);
const insumoEditando = ref(null);
const recetaDesplegada = ref({});

const showModalReceta = ref(false);
const showModalInsumos = ref(false);
const showConfirmModal = ref(false);
const showNuevoInsumoModal = ref(false);
const filtroActivo = ref("");
const paginaActual = ref(1);
const itemsPorPagina = ref(10);
const sidebarRef = ref(null);

// Stats para el header
const recetasStats = computed(() => {
  const stats = [];

  // Estadística de no rentables
  if (notificacionesRecetasNoRentables.value.length > 0) {
    stats.push({
      type: "bajo",
      icon: "fas fa-exclamation-circle",
      label: `${notificacionesRecetasNoRentables.value.length} no rentable(s)`,
      tooltip: "Filtrar recetas no rentables",
      value: notificacionesRecetasNoRentables.value.length,
    });
  }

  // Total de recetas
  stats.push({
    type: "total",
    icon: "fas fa-utensils",
    label: `${recetasFiltradas.value.length} receta(s)`,
    tooltip: "Total de recetas",
  });

  return stats;
});

// Filtros para el header
const recetasFilters = computed(() => [
  {
    type: "text",
    placeholder: "🔍 Buscar receta...",
    value: searchTerm.value,
    autocomplete: "off",
  },
]);

// Handlers
const handleStatClick = (stat) => {
  if (stat.type === "bajo") {
    aplicarFiltroNoRentables();
  }
};

const handleFilterChange = ({ filter, value }) => {
  if (filter.placeholder.includes("Buscar receta")) {
    searchTerm.value = value;
  }
};

const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};

const limpiarFiltros = () => {
  filtroActivo.value = "";
  searchTerm.value = "";
  cerrarTodasLasRecetas();
  resetearPaginacion();
};

const formReceta = ref({
  id: null,
  nombre: "",
  rinde: 1,
  unidad_rinde: "porciones",
  precio_venta: 0,
});

const nuevoInsumo = ref({
  insumo_id: "",
  cantidad: 0,
  unidad_medida_id: "",
});

const esEdicion = ref(false);
const recetaAEliminar = ref(null);
const recetaSeleccionada = ref(null);

const aplicarFiltroNoRentables = () => {
  filtroActivo.value =
    filtroActivo.value === "no-rentable" ? "" : "no-rentable";
  cerrarTodasLasRecetas();
  resetearPaginacion();
};

const recetasPaginadas = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina.value;
  const fin = inicio + itemsPorPagina.value;
  return recetasFiltradas.value.slice(inicio, fin);
});

const totalPaginas = computed(() => {
  return Math.ceil(recetasFiltradas.value.length / itemsPorPagina.value);
});

const inicioPagina = computed(() => {
  return (paginaActual.value - 1) * itemsPorPagina.value + 1;
});

const finPagina = computed(() => {
  const fin = paginaActual.value * itemsPorPagina.value;
  return Math.min(fin, recetasFiltradas.value.length);
});

const paginasVisibles = computed(() => {
  const total = totalPaginas.value;
  const actual = paginaActual.value;
  const paginas = [];

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      paginas.push(i);
    }
  } else {
    if (actual <= 4) {
      for (let i = 1; i <= 5; i++) {
        paginas.push(i);
      }
      paginas.push(total);
    } else if (actual >= total - 3) {
      paginas.push(1);
      for (let i = total - 4; i <= total; i++) {
        paginas.push(i);
      }
    } else {
      paginas.push(1);
      for (let i = actual - 1; i <= actual + 1; i++) {
        paginas.push(i);
      }
      paginas.push(total);
    }
  }

  return paginas;
});

const mostrarPuntosSuspensivos = computed(() => {
  return (
    totalPaginas.value > 7 &&
    paginaActual.value > 4 &&
    paginaActual.value < totalPaginas.value - 3
  );
});

const recetasFiltradas = computed(() => {
  let filtered = recetas.value;

  if (filtroActivo.value === "no-rentable") {
    filtered = filtered.filter(
      (receta) => receta.precio_venta <= receta.costo_total
    );
  }

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter((item) =>
      item.nombre.toLowerCase().includes(term)
    );
  }

  return filtered.sort((a, b) => {
    const aNoRentable = a.precio_venta <= a.costo_total;
    const bNoRentable = b.precio_venta <= b.costo_total;

    if (aNoRentable && !bNoRentable) return -1;
    if (!aNoRentable && bNoRentable) return 1;

    return a.nombre.localeCompare(b.nombre);
  });
});

const puedeAgregarInsumo = computed(() => {
  return (
    nuevoInsumo.value.insumo_id &&
    nuevoInsumo.value.cantidad > 0 &&
    nuevoInsumo.value.unidad_medida_id
  );
});

const formNuevoInsumo = ref({
  nombre: "",
  unidad_medida_id: "",
  stock_minimo: 0,
  precio_unitario: null,
});

const notificacionesLeidas = ref(new Set());

const notificacionesRecetasNoRentables = computed(() => {
  return recetas.value
    .filter((receta) => {
      const costoTotal = parseFloat(receta.costo_total) || 0;
      const precioVenta = parseFloat(receta.precio_venta) || 0;
      return precioVenta <= costoTotal;
    })
    .filter((notif) => !notif.leida);
});

const cambiarPagina = (pagina) => {
  if (pagina >= 1 && pagina <= totalPaginas.value) {
    cerrarTodasLasRecetas();
    paginaActual.value = pagina;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};

const resetearPaginacion = () => {
  cerrarTodasLasRecetas();
  paginaActual.value = 1;
};

const toggleReceta = (recetaId) => {
  const estaAbierta = recetaDesplegada.value[recetaId];

  if (estaAbierta) {
    recetaDesplegada.value = { [recetaId]: false };
  } else {
    recetaDesplegada.value = { [recetaId]: true };
  }
};

const cerrarTodasLasRecetas = () => {
  recetaDesplegada.value = {};
};

const logout = async () => {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
      await axios.post("/api/auth/logout/", { refresh: refreshToken });
    }
  } catch (err) {
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete axios.defaults.headers.common["Authorization"];
    router.push("/login");
  }
};

const formatDecimal = (value) => {
  if (value === null || value === undefined) return "0.00";

  const numericValue =
    typeof value === "string" ? parseFloat(value.replace(",", ".")) : value;

  return Number(numericValue).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const convertirUnidad = (cantidad, unidadOrigen, unidadDestino) => {
  if (unidadOrigen === unidadDestino) return cantidad;

  const conversiones = {
    kg: { g: 1000, mg: 1000000 },
    g: { kg: 0.001, mg: 1000 },
    mg: { kg: 0.000001, g: 0.001 },
    l: { ml: 1000, cl: 100 },
    ml: { l: 0.001, cl: 0.1 },
    cl: { l: 0.01, ml: 10 },
    unidad: { u: 1, pz: 1 },
    u: { unidad: 1, pz: 1 },
    pz: { unidad: 1, u: 1 },
    docena: { unidad: 12, u: 12 },
    doc: { unidad: 12, u: 12 },
  };

  unidadOrigen = unidadOrigen.toLowerCase();
  unidadDestino = unidadDestino.toLowerCase();

  if (conversiones[unidadOrigen] && conversiones[unidadOrigen][unidadDestino]) {
    return cantidad * conversiones[unidadOrigen][unidadDestino];
  }

  if (
    conversiones[unidadDestino] &&
    conversiones[unidadDestino][unidadOrigen]
  ) {
    return cantidad / conversiones[unidadDestino][unidadOrigen];
  }

  return cantidad;
};

const calcularCostoInsumo = (insumoReceta) => {
  if (
    !insumoReceta ||
    !insumoReceta.insumo ||
    insumoReceta.insumo.precio_unitario === null ||
    insumoReceta.insumo.precio_unitario === undefined
  ) {
    return 0;
  }

  try {
    const precioUnitario = parseFloat(
      insumoReceta.insumo.precio_unitario.toString().replace(",", ".")
    );
    const cantidad = parseFloat(
      insumoReceta.cantidad.toString().replace(",", ".")
    );

    if (!insumoReceta.insumo.unidad_medida || !insumoReceta.unidad_medida) {
      return precioUnitario * cantidad;
    }

    const unidadInsumo =
      insumoReceta.insumo.unidad_medida.abreviatura.toLowerCase();
    const unidadReceta = insumoReceta.unidad_medida.abreviatura.toLowerCase();

    if (unidadInsumo === unidadReceta) {
      return precioUnitario * cantidad;
    }

    const cantidadConvertida = convertirUnidad(
      cantidad,
      unidadReceta,
      unidadInsumo
    );
    const costo = precioUnitario * cantidadConvertida;

    return isNaN(costo) ? 0 : costo;
  } catch (error) {
    return 0;
  }
};

const showNuevaRecetaModal = () => {
  esEdicion.value = false;
  resetFormReceta();
  showModalReceta.value = true;
};

const editarReceta = (receta) => {
  esEdicion.value = true;
  formReceta.value = {
    id: receta.id,
    nombre: receta.nombre,
    rinde: receta.rinde,
    unidad_rinde: receta.unidad_rinde,
    precio_venta: receta.precio_venta,
  };
  showModalReceta.value = true;
};

const agregarInsumosAReceta = (receta) => {
  recetaSeleccionada.value = receta;
  resetNuevoInsumo();
  showModalInsumos.value = true;
};

const confirmarEliminarReceta = (receta) => {
  recetaAEliminar.value = receta;
  showConfirmModal.value = true;
};

const actualizarUnidadNuevoInsumo = () => {
  const insumoId = nuevoInsumo.value.insumo_id;

  if (!insumoId) {
    nuevoInsumo.value.unidad_medida_id = "";
    return;
  }

  const insumo = insumosDisponibles.value.find(
    (i) => i.id === parseInt(insumoId)
  );

  if (insumo && insumo.unidad_medida) {
    nuevoInsumo.value.unidad_medida_id = insumo.unidad_medida.id;
    nuevoInsumo.value.cantidad = 1;
  } else {
    nuevoInsumo.value.unidad_medida_id = "";
  }
};

const agregarInsumoAReceta = async () => {
  try {
    if (!puedeAgregarInsumo.value) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "Complete todos los campos del insumo",
        timeout: 4000,
      });
      return;
    }

    if (nuevoInsumo.value.cantidad <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La cantidad debe ser mayor a cero",
        timeout: 4000,
      });
      return;
    }

    const insumoData = {
      insumo: parseInt(nuevoInsumo.value.insumo_id),
      unidad_medida: parseInt(nuevoInsumo.value.unidad_medida_id),
      cantidad: parseFloat(nuevoInsumo.value.cantidad),
    };

    const response = await axios.post(
      `/api/recetas/${recetaSeleccionada.value.id}/insumos/`,
      insumoData
    );

    const nuevoInsumoObj = {
      ...response.data,
      editando: false,
      insumo: insumosDisponibles.value.find(
        (i) => i.id === parseInt(nuevoInsumo.value.insumo_id)
      ),
      unidad_medida: unidadesMedida.value.find(
        (u) => u.id === parseInt(nuevoInsumo.value.unidad_medida_id)
      ),
    };

    if (!recetaSeleccionada.value.insumos) {
      recetaSeleccionada.value.insumos = [];
    }
    recetaSeleccionada.value.insumos.push(nuevoInsumoObj);

    await recalcularCostosReceta();
    await onInsumosModificados(recetaSeleccionada.value);

    notificationSystem.show({
      type: "success",
      title: "Insumo agregado",
      message: "Insumo agregado correctamente a la receta",
      timeout: 4000,
    });

    resetNuevoInsumo();
  } catch (error) {
    let errorMessage = "Error al agregar el insumo a la receta";

    if (error.response?.data) {
      if (typeof error.response.data === "object") {
        const errors = [];
        for (const key in error.response.data) {
          if (Array.isArray(error.response.data[key])) {
            errors.push(...error.response.data[key]);
          } else {
            errors.push(error.response.data[key]);
          }
        }
        errorMessage = errors.join(", ");
      } else if (typeof error.response.data === "string") {
        errorMessage = error.response.data;
      }
    }

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: errorMessage,
      timeout: 4000,
    });
  }
};

const eliminarInsumoDeReceta = async (receta, insumo) => {
  try {
    await axios.delete(`/api/recetas/${receta.id}/insumos/${insumo.id}/`);

    const insumoIndex = receta.insumos.findIndex((i) => i.id === insumo.id);
    if (insumoIndex !== -1) {
      receta.insumos.splice(insumoIndex, 1);
    }

    await onInsumosModificados(receta);

    notificationSystem.show({
      type: "success",
      title: "Insumo eliminado",
      message: "Insumo eliminado correctamente de la receta",
      timeout: 4000,
    });
  } catch (error) {
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al eliminar el insumo de la receta",
      timeout: 6000,
    });
  }
};

const guardarRecetaBasica = async () => {
  try {
    if (!formReceta.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre es requerido",
        timeout: 4000,
      });
      return;
    }

    const datosParaEnviar = {
      nombre: formReceta.value.nombre,
      rinde: formReceta.value.rinde,
      unidad_rinde: formReceta.value.unidad_rinde,
      precio_venta: formReceta.value.precio_venta,
      costo_unitario: 0,
      costo_total: 0,
    };

    let response;
    let esNuevaReceta = !esEdicion.value;

    if (esEdicion.value) {
      response = await axios.put(
        `/api/recetas/${formReceta.value.id}/`,
        datosParaEnviar
      );

      notificationSystem.show({
        type: "success",
        title: "Receta actualizada",
        message: "Receta actualizada correctamente",
        timeout: 4000,
      });
    } else {
      response = await axios.post("/api/recetas/", datosParaEnviar);

      notificationSystem.show({
        type: "success",
        title: "Receta creada",
        message: "Receta creada correctamente",
        timeout: 4000,
      });
    }

    await fetchRecetas();
    closeModal();

    const recetaGuardada = response.data;
    verificarRentabilidadYNotificar(recetaGuardada);

    if (esNuevaReceta && response.data.id) {
      setTimeout(() => {
        if (!esEdicion.value) {
          const nuevaReceta = {
            id: response.data.id,
            nombre: response.data.nombre,
            rinde: response.data.rinde,
            unidad_rinde: response.data.unidad_rinde,
            precio_venta: response.data.precio_venta,
            costo_total: response.data.costo_total || 0,
            insumos: response.data.insumos || [],
          };
          agregarInsumosAReceta(nuevaReceta);
        }
      }, 100);
    }
  } catch (error) {
    if (error.response?.status === 400) {
      let errorMessage = "Error de validación";
      if (error.response.data) {
        if (typeof error.response.data === "object") {
          const errors = [];
          for (const key in error.response.data) {
            if (Array.isArray(error.response.data[key])) {
              errors.push(...error.response.data[key]);
            } else {
              errors.push(error.response.data[key]);
            }
          }
          errorMessage = errors.join(", ");
        } else if (typeof error.response.data === "string") {
          errorMessage = error.response.data;
        }
      }

      notificationSystem.show({
        type: "error",
        title: "Error al guardar receta",
        message: errorMessage,
        timeout: 4000,
      });
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al guardar la receta",
        timeout: 4000,
      });
    }
  }
};

const eliminarReceta = async () => {
  try {
    await axios.delete(`/api/recetas/${recetaAEliminar.value.id}/`);

    const index = recetas.value.findIndex(
      (item) => item.id === recetaAEliminar.value.id
    );
    if (index !== -1) {
      recetas.value.splice(index, 1);
    }

    showConfirmModal.value = false;
    actualizarNotificacionesRecetas();

    notificationSystem.show({
      type: "success",
      title: "Receta eliminada",
      message: "Receta eliminada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al eliminar la receta",
      timeout: 6000,
    });
  }
};

const guardarNuevoInsumo = async () => {
  try {
    if (!formNuevoInsumo.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre del insumo es requerido",
        timeout: 4000,
      });
      return;
    }
    if (!formNuevoInsumo.value.unidad_medida_id) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La unidad de medida es requerida",
        timeout: 4000,
      });
      return;
    }

    const datosParaEnviar = {
      nombre: formNuevoInsumo.value.nombre,
      unidad_medida_id: formNuevoInsumo.value.unidad_medida_id,
      stock_minimo: parseFloat(formNuevoInsumo.value.stock_minimo) || 0,
      precio_unitario: formNuevoInsumo.value.precio_unitario
        ? parseFloat(formNuevoInsumo.value.precio_unitario)
        : null,
      stock_actual: 0,
      activo: true,
    };

    const response = await axios.post("/api/insumos/crear/", datosParaEnviar);

    await fetchInsumosDisponibles();
    nuevoInsumo.value.insumo_id = response.data.id;

    showNuevoInsumoModal.value = false;
    resetFormNuevoInsumo();

    notificationSystem.show({
      type: "success",
      title: "Insumo creado",
      message: "Insumo creado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    let errorMessage = "Error al crear el insumo";
    if (error.response?.data) {
      if (typeof error.response.data === "object") {
        errorMessage = Object.values(error.response.data).join(", ");
      } else {
        errorMessage = error.response.data;
      }
    }

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: errorMessage,
      timeout: 6000,
    });
  }
};

const activarEdicionInsumo = (insumo) => {
  if (recetaSeleccionada.value?.insumos) {
    recetaSeleccionada.value.insumos.forEach((i) => {
      i.editando = false;
    });
  }

  insumo.editando = true;
  insumo.cantidadEdit = parseFloat(
    insumo.cantidad.toString().replace(",", ".")
  );
  insumo.insumo_id_edit = insumo.insumo.id;
  insumo.unidad_medida_id_edit = insumo.unidad_medida.id;
  insumoEditando.value = insumo;
};

const cancelarEdicionInsumo = (insumo) => {
  insumo.editando = false;
  delete insumo.cantidadEdit;
  delete insumo.insumo_id_edit;
  delete insumo.unidad_medida_id_edit;
  insumoEditando.value = null;
};

const guardarEdicionInsumo = async (insumo) => {
  try {
    if (!insumo.cantidadEdit || insumo.cantidadEdit <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La cantidad debe ser mayor a cero",
        timeout: 4000,
      });
      return;
    }

    if (!insumo.unidad_medida_id_edit) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "Seleccione una unidad de medida válida",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.patch(
      `/api/recetas/${recetaSeleccionada.value.id}/insumos/${insumo.id}/actualizar/`,
      {
        cantidad: parseFloat(insumo.cantidadEdit),
        unidad_medida: parseInt(insumo.unidad_medida_id_edit),
      }
    );

    insumo.cantidad = parseFloat(insumo.cantidadEdit);

    const nuevaUnidad = unidadesMedida.value.find(
      (u) => u.id === parseInt(insumo.unidad_medida_id_edit)
    );
    if (nuevaUnidad) {
      insumo.unidad_medida = nuevaUnidad;
    }

    insumo.editando = false;
    delete insumo.cantidadEdit;
    delete insumo.insumo_id_edit;
    delete insumo.unidad_medida_id_edit;
    insumoEditando.value = null;

    await recalcularCostosReceta();
    await onInsumosModificados(recetaSeleccionada.value);

    notificationSystem.show({
      type: "success",
      title: "Insumo actualizado",
      message: "Insumo actualizado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    let errorMessage = "Error al actualizar el insumo";
    if (error.response?.data) {
      if (typeof error.response.data === "object") {
        const errors = [];
        for (const key in error.response.data) {
          if (Array.isArray(error.response.data[key])) {
            errors.push(...error.response.data[key]);
          } else if (typeof error.response.data[key] === "object") {
            for (const subKey in error.response.data[key]) {
              if (Array.isArray(error.response.data[key][subKey])) {
                errors.push(...error.response.data[key][subKey]);
              } else {
                errors.push(error.response.data[key][subKey]);
              }
            }
          } else {
            errors.push(error.response.data[key]);
          }
        }
        errorMessage = errors.join(", ");
      } else if (typeof error.response.data === "string") {
        errorMessage = error.response.data;
      }
    }

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: errorMessage,
      timeout: 8000,
    });
  }
};

const formatearCantidadInput = (event, insumo) => {
  const input = event.target;
  let value = input.value;
  value = value.replace(",", ".");

  if (!isNaN(value) && value !== "") {
    insumo.cantidadEdit = parseFloat(value);
  }
};

const recalcularCostosReceta = async () => {
  if (!recetaSeleccionada.value) return;

  try {
    let costoTotal = 0;

    if (recetaSeleccionada.value.insumos) {
      recetaSeleccionada.value.insumos.forEach((insumo) => {
        costoTotal += calcularCostoInsumo(insumo);
      });
    }

    recetaSeleccionada.value.costo_total = costoTotal;

    const recetaIndex = recetas.value.findIndex(
      (r) => r.id === recetaSeleccionada.value.id
    );
    if (recetaIndex !== -1) {
      recetas.value[recetaIndex].costo_total = costoTotal;

      if (recetas.value[recetaIndex].rinde > 0) {
        recetas.value[recetaIndex].costo_unitario =
          costoTotal / recetas.value[recetaIndex].rinde;
      }
    }
  } catch (error) {}
};

const closeModal = () => {
  showModalReceta.value = false;
  showModalInsumos.value = false;
  showConfirmModal.value = false;
  showNuevoInsumoModal.value = false;
  resetFormReceta();
};

const resetFormReceta = () => {
  formReceta.value = {
    id: null,
    nombre: "",
    rinde: 1,
    unidad_rinde: "porciones",
    precio_venta: 0,
  };
  esEdicion.value = false;
};

const resetNuevoInsumo = () => {
  nuevoInsumo.value = {
    insumo_id: "",
    cantidad: 0,
    unidad_medida_id: "",
  };
};

const resetFormNuevoInsumo = () => {
  formNuevoInsumo.value = {
    nombre: "",
    unidad_medida_id: "",
    stock_minimo: 0,
    precio_unitario: null,
  };
};

const fetchRecetas = async () => {
  try {
    loading.value = true;
    const response = await axios.get("/api/recetas/");

    recetas.value = response.data.map((receta) => {
      if (!receta.insumos) {
        receta.insumos = [];
      }

      return {
        ...receta,
        insumos: receta.insumos || [],
        costo_total: parseFloat(receta.costo_total) || 0,
        costo_unitario: parseFloat(receta.costo_unitario) || 0,
      };
    });

    loading.value = false;
  } catch (err) {
    loading.value = false;
    if (err.response?.status === 401) {
      logout();
    }
  }
};

const fetchInsumosDisponibles = async () => {
  try {
    const response = await axios.get("/api/insumos/");
    insumosDisponibles.value = response.data.insumos;
  } catch (err) {}
};

const fetchUnidadesMedida = async () => {
  try {
    const response = await axios.get("/api/unidades-medida/");
    unidadesMedida.value = response.data;
  } catch (err) {}
};

const actualizarNotificacionesRecetas = () => {
  setTimeout(() => {}, 100);
};

const verificarRentabilidadYNotificar = (receta) => {
  const costoTotal = parseFloat(receta.costo_total) || 0;
  const precioVenta = parseFloat(receta.precio_venta) || 0;
  const margen = precioVenta - costoTotal;

  if (margen <= 0) {
    const notificacionId = `receta-no-rentable-${receta.id}`;

    if (!notificacionesLeidas.value.has(notificacionId)) {
      notificationSystem.show({
        type: "warning",
        title: `${receta.nombre} NO es rentable.`,
        message: `• Pérdida de $${formatDecimal(Math.abs(margen))}`,
        timeout: 4000,
      });
    }

    actualizarNotificacionesRecetas();
  } else if (margen > 0 && margen < costoTotal * 0.1) {
    notificationSystem.show({
      type: "info",
      title: "Margen Bajo",
      message: `"${receta.nombre}" tiene margen bajo: $${formatDecimal(
        margen
      )} (${formatDecimal((margen / costoTotal) * 100)}%)`,
      timeout: 4000,
    });
  }
};

const limpiarNotificacionesObsoletas = () => {
  const leidasGuardadas = JSON.parse(
    localStorage.getItem("notificacionesLeidas") || "[]"
  );
  const idsRecetasActuales = recetas.value.map(
    (r) => `receta-no-rentable-${r.id}`
  );

  const leidasFiltradas = leidasGuardadas.filter((id) =>
    idsRecetasActuales.some((recetaId) => id === recetaId)
  );

  localStorage.setItem("notificacionesLeidas", JSON.stringify(leidasFiltradas));
  notificacionesLeidas.value = new Set(leidasFiltradas);
};

const cargarNotificacionesLeidas = () => {
  const leidasGuardadas = JSON.parse(
    localStorage.getItem("notificacionesLeidas") || "[]"
  );
  notificacionesLeidas.value = new Set(leidasGuardadas);
};

const onInsumosModificados = async (receta) => {
  await recalcularCostosReceta();

  const recetaActualizada = recetas.value.find((r) => r.id === receta.id);
  if (recetaActualizada) {
    verificarRentabilidadYNotificar(recetaActualizada);
  }
};

onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  cargarNotificacionesLeidas();

  Promise.all([
    fetchRecetas(),
    fetchInsumosDisponibles(),
    fetchUnidadesMedida(),
  ])
    .then(() => {
      limpiarNotificacionesObsoletas();
      actualizarNotificacionesRecetas();

      recetas.value.forEach((receta) => {
        verificarRentabilidadYNotificar(receta);
      });
    })
    .catch((error) => {
      loading.value = false;
      if (error.response?.status === 401) {
        logout();
      }
    });
});
</script>

<style scoped>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css");

.recetas-card {
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 16px;
  margin: 0 auto;
  border: 1px solid #eaeaea;
}

.recetas-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.receta-item {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.receta-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.receta-item.no-rentable {
  border-left: 4px solid #dc3545;
}

.receta-item:not(.no-rentable) {
  border-left: 4px solid #28a745;
}

.receta-item-compact {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
}

.estado-indicador {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.estado-indicador.critico {
  background-color: #dc3545;
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.2);
}

.estado-indicador.normal {
  background-color: #28a745;
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.2);
}

.info-principal {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
  gap: 8px;
}

.receta-nombre {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.3;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badges-container {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.badge-cantidad,
.badge-rentabilidad {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-cantidad {
  background: #e9ecef;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.badge-rentabilidad.rentable {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.badge-rentabilidad.no-rentable {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.info-detalles {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detalle-grupo {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detalle-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
}

.detalle-label {
  color: #6c757d;
  font-weight: 500;
}

.detalle-valor {
  color: #495057;
  font-weight: 600;
}

.acciones-container {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.btn-accion {
  border: none;
  cursor: pointer;
  font-size: 12px;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.btn-gestionar {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.btn-gestionar:hover {
  background: linear-gradient(135deg, #138496, #117a8b);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(23, 162, 184, 0.3);
}

.btn-editar {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.btn-editar:hover {
  background: linear-gradient(135deg, #2980b9, #21618c);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
}

.btn-eliminar {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.btn-eliminar:hover {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
}

.receta-detalles-desplegable {
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

.detalles-content {
  padding: 16px;
}

.receta-rentabilidad-info h4 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: var(--color-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.receta-rentabilidad-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.rentabilidad-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.rentabilidad-label {
  font-weight: 500;
  color: #6c757d;
  font-size: 0.85rem;
}

.rentabilidad-valor {
  font-weight: 600;
  font-size: 0.85rem;
}

.rentabilidad-valor.positiva {
  color: #28a745;
}

.rentabilidad-valor.negativa {
  color: #dc3545;
}

.receta-insumos-section {
  margin-bottom: 16px;
}

.insumos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 12px;
}

.insumos-header h4 {
  margin: 0;
  font-size: 1rem;
  color: var(--color-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-agregar-insumo {
  background: linear-gradient(135deg, var(--color-success), #218838);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  font-size: 0.8rem;
  box-shadow: 0 1px 3px rgba(40, 167, 69, 0.2);
}

.btn-agregar-insumo:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(40, 167, 69, 0.3);
}

.insumos-list {
  background: white;
  border-radius: 8px;
  padding: 0;
  border: 1px solid #e9ecef;
  max-height: 300px;
  overflow-y: auto;
}

.insumo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #f8f9fa;
  transition: background-color 0.2s;
}

.insumo-item:hover {
  background-color: rgba(123, 90, 80, 0.05);
}

.insumo-item:last-child {
  border-bottom: none;
}

.insumo-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.insumo-nombre {
  font-size: 0.85rem;
  font-weight: 500;
  color: #2c3e50;
}

.insumo-cantidad {
  font-size: 0.8rem;
  color: #6c757d;
  background: #f8f9fa;
  padding: 3px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.insumo-costo-container {
  min-width: 80px;
  text-align: right;
}

.insumo-costo {
  font-size: 0.8rem;
  color: var(--color-success);
  font-weight: 600;
  background: rgba(40, 167, 69, 0.1);
  padding: 3px 6px;
  border-radius: 4px;
}

.insumos-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.insumos-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: var(--color-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  font-size: 0.9rem;
  color: #495057;
}

.form-input,
.form-input-small {
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-input-small:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(156, 122, 109, 0.1);
}

.form-input-small {
  padding: 8px 10px;
  font-size: 0.9rem;
}

.select-with-button {
  display: flex;
  gap: 8px;
}

.btn-agregar-nuevo {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-agregar-nuevo:hover {
  background: #9c7a6d;
  transform: translateY(-1px);
}

.btn-agregar-insumo-modal {
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 12px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn-agregar-insumo-modal:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
}

.btn-agregar-insumo-modal:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}

.insumos-existente-section {
  margin-top: 25px;
}

.insumos-existente-section h4 {
  margin-bottom: 15px;
  color: var(--color-primary);
  font-size: 1.1rem;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 2px solid #e9ecef;
}

.insumo-existente-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.insumo-existente-item:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.insumo-info {
  flex: 1;
  font-size: 0.95rem;
}

.insumo-costo {
  color: #28a745;
  font-weight: 500;
  font-size: 0.85rem;
  margin-left: 8px;
}

.insumo-edit-form {
  flex: 1;
}

.edit-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  align-items: center;
}

.insumo-acciones {
  display: flex;
  gap: 5px;
  margin-left: 15px;
}

.btn-accion-small {
  background: none;
  border: none;
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
}

.btn-accion-small:hover {
  background: #f8f9fa;
  transform: translateY(-1px);
}

.btn-confirmar {
  color: #28a745;
}

.btn-confirmar:hover {
  background: #d4edda;
}

.btn-eliminar-modal {
  color: #dc3545;
}

.btn-eliminar-modal:hover {
  background: #f8d7da;
}

.btn-cancelar {
  color: #6c757d;
}

.btn-cancelar:hover {
  background: #f8f9fa;
}

.receta-alerta {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.85rem;
}

.alerta-no-rentable {
  background: linear-gradient(135deg, #f8d7da, #f5b7b1);
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.btn-nueva-receta-flotante {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 50px;
  padding: 16px 24px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
  z-index: 100;
  font-size: 1rem;
}

.btn-nueva-receta-flotante:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
  color: #212529;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: var(--color-primary);
  font-size: 1.1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.loading-state i {
  font-size: 2rem;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #6c757d;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.empty-state i {
  font-size: 3rem;
  color: #bdc3c7;
}

.empty-state p {
  margin: 0;
  font-size: 1.1rem;
}

.sin-insumos {
  text-align: center;
  padding: 30px;
  color: #6c757d;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.sin-insumos i {
  font-size: 1.5rem;
  color: #bdc3c7;
}

.sin-insumos p {
  margin: 0;
  font-size: 0.9rem;
}

.btn-agregar-insumo-small {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 1px 3px rgba(123, 90, 80, 0.2);
}

.btn-agregar-insumo-small:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(123, 90, 80, 0.3);
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  padding: 15px 0;
  border-top: 1px solid #eaeaea;
  flex-wrap: wrap;
  gap: 15px;
}

.pagination-info {
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
}

.pagination-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #495057;
}

.pagination-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #adb5bd;
  transform: translateY(-1px);
}

.pagination-btn:disabled {
  background: #f8f9fa;
  color: #adb5bd;
  cursor: not-allowed;
  transform: none;
}

.pagination-btn i {
  font-size: 0.8rem;
}

.pagination-numbers {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 36px;
  padding: 0 8px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #495057;
  font-weight: 500;
  font-size: 0.9rem;
}

.pagination-number:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
  transform: translateY(-1px);
}

.pagination-number.active {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination-ellipsis {
  padding: 0 8px;
  color: #6c757d;
  font-weight: 500;
}

/* ----------------------------- MODALES (mantener los estilos de modales) ----------------------------- */

/* Agregar estos estilos al global.css */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* Responsive para recetas específicas */
@media (max-width: 767px) {
  .recetas-card {
    padding: 12px;
  }

  .receta-item-compact {
    padding: 10px 12px;
    gap: 10px;
  }

  .info-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .badges-container {
    width: 100%;
    justify-content: flex-start;
  }

  .info-detalles {
    flex-direction: column;
    gap: 6px;
  }

  .detalle-grupo {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .detalles-content {
    padding: 12px;
  }

  .receta-rentabilidad-grid {
    grid-template-columns: 1fr;
  }

  .insumos-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .btn-agregar-insumo {
    align-self: flex-start;
  }

  .insumo-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .insumo-costo-container {
    align-self: flex-end;
  }

  .btn-nueva-receta-flotante {
    bottom: 20px;
    right: 20px;
    padding: 14px 20px;
    font-size: 0.9rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .recetas-card {
    padding: 8px;
  }

  .receta-item-compact {
    padding: 8px 10px;
    gap: 8px;
  }

  .receta-nombre {
    font-size: 0.9rem;
  }

  .badge-cantidad,
  .badge-rentabilidad {
    font-size: 0.65rem;
    padding: 2px 6px;
  }

  .detalle-item {
    font-size: 0.75rem;
  }

  .acciones-container {
    gap: 4px;
  }

  .btn-accion {
    width: 28px;
    height: 28px;
    padding: 6px;
  }

  .btn-nueva-receta-flotante {
    bottom: 15px;
    right: 15px;
    padding: 12px 18px;
    font-size: 0.8rem;
  }

  .btn-nueva-receta-flotante span {
    display: none;
  }
}
</style>
