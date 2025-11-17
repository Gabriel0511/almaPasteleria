<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <section class="principal-content">
          <h3 class="card-title1" :class="{ 'mobile-center': isMobile }">
            Gestión de Recetas
          </h3>

          <!-- Estadísticas de recetas -->
          <!-- Actualizar la sección de estadísticas -->
          <div class="estadisticas-stock">
            <div class="estadistica-item" v-if="notificacionesRecetasNoRentables.length > 0">
              <span class="estadistica-badge bajo" :class="{ active: filtroActivo === 'no-rentable' }"
                @click="aplicarFiltroNoRentables" title="Filtrar recetas no rentables">
                <i class="fas fa-exclamation-circle"></i>
                {{ notificacionesRecetasNoRentables.length }} no rentable(s)
              </span>
            </div>
            <div class="estadistica-item">
              <span class="estadistica-badge total">
                <i class="fas fa-utensils"></i>
                {{ recetasFiltradas.length }} receta(s)
              </span>
            </div>
            <div class="estadistica-item" v-if="filtroActivo || searchTerm">
              <span class="estadistica-badge limpiar-filtro" @click="limpiarFiltros">
                <i class="fas fa-times"></i>
                Limpiar filtros
              </span>
            </div>
          </div>
          <!-- Filtros de recetas -->
          <div class="filtros-derecha">
            <div class="filtro-group">
              <input type="text" v-model="searchTerm" placeholder="Buscar receta..." class="filtro-input" />
            </div>
          </div>
        </section>

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
            <div v-for="receta in recetasFiltradas" :key="receta.id" class="receta-item" :class="{
              'no-rentable': receta.precio_venta <= receta.costo_total,
              expanded: recetaDesplegada[receta.id],
            }">
              <!-- Contenedor principal compacto - ESTILO COMO STOCK -->
              <div class="receta-item-compact">
                <!-- Indicador de estado -->
                <div class="estado-indicador" :class="{
                  critico: receta.precio_venta <= receta.costo_total,
                  normal: receta.precio_venta > receta.costo_total,
                }"></div>

                <!-- Información principal -->
                <div class="info-principal" @click="toggleReceta(receta.id)">
                  <div class="info-header">
                    <h4 class="receta-nombre">{{ receta.nombre }}</h4>
                    <div class="badges-container">
                      <span class="badge-cantidad">
                        {{ (receta.insumos || []).length }} insumos
                      </span>
                      <span class="badge-rentabilidad" :class="receta.precio_venta > receta.costo_total
                        ? 'rentable'
                        : 'no-rentable'
                        ">
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

                <!-- Acciones -->
                <div class="acciones-container">
                  <button class="btn-accion btn-gestionar" @click="agregarInsumosAReceta(receta)"
                    title="Gestionar insumos">
                    <i class="fas fa-list"></i>
                  </button>
                  <button class="btn-accion btn-editar" @click="editarReceta(receta)" title="Editar receta">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn-accion btn-eliminar" @click="confirmarEliminarReceta(receta)"
                    title="Eliminar receta">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <!-- Desplegable de detalles de la receta - MEJORADO -->
              <div v-if="recetaDesplegada[receta.id]" class="receta-detalles-desplegable">
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
                        <span class="rentabilidad-valor" :class="{
                          positiva: receta.precio_venta > receta.costo_total,
                          negativa: receta.precio_venta <= receta.costo_total,
                        }">
                          ${{
                            formatDecimal(
                              receta.precio_venta - receta.costo_total
                            )
                          }}
                        </span>
                      </div>
                      <div class="rentabilidad-item">
                        <span class="rentabilidad-label">Margen:</span>
                        <span class="rentabilidad-valor" :class="{
                          positiva: receta.precio_venta > receta.costo_total,
                          negativa: receta.precio_venta <= receta.costo_total,
                        }">
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
                      <button class="btn-agregar-insumo" @click="agregarInsumosAReceta(receta)">
                        <i class="fas fa-plus"></i> Gestionar Insumos
                      </button>
                    </div>

                    <div class="insumos-list">
                      <div v-for="insumo in receta.insumos || []" :key="insumo.id" class="insumo-item">
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
                          <span class="insumo-costo" v-if="insumo.insumo.precio_unitario != null">
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
                      <div v-if="(receta.insumos || []).length === 0" class="sin-insumos">
                        <i class="fas fa-info-circle"></i>
                        <p>Esta receta no tiene insumos asignados</p>
                        <button class="btn-agregar-insumo-small" @click="agregarInsumosAReceta(receta)">
                          <i class="fas fa-plus"></i> Agregar Insumos
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Alertas de rentabilidad -->
                  <div v-if="receta.precio_venta <= receta.costo_total" class="receta-alerta alerta-no-rentable">
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
        </div>

        <!-- Botón Nueva Receta flotante - ESTILO COMO STOCK -->
        <button class="btn-nueva-receta-flotante" @click="showNuevaRecetaModal">
          <i class="fas fa-plus"></i>
          <span>Nueva Receta</span>
        </button>
      </main>
    </div>
    <!-- MODALES REFACTORIZADOS -->

    <!-- Modal para Nueva/Editar Receta -->
    <BaseModal v-model:show="showModalReceta" :title="esEdicion ? 'Editar Receta' : 'Nueva Receta'" size="medium"
      @close="closeModal">
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input v-model="formReceta.nombre" type="text" required class="form-input"
            placeholder="Nombre de la receta" />
        </div>
        <div class="form-group">
          <label>Rinde:</label>
          <input v-model="formReceta.rinde" type="number" min="1" required class="form-input"
            placeholder="Cantidad que rinde" />
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
          <input v-model="formReceta.precio_venta" type="number" step="1" min="0" required class="form-input"
            placeholder="Precio de venta" />
        </div>
      </div>

      <template #footer>
        <ModalButtons :confirm-text="esEdicion ? 'Actualizar' : 'Guardar Receta'" @cancel="closeModal"
          @confirm="guardarRecetaBasica" />
      </template>
    </BaseModal>

    <!-- Modal para Agregar/Eliminar Insumos a Receta -->
    <BaseModal v-model:show="showModalInsumos" :title="`Gestionar Insumos: ${recetaSeleccionada?.nombre || ''}`"
      size="large" @close="showModalInsumos = false">
      <div class="insumos-section">
        <h4>Agregar Nuevo Insumo:</h4>
        <div class="form-grid">
          <div class="form-group">
            <label>Insumo:</label>
            <div class="select-with-button">
              <select v-model="nuevoInsumo.insumo_id" required class="form-input" @change="actualizarUnidadNuevoInsumo">
                <option value="">Seleccione un insumo</option>
                <option v-for="item in insumosDisponibles" :key="item.id" :value="item.id">
                  {{ item.nombre }}
                </option>
              </select>
              <button type="button" class="btn-agregar-nuevo" @click="showNuevoInsumoModal = true"
                title="Agregar nuevo insumo">
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>Cantidad:</label>
            <input v-model="nuevoInsumo.cantidad" type="number" step="1" min="0" required class="form-input"
              placeholder="0.000" />
          </div>
          <div class="form-group">
            <label>Unidad de Medida:</label>
            <select v-model="nuevoInsumo.unidad_medida_id" required class="form-input">
              <option value="">Seleccione una unidad</option>
              <option v-for="unidad in unidadesMedida" :key="unidad.id" :value="unidad.id">
                {{ unidad.nombre }} ({{ unidad.abreviatura }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <button class="btn-agregar-insumo-modal" @click="agregarInsumoAReceta" :disabled="!puedeAgregarInsumo">
              <i class="fas fa-plus"></i> Agregar
            </button>
          </div>
        </div>
      </div>

      <div class="insumos-existente-section">
        <h4>
          Insumos Actuales ({{ recetaSeleccionada?.insumos?.length || 0 }}):
        </h4>
        <div v-for="insumo in recetaSeleccionada?.insumos || []" :key="insumo.id" class="insumo-existente-item">
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
                <input v-model.number="insumo.cantidadEdit" type="number" step="1" min="0" class="form-input-small"
                  placeholder="0.000" @input="formatearCantidadInput($event, insumo)" />
              </div>
              <div class="form-group">
                <label>Unidad:</label>
                <select v-model="insumo.unidad_medida_id_edit" class="form-input-small" required>
                  <option value="">Seleccione...</option>
                  <option v-for="unidad in unidadesMedida" :key="unidad.id" :value="unidad.id">
                    {{ unidad.abreviatura }} ({{ unidad.nombre }})
                  </option>
                </select>
              </div>
            </div>
          </div>
          <div class="insumo-acciones">
            <button v-if="!insumo.editando" class="btn-accion-small" @click="activarEdicionInsumo(insumo)"
              title="Editar insumo">
              <i class="fas fa-edit"></i>
            </button>
            <button v-else class="btn-accion-small btn-confirmar" @click="guardarEdicionInsumo(insumo)"
              title="Guardar cambios">
              <i class="fas fa-check"></i>
            </button>
            <button v-if="!insumo.editando" class="btn-accion-small btn-eliminar-modal"
              @click="eliminarInsumoDeReceta(recetaSeleccionada, insumo)" title="Eliminar insumo">
              <i class="fas fa-trash"></i>
            </button>
            <button v-else class="btn-accion-small btn-cancelar" @click="cancelarEdicionInsumo(insumo)"
              title="Cancelar edición">
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
        <ModalButtons :show-cancel="false" confirm-text="Cerrar" @cancel="showModalInsumos = false"
          @confirm="showModalInsumos = false" />
      </template>
    </BaseModal>

    <!-- Modal para Nuevo Insumo -->
    <BaseModal v-model:show="showNuevoInsumoModal" title="Nuevo Insumo" size="medium"
      @close="showNuevoInsumoModal = false">
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input v-model="formNuevoInsumo.nombre" type="text" required class="form-input"
            placeholder="Nombre del insumo" />
        </div>
        <div class="form-group">
          <label>Unidad de Medida:</label>
          <select v-model="formNuevoInsumo.unidad_medida_id" required class="form-input">
            <option value="">Seleccione una unidad</option>
            <option v-for="unidad in unidadesMedida" :key="unidad.id" :value="unidad.id">
              {{ unidad.nombre }} ({{ unidad.abreviatura }})
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Stock Mínimo:</label>
          <input v-model="formNuevoInsumo.stock_minimo" type="number" step="1" min="0" required class="form-input"
            placeholder="0.000" />
        </div>
        <div class="form-group">
          <label>Precio Unitario:</label>
          <input v-model="formNuevoInsumo.precio_unitario" type="number" step="1" min="0" class="form-input"
            placeholder="0.00" />
        </div>
      </div>

      <template #footer>
        <ModalButtons confirm-text="Guardar" @cancel="showNuevoInsumoModal = false" @confirm="guardarNuevoInsumo" />
      </template>
    </BaseModal>

    <!-- Modal de confirmación para eliminar receta -->
    <ConfirmModal :show="showConfirmModal" title="Confirmar Eliminación"
      :message="`¿Está seguro de que desea eliminar la receta '${recetaAEliminar?.nombre}'?`" confirm-text="Eliminar"
      @update:show="showConfirmModal = $event" @cancel="showConfirmModal = false" @confirm="eliminarReceta" />
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
import axios from "axios";

const router = useRouter();
const notificationSystem = inject("notifications");

// Variables de estado
const headerRef = ref(null);
const recetas = ref([]);
const insumosDisponibles = ref([]);
const unidadesMedida = ref([]);
const searchTerm = ref("");
const loading = ref(true);
const insumoEditando = ref(null);
const recetaDesplegada = ref({});

// Modales
const showModalReceta = ref(false);
const showModalInsumos = ref(false);
const showConfirmModal = ref(false);
const showNuevoInsumoModal = ref(false);

// Agregar variable de estado para filtro activo
const filtroActivo = ref('');

// Referencia al sidebar para controlarlo desde el header
const sidebarRef = ref(null);

// Método para alternar el sidebar desde el header
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};

// Método para limpiar filtros
const limpiarFiltros = () => {
  filtroActivo.value = '';
  searchTerm.value = '';
};

// Formularios
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

// Método para aplicar filtro de no rentables
const aplicarFiltroNoRentables = () => {
  filtroActivo.value = filtroActivo.value === 'no-rentable' ? '' : 'no-rentable';
};

// Actualizar recetasFiltradas para incluir este filtro
const recetasFiltradas = computed(() => {
  let filtered = recetas.value;

  // Filtrar por no rentables si está activo
  if (filtroActivo.value === 'no-rentable') {
    filtered = filtered.filter(receta => receta.precio_venta <= receta.costo_total);
  }

  // Filtrar por término de búsqueda
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter((item) =>
      item.nombre.toLowerCase().includes(term)
    );
  }

  // Ordenar: no rentables primero, luego alfabéticamente
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
      // Validación más robusta de rentabilidad
      const costoTotal = parseFloat(receta.costo_total) || 0;
      const precioVenta = parseFloat(receta.precio_venta) || 0;
      const esNoRentable = precioVenta <= costoTotal;

      return esNoRentable;
    })
    .filter((notif) => !notif.leida); // Solo mostrar no leídas
});

