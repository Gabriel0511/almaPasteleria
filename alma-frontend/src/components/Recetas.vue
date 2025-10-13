<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <section class="recetas-content">
          <h3 class="card-title1">Gestión de Recetas</h3>

          <!-- AGREGAR: Contador de recetas no rentables -->
          <div class="estadisticas-rapidas">
            <div
              class="estadistica-item"
              v-if="notificacionesRecetasNoRentables.length > 0"
            >
              <span class="estadistica-badge warning">
                <i class="fas fa-exclamation-circle"></i>
                {{ notificacionesRecetasNoRentables.length }} no rentable(s)
              </span>
            </div>
            <div class="estadistica-item">
              <span class="estadistica-badge info">
                <i class="fas fa-utensils"></i>
                {{ recetasFiltradas.length }} receta(s)
              </span>
            </div>
          </div>

          <!-- Filtros de recetas -->
          <div class="filtros-derecha">
            <div class="filtro-group">
              <input
                type="text"
                v-model="searchTerm"
                placeholder="Buscar receta..."
                class="filtro-input"
              />
            </div>
          </div>
        </section>

        <!-- Card principal de recetas -->
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
              v-for="receta in recetasFiltradas"
              :key="receta.id"
              class="receta-item"
              :class="{
                expanded: recetaDesplegada[receta.id],
              }"
            >
              <!-- Contenedor principal del header -->
              <div class="receta-item-main">
                <!-- Header que ocupa todo el ancho -->
                <!-- En la sección del receta-item, modificar el receta-header-full -->
                <div
                  class="receta-header-full cursor-pointer"
                  @click="toggleReceta(receta.id)"
                >
                  <div class="receta-header-content">
                    <div class="receta-info-main">
                      <div class="receta-titulo">
                        <span class="receta-nombre">{{ receta.nombre }}</span>
                        <span class="receta-badge"
                          >{{ (receta.insumos || []).length }} insumos</span
                        >
                      </div>
                      <div class="receta-datos-compact">
                        <div class="dato-grupo">
                          <i class="fas fa-utensils"></i>
                          <span class="receta-rinde">
                            Rinde {{ receta.rinde }} {{ receta.unidad_rinde }}
                          </span>
                        </div>
                        <div class="dato-grupo">
                          <i class="fas fa-dollar-sign"></i>
                          <span class="receta-costo">
                            ${{ formatDecimal(receta.costo_total) }}
                          </span>
                        </div>
                        <div class="dato-grupo">
                          <i class="fas fa-tag"></i>
                          <span class="receta-precio">
                            ${{ formatDecimal(receta.precio_venta) }}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div class="receta-header-right" @click.stop>
                      <span
                        class="receta-estado-badge"
                        :class="{
                          rentable: receta.precio_venta > receta.costo_total,
                          noRentable: receta.precio_venta <= receta.costo_total,
                        }"
                      >
                        <i
                          class="fas"
                          :class="{
                            'fa-check-circle':
                              receta.precio_venta > receta.costo_total,
                            'fa-exclamation-circle':
                              receta.precio_venta <= receta.costo_total,
                          }"
                        ></i>
                        {{
                          receta.precio_venta > receta.costo_total
                            ? "Rentable"
                            : "No Rentable"
                        }}
                      </span>

                      <div class="receta-acciones">
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
                        <button
                          class="btn-accion btn-desplegable"
                          @click="toggleReceta(receta.id)"
                          :title="
                            recetaDesplegada[receta.id]
                              ? 'Ocultar detalles'
                              : 'Mostrar detalles'
                          "
                        >
                          <i
                            class="fas"
                            :class="
                              recetaDesplegada[receta.id]
                                ? 'fa-chevron-up'
                                : 'fa-chevron-down'
                            "
                          ></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Desplegable que aparece en la parte inferior del receta-item -->
                <div
                  v-if="recetaDesplegada[receta.id]"
                  class="receta-detalles-container"
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
                          <span class="rentabilidad-label"
                            >Precio de Venta:</span
                          >
                          <span class="rentabilidad-valor">
                            ${{ formatDecimal(receta.precio_venta) }}
                          </span>
                        </div>
                        <div class="rentabilidad-item">
                          <span class="rentabilidad-label">Ganancia:</span>
                          <span
                            class="rentabilidad-valor"
                            :class="{
                              positiva:
                                receta.precio_venta > receta.costo_total,
                              negativa:
                                receta.precio_venta <= receta.costo_total,
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
                              positiva:
                                receta.precio_venta > receta.costo_total,
                              negativa:
                                receta.precio_venta <= receta.costo_total,
                            }"
                          >
                            {{
                              receta.costo_total > 0
                                ? formatDecimal(
                                    ((receta.precio_venta -
                                      receta.costo_total) /
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
                      </div>

                      <div class="insumos-list">
                        <div
                          v-for="insumo in receta.insumos || []"
                          :key="insumo.id"
                          class="insumo-item"
                        >
                          <div class="insumo-info">
                            <span class="insumo-nombre">
                              <i
                                class="fas fa-circle"
                                style="font-size: 6px; color: #7b5a50"
                              ></i>
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
                                }}/{{
                                  insumo.insumo.unidad_medida.abreviatura
                                }})
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

                    <!-- Acciones rápidas -->
                    <div class="receta-acciones-rapidas">
                      <button
                        class="btn-editar-insumos"
                        @click="agregarInsumosAReceta(receta)"
                      >
                        <i class="fas fa-edit"></i> Gestionar Insumos
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón Nueva Receta flotante -->
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
            step="0.01"
            min="0.01"
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
                  {{ item.nombre }} (Stock:
                  {{ formatDecimal(item.stock_actual) }}
                  {{ item.unidad_medida.abreviatura }})
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
              step="0.001"
              min="0.001"
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
                  step="0.001"
                  min="0.001"
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
              class="btn-accion-small btn-eliminar"
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
              v-for="unidad in unidadesPermitidas"
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
            step="0.001"
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
            step="0.01"
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

// Referencia al sidebar para controlarlo desde el header
const sidebarRef = ref(null);

// Método para alternar el sidebar desde el header
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
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

// Computed properties
const recetasFiltradas = computed(() => {
  let filtered = recetas.value;

  // Filtrar por término de búsqueda
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter((item) =>
      item.nombre.toLowerCase().includes(term)
    );
  }

  return filtered;
});