// Métodos
const handleNavigation = (route) => {
  router.push(route);
};

// Nuevo método para toggle del desplegable
const toggleReceta = (recetaId) => {
  recetaDesplegada.value = {
    ...recetaDesplegada.value,
    [recetaId]: !recetaDesplegada.value[recetaId],
  };
};

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
    // Peso
    kg: { g: 1000, mg: 1000000 },
    g: { kg: 0.001, mg: 1000 },
    mg: { kg: 0.000001, g: 0.001 },

    // Volumen
    l: { ml: 1000, cl: 100 },
    ml: { l: 0.001, cl: 0.1 },
    cl: { l: 0.01, ml: 10 },

    // Unidades (1:1 por defecto)
    unidad: { u: 1, pz: 1 },
    u: { unidad: 1, pz: 1 },
    pz: { unidad: 1, u: 1 },

    // Agregar más conversiones si es necesario
    docena: { unidad: 12, u: 12 },
    doc: { unidad: 12, u: 12 },
  };

  // Normalizar unidades
  unidadOrigen = unidadOrigen.toLowerCase();
  unidadDestino = unidadDestino.toLowerCase();

  // Buscar conversión directa
  if (conversiones[unidadOrigen] && conversiones[unidadOrigen][unidadDestino]) {
    return cantidad * conversiones[unidadOrigen][unidadDestino];
  }

  // Buscar conversión inversa
  if (
    conversiones[unidadDestino] &&
    conversiones[unidadDestino][unidadOrigen]
  ) {
    return cantidad / conversiones[unidadDestino][unidadOrigen];
  }

  // Si no encuentra conversión, mostrar advertencia y devolver cantidad original
  console.warn(
    `No se encontró conversión de ${unidadOrigen} a ${unidadDestino}`
  );
  return cantidad;
};

const marcarTodasComoLeidas = () => {
  notificacionesRecetasNoRentables.value.forEach((notif) => {
    marcarNotificacionLeida(notif.id);
  });

  // Mostrar confirmación
  notificationSystem.show({
    type: "success",
    title: "Notificaciones marcadas",
    message:
      "Todas las notificaciones de recetas no rentables fueron marcadas como leídas",
    timeout: 3000,
  });
};

// AGREGAR: Método para marcar notificación como leída
const marcarNotificacionLeida = (notificacionId) => {
  notificacionesLeidas.value.add(notificacionId);

  // Persistir en localStorage
  const leidasGuardadas = JSON.parse(
    localStorage.getItem("notificacionesLeidas") || "[]"
  );
  leidasGuardadas.push(notificacionId);
  localStorage.setItem(
    "notificacionesLeidas",
    JSON.stringify([...new Set(leidasGuardadas)])
  );

  // Actualizar contador en header
  actualizarNotificacionesRecetas();
};

// AGREGAR: Cargar notificaciones leídas al inicializar
const cargarNotificacionesLeidas = () => {
  const leidasGuardadas = JSON.parse(
    localStorage.getItem("notificacionesLeidas") || "[]"
  );
  notificacionesLeidas.value = new Set(leidasGuardadas);
};