const puedeAgregarInsumo = computed(() => {
  return (
    nuevoInsumo.value.insumo_id &&
    nuevoInsumo.value.cantidad > 0 &&
    nuevoInsumo.value.unidad_medida_id
  );
});

// Agrega esta computed property que solo permite kg, litros y unidades
const unidadesPermitidas = computed(() => {
  const abreviaturasPermitidas = ["kg", "l", "L", "lt", "un", "ud", "u"];
  const nombresPermitidos = [
    "kilogramo",
    "kilogramos",
    "litro",
    "litros",
    "unidad",
    "unidades",
  ];

  return unidadesMedida.value.filter(
    (unidad) =>
      abreviaturasPermitidas.includes(unidad.abreviatura.toLowerCase()) ||
      nombresPermitidos.includes(unidad.nombre.toLowerCase())
  );
});

const formNuevoInsumo = ref({
  nombre: "",
  unidad_medida_id: "",
  stock_minimo: 0,
  precio_unitario: null,
});

const notificacionesRecetasNoRentables = computed(() => {
  return recetas.value
    .filter((receta) => receta.precio_venta <= receta.costo_total)
    .map((receta) => ({
      id: `receta-no-rentable-${receta.id}`,
      type: "warning",
      title: "Receta No Rentable",
      message: `${receta.nombre} no es rentable (Costo: $${formatDecimal(
        receta.costo_total
      )} > Venta: $${formatDecimal(receta.precio_venta)})`,
      timestamp: new Date(),
      receta: receta,
    }));
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

const calcularCostoInsumo = (insumoReceta) => {
  console.log("🔍 Calculando costo para insumo:", insumoReceta);

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

    console.log(
      `💰 Datos cálculo: precio=${precioUnitario}, cantidad=${cantidad}`
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

    console.log(`📏 Unidades: insumo=${unidadInsumo}, receta=${unidadReceta}`);

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
    // Establecer la unidad de medida por defecto del insumo
    nuevoInsumo.value.unidad_medida_id = insumo.unidad_medida.id;

    // Establecer una cantidad por defecto pequeña
    if (!nuevoInsumo.value.cantidad || nuevoInsumo.value.cantidad === 0) {
      // Dependiendo de la unidad, establecer un valor por defecto razonable
      const unidad = insumo.unidad_medida.abreviatura.toLowerCase();
      if (unidad === "kg" || unidad === "l") {
        nuevoInsumo.value.cantidad = 0.1; // 100g o 100ml por defecto
      } else if (unidad === "g" || unidad === "ml") {
        nuevoInsumo.value.cantidad = 100; // 100g o 100ml por defecto
      } else {
        nuevoInsumo.value.cantidad = 1; // 1 unidad por defecto
      }
    }
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

    console.log("Respuesta del servidor:", response.data);

    // ACTUALIZACIÓN EN TIEMPO REAL: Agregar el nuevo insumo a la lista local
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
      timeout: 8000,
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

    // AGREGAR: Verificar rentabilidad y mostrar notificación
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

    // Si es una receta nueva, abrir modal para agregar insumos
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
        timeout: 8000,
      });
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al guardar la receta",
        timeout: 6000,
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

    console.log("📦 Datos recibidos del backend:", response.data);

    // SOLO usar los costos que vienen del backend, NO recalcular en frontend
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

      // ⚠️ IMPORTANTE: Usar SOLO los costos del backend
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
};

// AGREGAR: Método para emitir notificación cuando se crea/edita una receta no rentable
const verificarRentabilidadYNotificar = (receta) => {
  if (receta.precio_venta <= receta.costo_total) {
    notificationSystem.show({
      type: "warning",
      title: "Receta No Rentable",
      message: `La receta "${receta.nombre}" no es rentable. El precio de venta no cubre los costos.`,
      timeout: 6000,
    });

    // Actualizar notificaciones en el header
    actualizarNotificacionesRecetas();
  }
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

  // Cargar datos
  Promise.all([
    fetchRecetas(),
    fetchInsumosDisponibles(),
    fetchUnidadesMedida(),
  ])
    .then(() => {
      // AGREGAR: Actualizar notificaciones después de cargar recetas
      actualizarNotificacionesRecetas();
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

/* ----------------------------- CONTENIDO PRINCIPAL ----------------------------- */
.recetas-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 20px;
  padding: 0 10px;
}

.card-title1 {
  color: var(--color-primary);
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 2px 4px rgba(123, 90, 80, 0.1);
}

/* ----------------------------- FILTROS ----------------------------- */
.filtros-derecha {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filtro-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filtro-input {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  height: 46px;
  transition: all 0.3s ease;
  background: white;
  min-width: 200px;
}

.filtro-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(123, 90, 80, 0.1);
  transform: translateY(-1px);
}

/* ----------------------------- BOTONES GENERALES ----------------------------- */
.botones-acciones {
  display: flex;
  gap: 10px;
}

.btn-nueva-receta {
  background: linear-gradient(135deg, var(--color-success), #218838);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 12px 20px;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
  font-size: 0.9rem;
}

.btn-nueva-receta:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
}

/* ----------------------------- CARD DE RECETAS ----------------------------- */
.recetas-card {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(123, 90, 80, 0.1);
  padding: 25px;
  margin: 0 auto;
  border: 1px solid rgba(123, 90, 80, 0.1);
}

.recetas-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.receta-item {
  position: relative;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.receta-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, var(--color-primary), #f1d0cb);
  opacity: 0.8;
}

.receta-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(123, 90, 80, 0.15);
  border-color: var(--color-primary);
}

.receta-item.expanded {
  padding-bottom: 0;
}

.receta-item-main {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.receta-header-full {
  width: 100%;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  padding: 15px 20px;
  flex-shrink: 0;
}

.receta-header-full:hover {
  background-color: rgba(123, 90, 80, 0.05);
}

.receta-header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  gap: 20px;
}

.receta-info-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.receta-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.receta-nombre {
  font-weight: 700;
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0;
}

.receta-badge {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.receta-datos-compact {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.receta-datos-compact .dato-grupo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
  background: rgba(123, 90, 80, 0.05);
  padding: 6px 12px;
  border-radius: 6px;
}

.receta-datos-compact .dato-grupo i {
  color: var(--color-primary);
  width: 14px;
  text-align: center;
  font-size: 0.8rem;
}

.receta-header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

/* ----------------------------- BOTONES DE ACCIÓN ----------------------------- */
.receta-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.receta-estado-badge {
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.receta-estado-badge.rentable {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.receta-estado-badge.noRentable {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

.btn-accion {
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.btn-editar {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.btn-editar:hover {
  background: linear-gradient(135deg, #2980b9, #21618c);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-eliminar {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.btn-eliminar:hover {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.btn-desplegable {
  background: linear-gradient(135deg, #95a5a6, #7f8c8d);
  color: white;
}

.btn-desplegable:hover {
  background: linear-gradient(135deg, #7f8c8d, #6c7a7d);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(149, 165, 166, 0.3);
}

/* ----------------------------- DESPLEGABLE DE DETALLES ----------------------------- */
.receta-detalles-container {
  width: 100%;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-top: 1px solid #dee2e6;
  margin-top: 0;
  flex-shrink: 0;
}

.detalles-content {
  padding: 20px;
  border-radius: 0 0 12px 12px;
}

.receta-rentabilidad-info h4 {
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  color: var(--color-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.receta-rentabilidad-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.rentabilidad-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.rentabilidad-label {
  font-weight: 500;
  color: #6c757d;
}

.rentabilidad-valor {
  font-weight: 600;
}

.rentabilidad-valor.positiva {
  color: #28a745;
}

.rentabilidad-valor.negativa {
  color: #dc3545;
}

/* ----------------------------- SECCIÓN DE INSUMOS ----------------------------- */
.receta-insumos-section {
  margin-bottom: 20px;
}

.insumos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 15px;
}

.insumos-header h4 {
  margin: 0;
  font-size: 1.1rem;
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
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  box-shadow: 0 2px 6px rgba(40, 167, 69, 0.2);
}

.btn-agregar-insumo:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
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
  padding: 12px 16px;
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
  font-size: 0.9rem;
  font-weight: 500;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 8px;
}

.insumo-cantidad {
  font-size: 0.85rem;
  color: #6c757d;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
}

.insumo-costo-container {
  min-width: 80px;
  text-align: right;
}

.insumo-costo {
  font-size: 0.85rem;
  color: var(--color-success);
  font-weight: 600;
  background: rgba(40, 167, 69, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

/* ----------------------------- ALERTAS DE RECETA ----------------------------- */
.receta-alerta {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.alerta-no-rentable {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  color: #856404;
  border: 1px solid #ffeaa7;
}

/* ----------------------------- ACCIONES RÁPIDAS ----------------------------- */
.receta-acciones-rapidas {
  text-align: right;
}

.btn-editar-insumos {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  font-size: 0.85rem;
  box-shadow: 0 2px 6px rgba(23, 162, 184, 0.2);
}

.btn-editar-insumos:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
}

/* ----------------------------- BOTÓN FLOTANTE NUEVA RECETA ----------------------------- */
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
  background: linear-gradient(135deg, #9c7a6d, var(--color-primary));
}

/* ----------------------------- ESTADOS ----------------------------- */
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
  padding: 40px;
  color: #6c757d;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.sin-insumos i {
  font-size: 2rem;
  color: #bdc3c7;
}

.sin-insumos p {
  margin: 0;
}

.btn-agregar-insumo-small {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.btn-agregar-insumo-small:hover {
  background: #9c7a6d;
  transform: translateY(-1px);
}

/* Añadir al final de la sección de estilos */
.cursor-pointer {
  cursor: pointer;
}

.receta-header-full:hover {
  background-color: rgba(123, 90, 80, 0.05);
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

/* Indicador visual de que es clickeable */
.receta-header-full::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 12px;
  pointer-events: none;
  transition: box-shadow 0.2s ease;
}

.receta-header-full:hover::after {
  box-shadow: inset 0 0 0 2px rgba(123, 90, 80, 0.1);
}

/* Mejorar la transición del desplegable */
.receta-detalles-container {
  transition: all 0.3s ease;
  max-height: 0;
  overflow: hidden;
}

.receta-item.expanded .receta-detalles-container {
  max-height: 1000px;
}

.alertas-rapidas {
  margin-bottom: 20px;
  padding: 0 10px;
}

.alerta-contenido {
  flex: 1;
}

.alerta-contenido strong {
  display: block;
  margin-bottom: 4px;
  font-size: 1rem;
}

.alerta-contenido p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

.btn-alerta-cerrar {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.btn-alerta-cerrar:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

/* AGREGAR: Estilos para estadísticas rápidas */
.estadisticas-rapidas {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.estadistica-item {
  display: flex;
  align-items: center;
}

.estadistica-badge {
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.estadistica-badge.warning {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

.estadistica-badge.info {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

/* ----------------------------- MEJORAS RESPONSIVE ----------------------------- */

/* Para pantallas medianas (tablets) */
@media (max-width: 1024px) {
  .recetas-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .filtros-derecha {
    width: 100%;
    justify-content: space-between;
  }

  .receta-rentabilidad-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* Para tablets pequeñas y móviles grandes */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 10px 10px 10px 10px;
  }

  .recetas-card {
    padding: 15px;
    max-height: calc(100vh - 150px);
  }

  .receta-header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .receta-header-right {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .receta-datos-compact {
    flex-direction: column;
    gap: 8px;
  }

  .receta-datos-compact .dato-grupo {
    justify-content: flex-start;
  }

  .detalles-content {
    padding: 15px;
  }

  .insumos-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .btn-agregar-insumo {
    align-self: flex-start;
  }

  .receta-rentabilidad-grid {
    grid-template-columns: 1fr;
  }

  .btn-nueva-receta-flotante {
    bottom: 20px;
    right: 20px;
    padding: 14px 20px;
    font-size: 0.9rem;
  }

  .alertas-rapidas {
    margin-bottom: 15px;
  }

  .estadisticas-rapidas {
    justify-content: center;
    width: 100%;
    margin-top: 10px;
  }
}

/* Para móviles */
@media (max-width: 480px) {
  .main-content {
    margin-left: 0;
    padding: 10px 10px 10px 10px;
  }

  .receta-header-full {
    padding: 12px 15px;
  }

  .receta-header-right {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .receta-acciones {
    align-self: center;
  }

  .receta-nombre {
    font-size: 1.1rem;
  }

  .insumo-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .insumo-costo-container {
    align-self: flex-end;
  }

  .card-title1 {
    font-size: 1.5rem;
  }

  .filtro-input {
    min-width: 100%;
  }

  .receta-titulo {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .btn-accion {
    width: 36px;
    height: 36px;
    padding: 8px;
  }

  .btn-nueva-receta-flotante {
    bottom: 15px;
    right: 15px;
    padding: 12px 18px;
    font-size: 0.85rem;
  }

  .btn-nueva-receta-flotante span {
    display: none; /* Ocultar texto en móviles muy pequeños */
  }

  .btn-nueva-receta-flotante i {
    margin-right: 0;
  }
}

/* Para móviles muy pequeños */
@media (max-width: 360px) {
  .main-content {
    margin-left: 0;
    padding: 10px 10px 10px 10px;
  }

  .recetas-card {
    padding: 10px;
  }

  .receta-header-full {
    padding: 10px 12px;
  }

  .receta-nombre {
    font-size: 1rem;
  }

  .receta-badge {
    font-size: 0.7rem;
    padding: 3px 8px;
  }

  .receta-datos-compact .dato-grupo {
    font-size: 0.8rem;
    padding: 4px 8px;
  }

  .btn-accion {
    width: 32px;
    height: 32px;
    padding: 6px;
  }

  .receta-estado-badge {
    font-size: 0.7rem;
    padding: 6px 10px;
  }

  .detalles-content {
    padding: 12px;
  }
}
</style>