const calcularCostoInsumo = (insumoReceta) => {
  // Validar que el objeto insumoReceta y sus propiedades existan
  if (
    !insumoReceta ||
    !insumoReceta.insumo ||
    insumoReceta.insumo.precio_unitario === null ||
    insumoReceta.insumo.precio_unitario === undefined
  ) {
    console.log(
      "❌ Datos insuficientes para calcular costo - precio_unitario:",
      insumoReceta?.insumo?.precio_unitario
    );
    return 0;
  }

  try {
    const precioUnitario = parseFloat(
      insumoReceta.insumo.precio_unitario.toString().replace(",", ".")
    );
    const cantidad = parseFloat(
      insumoReceta.cantidad.toString().replace(",", ".")
    );

    // Si no hay información de unidades, cálculo directo
    if (!insumoReceta.insumo.unidad_medida || !insumoReceta.unidad_medida) {
      const costoDirecto = precioUnitario * cantidad;
      console.log(`📊 Cálculo directo: ${costoDirecto}`);
      return costoDirecto;
    }

    const unidadInsumo =
      insumoReceta.insumo.unidad_medida.abreviatura.toLowerCase();
    const unidadReceta = insumoReceta.unidad_medida.abreviatura.toLowerCase();

    // Si las unidades son iguales, cálculo directo
    if (unidadInsumo === unidadReceta) {
      const costoDirecto = precioUnitario * cantidad;
      console.log(`📊 Cálculo mismo unidad: ${costoDirecto}`);
      return costoDirecto;
    }

    // Convertir a la unidad del insumo
    const cantidadConvertida = convertirUnidad(
      cantidad,
      unidadReceta,
      unidadInsumo
    );

    console.log(
      `🔄 Cantidad convertida: ${cantidad} ${unidadReceta} → ${cantidadConvertida} ${unidadInsumo}`
    );

    const costo = precioUnitario * cantidadConvertida;
    console.log(`📊 Costo final: ${costo}`);

    return isNaN(costo) ? 0 : costo;
  } catch (error) {
    console.error(
      "❌ Error al calcular costo del insumo:",
      error,
      insumoReceta
    );
    return 0;
  }
};

const resetFilters = () => {
  searchTerm.value = "";
};

const getInsumosSeguros = (receta) => {
  return receta?.insumos || [];
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

    // CAMBIO: Siempre establecer cantidad en 1
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

    // Validar que la cantidad sea positiva
    if (nuevoInsumo.value.cantidad <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La cantidad debe ser mayor a cero",
        timeout: 4000,
      });
      return;
    }

    // Estructura simple con IDs numéricos
    const insumoData = {
      insumo: parseInt(nuevoInsumo.value.insumo_id),
      unidad_medida: parseInt(nuevoInsumo.value.unidad_medida_id),
      cantidad: parseFloat(nuevoInsumo.value.cantidad),
    };

    console.log("Enviando datos:", insumoData);

    const response = await axios.post(
      `/api/recetas/${recetaSeleccionada.value.id}/insumos/`,
      insumoData
    );

    // Agregar el nuevo insumo a la lista local
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

    // Recalcular costos
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
    console.error("Error al agregar insumo:", error);

    let errorMessage = "Error al agregar el insumo a la receta";

    if (error.response?.data) {
      console.error("Detalles del error:", error.response.data);

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

// Modificar eliminarInsumoDeReceta para actualizar en tiempo real
const eliminarInsumoDeReceta = async (receta, insumo) => {
  try {
    await axios.delete(`/api/recetas/${receta.id}/insumos/${insumo.id}/`);

    // ACTUALIZACIÓN EN TIEMPO REAL: Eliminar de la lista local
    const insumoIndex = receta.insumos.findIndex((i) => i.id === insumo.id);
    if (insumoIndex !== -1) {
      receta.insumos.splice(insumoIndex, 1);
    }

    // AGREGAR: Notificar cambios en insumos
    await onInsumosModificados(receta);

    notificationSystem.show({
      type: "success",
      title: "Insumo eliminado",
      message: "Insumo eliminado correctamente de la receta",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al eliminar insumo:", error);
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

    // Preparar datos básicos de la receta
    const datosParaEnviar = {
      nombre: formReceta.value.nombre,
      rinde: formReceta.value.rinde,
      unidad_rinde: formReceta.value.unidad_rinde,
      precio_venta: formReceta.value.precio_venta,
      costo_unitario: 0,
      costo_total: 0,
    };

    let response;
    if (esEdicion.value) {
      response = await axios.put(
        `/api/recetas/${formReceta.value.id}/`,
        datosParaEnviar
      );
    } else {
      response = await axios.post("/api/recetas/", datosParaEnviar);
    }

    await fetchRecetas();
    closeModal();

    // Verificar rentabilidad y mostrar notificación
    const recetaGuardada = response.data;
    verificarRentabilidadYNotificar(recetaGuardada);

    notificationSystem.show({
      type: "success",
      title: esEdicion.value ? "Receta actualizada" : "Receta creada",
      message: esEdicion.value
        ? "Receta actualizada correctamente"
        : "Receta creada correctamente. Ahora puede agregarle insumos.",
      timeout: 4000,
    });

    // ✅ CORREGIDO: Solo abrir modal de insumos para NUEVAS recetas, NO para edición
    if (!esEdicion.value && response.data.id) {
      const nuevaReceta = recetas.value.find((r) => r.id === response.data.id);
      if (nuevaReceta) {
        setTimeout(() => {
          agregarInsumosAReceta(nuevaReceta);
        }, 1000);
      }
    }
  } catch (error) {
    console.error("Error al guardar receta:", error);

    if (error.response?.status === 400) {
      console.error("Datos de error:", error.response.data);

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

    // Actualizar la lista local inmediatamente sin recargar toda la data
    const index = recetas.value.findIndex(
      (item) => item.id === recetaAEliminar.value.id
    );
    if (index !== -1) {
      recetas.value.splice(index, 1);
    }

    showConfirmModal.value = false;

    // AGREGAR: Actualizar notificaciones después de eliminar
    actualizarNotificacionesRecetas();

    notificationSystem.show({
      type: "success",
      title: "Receta eliminada",
      message: "Receta eliminada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al eliminar receta:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al eliminar la receta",
      timeout: 6000,
    });
  }
};

// Agregar este método para guardar el nuevo insumo
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
      stock_actual: 0, // Empezar con stock 0
      activo: true,
    };

    const response = await axios.post("/api/insumos/crear/", datosParaEnviar);

    // Actualizar la lista de insumos disponibles
    await fetchInsumosDisponibles();

    // Seleccionar automáticamente el nuevo insumo
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
    console.error("Error al guardar insumo:", error);

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

  // Usar punto decimal en lugar de coma
  insumo.cantidadEdit = parseFloat(
    insumo.cantidad.toString().replace(",", ".")
  );

  // Guardar el ID del insumo también (necesario para la actualización)
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

    // Validar que la unidad de medida sea válida
    if (!insumo.unidad_medida_id_edit) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "Seleccione una unidad de medida válida",
        timeout: 4000,
      });
      return;
    }

    // Estructura correcta que espera el backend
    const datosActualizacion = {
      insumo: insumo.insumo.id, // Incluir el insumo (requerido)
      cantidad: parseFloat(insumo.cantidadEdit),
      unidad_medida: parseInt(insumo.unidad_medida_id_edit), // Nombre correcto del campo
    };

    console.log("Enviando datos de actualización:", datosActualizacion);

    const response = await axios.patch(
      `/api/recetas/${recetaSeleccionada.value.id}/insumos/${insumo.id}/actualizar/`,
      {
        cantidad: parseFloat(insumo.cantidadEdit),
        unidad_medida: parseInt(insumo.unidad_medida_id_edit),
      }
    );

    console.log("Respuesta del servidor:", response.data);

    // Actualizar los datos locales en tiempo real
    insumo.cantidad = parseFloat(insumo.cantidadEdit);

    // Buscar y asignar la nueva unidad de medida
    const nuevaUnidad = unidadesMedida.value.find(
      (u) => u.id === parseInt(insumo.unidad_medida_id_edit)
    );
    if (nuevaUnidad) {
      insumo.unidad_medida = nuevaUnidad;
    }

    // Desactivar modo edición
    insumo.editando = false;
    delete insumo.cantidadEdit;
    delete insumo.insumo_id_edit;
    delete insumo.unidad_medida_id_edit;
    insumoEditando.value = null;

    // Recalcular costos de la receta
    await recalcularCostosReceta();
    await onInsumosModificados(recetaSeleccionada.value);

    notificationSystem.show({
      type: "success",
      title: "Insumo actualizado",
      message: "Insumo actualizado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al actualizar insumo:", error);

    let errorMessage = "Error al actualizar el insumo";
    if (error.response?.data) {
      console.error("Detalles del error:", error.response.data);

      if (typeof error.response.data === "object") {
        const errors = [];
        for (const key in error.response.data) {
          if (Array.isArray(error.response.data[key])) {
            errors.push(...error.response.data[key]);
          } else if (typeof error.response.data[key] === "object") {
            // Si es un objeto anidado, extraer sus valores
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

// Agrega esta función para manejar el formato de números
const formatearCantidadInput = (event, insumo) => {
  const input = event.target;
  let value = input.value;

  // Reemplazar coma por punto
  value = value.replace(",", ".");

  // Validar que sea un número válido
  if (!isNaN(value) && value !== "") {
    insumo.cantidadEdit = parseFloat(value);
  }
};

// Método para recalcular costos en tiempo real
const recalcularCostosReceta = async () => {
  if (!recetaSeleccionada.value) return;

  try {
    // Recalcular costo total de la receta
    let costoTotal = 0;

    if (recetaSeleccionada.value.insumos) {
      recetaSeleccionada.value.insumos.forEach((insumo) => {
        costoTotal += calcularCostoInsumo(insumo);
      });
    }

    // Actualizar localmente
    recetaSeleccionada.value.costo_total = costoTotal;

    // También actualizar en la lista principal de recetas
    const recetaIndex = recetas.value.findIndex(
      (r) => r.id === recetaSeleccionada.value.id
    );
    if (recetaIndex !== -1) {
      recetas.value[recetaIndex].costo_total = costoTotal;

      // También actualizar el costo unitario si el rinde es mayor a 0
      if (recetas.value[recetaIndex].rinde > 0) {
        recetas.value[recetaIndex].costo_unitario =
          costoTotal / recetas.value[recetaIndex].rinde;
      }
    }

    console.log("Costos recalculados:", costoTotal);
  } catch (error) {
    console.error("Error al recalcular costos:", error);
  }
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

// Agregar método para resetear el formulario de nuevo insumo
const resetFormNuevoInsumo = () => {
  formNuevoInsumo.value = {
    nombre: "",
    unidad_medida_id: "",
    stock_minimo: 0,
    precio_unitario: null,
  };
};

// Funciones para cargar datos
const fetchRecetas = async () => {
  try {
    loading.value = true;
    const response = await axios.get("/api/recetas/");

    recetas.value = response.data.map((receta) => {
      console.log(`🔍 Receta "${receta.nombre}":`, {
        costo_total_backend: receta.costo_total,
        precio_venta: receta.precio_venta,
        insumos_count: receta.insumos?.length || 0,
        rentable: receta.precio_venta > receta.costo_total,
      });

      // Si insumos es undefined, inicializarlo como array vacío
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
    console.error("Error en fetchRecetas:", err);
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
  } catch (err) {
    console.error("Error en fetchInsumosDisponibles:", err);
  }
};

const fetchUnidadesMedida = async () => {
  try {
    const response = await axios.get("/api/unidades-medida/");
    unidadesMedida.value = response.data;
  } catch (err) {
    console.error("Error en fetchUnidadesMedida:", err);
  }
};

// AGREGAR: Método para actualizar notificaciones en el Header
const actualizarNotificacionesRecetas = () => {
  if (headerRef.value && headerRef.value.actualizarNotificaciones) {
    headerRef.value.actualizarNotificaciones();
  }

  // Forzar recálculo de notificaciones locales
  setTimeout(() => {
    // Esto activará el computed property nuevamente
  }, 100);
};

// Método para emitir notificación cuando se crea/edita una receta no rentable
const verificarRentabilidadYNotificar = (receta) => {
  // Validación más precisa
  const costoTotal = parseFloat(receta.costo_total) || 0;
  const precioVenta = parseFloat(receta.precio_venta) || 0;
  const margen = precioVenta - costoTotal;

  if (margen <= 0) {
    const notificacionId = `receta-no-rentable-${receta.id}`;

    // Solo mostrar si no está marcada como leída
    if (!notificacionesLeidas.value.has(notificacionId)) {
      notificationSystem.show({
        type: "warning",
        title: `${receta.nombre} NO es rentable.`,
        message: `• Pérdida de $${formatDecimal(Math.abs(margen))}`,
        timeout: 4000,
      });
    }

    // Actualizar notificaciones en el header
    actualizarNotificacionesRecetas();
  } else if (margen > 0 && margen < costoTotal * 0.1) {
    // Notificación para márgenes bajos (menos del 10%)
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

// AGREGAR: Método para limpiar notificaciones de recetas eliminadas
const limpiarNotificacionesObsoletas = () => {
  const leidasGuardadas = JSON.parse(
    localStorage.getItem("notificacionesLeidas") || "[]"
  );
  const idsRecetasActuales = recetas.value.map(
    (r) => `receta-no-rentable-${r.id}`
  );

  // Mantener solo las notificaciones de recetas que aún existen
  const leidasFiltradas = leidasGuardadas.filter((id) =>
    idsRecetasActuales.some((recetaId) => id === recetaId)
  );

  localStorage.setItem("notificacionesLeidas", JSON.stringify(leidasFiltradas));
  notificacionesLeidas.value = new Set(leidasFiltradas);
};

const onInsumosModificados = async (receta) => {
  // Recalcular costos
  await recalcularCostosReceta();

  // Verificar si la rentabilidad cambió
  const recetaActualizada = recetas.value.find((r) => r.id === receta.id);
  if (recetaActualizada) {
    verificarRentabilidadYNotificar(recetaActualizada);
  }
};

// Cargar datos al montar el componente
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  // Cargar notificaciones leídas primero
  cargarNotificacionesLeidas();

  // Cargar datos
  Promise.all([
    fetchRecetas(),
    fetchInsumosDisponibles(),
    fetchUnidadesMedida(),
  ])
    .then(() => {
      // Limpiar notificaciones obsoletas
      limpiarNotificacionesObsoletas();

      // Actualizar notificaciones
      actualizarNotificacionesRecetas();

      // Verificar rentabilidad de todas las recetas
      recetas.value.forEach((receta) => {
        verificarRentabilidadYNotificar(receta);
      });
    })
    .catch((error) => {
      console.error("Error cargando datos:", error);
      loading.value = false;
      if (error.response?.status === 401) {
        logout();
      }
    });
});
</script>

<style scoped>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css");

/* ----------------------------- CARD DE RECETAS - MISMO ESTILO QUE STOCK ----------------------------- */
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

/* Contenedor compacto - MISMO ESTILO QUE STOCK */
.receta-item-compact {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
}

/* Indicador de estado - MISMO ESTILO QUE STOCK */
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

/* Información principal - MISMO ESTILO QUE STOCK */
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

/* Acciones - MISMO ESTILO QUE STOCK */
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

/* ----------------------------- DESPLEGABLE DE DETALLES - MEJORADO ----------------------------- */
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

/* Información de rentabilidad */
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

/* ----------------------------- SECCIÓN DE INSUMOS - MEJORADA ----------------------------- */
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

/* Nuevos estilos específicos para el modal de insumos */
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

.sin-insumos {
  text-align: center;
  padding: 30px;
  color: #6c757d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px dashed #dee2e6;
}

.sin-insumos i {
  margin-right: 8px;
  color: var(--color-primary);
}

/* ----------------------------- ALERTAS DE RECETA ----------------------------- */
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

/* ----------------------------- BOTÓN FLOTANTE NUEVA RECETA - MISMO ESTILO QUE STOCK ----------------------------- */
.btn-nueva-receta-flotante {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
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
  box-shadow: 0 6px 20px rgba(123, 90, 80, 0.3);
  z-index: 100;
  font-size: 1rem;
}

.btn-nueva-receta-flotante:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(123, 90, 80, 0.4);
  color: #212529;
}

/* ----------------------------- ESTADOS DE CARGA Y VACÍO - MISMO ESTILO QUE STOCK ----------------------------- */
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

/* ==============================
   RESPONSIVE DESIGN - CONSISTENTE CON STOCK
   ============================== */

/* Tablets */
@media (max-width: 1024px) {
  .recetas-card {
    padding: 15px;
  }
}

/* Tablets pequeñas y móviles grandes */
@media (max-width: 768px) {
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
}

/* Móviles pequeños */
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

/* Pantallas muy pequeñas */
@media (max-width: 360px) {
  .receta-item-compact {
    padding: 6px 8px;
    gap: 6px;
  }

  .receta-nombre {
    font-size: 0.8rem;
  }

  .acciones-container {
    gap: 2px;
  }

  .btn-accion {
    width: 26px;
    height: 26px;
    padding: 5px;
  }

  .btn-accion i {
    font-size: 0.8rem;
  }
}

/* Mejoras de usabilidad táctil */
@media (hover: none) and (pointer: coarse) {
  .receta-item:hover {
    transform: none;
  }

  .btn-accion {
    min-height: 44px;
    min-width: 44px;
  }

  .btn-nueva-receta-flotante {
    min-height: 44px;
  }
}

/* Utilidades */
.ml-2 {
  margin-left: 8px;
}

.cursor-pointer {
  cursor: pointer;
}

.animacion-pulsante {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.7);
  }

  70% {
    box-shadow: 0 0 0 6px rgba(255, 193, 7, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0);
  }
}

/* Estilos para el nuevo botón flotante */
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
}
/* Estilos para los badges de estadísticas */
.estadisticas-stock {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.estadistica-item {
  display: flex;
}

.estadistica-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  user-select: none;
}

.estadistica-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.estadistica-badge.active {
  border: 2px solid currentColor;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.estadistica-badge.bajo {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

.estadistica-badge.total {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
}

.estadistica-badge.limpiar-filtro {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}
</style>
