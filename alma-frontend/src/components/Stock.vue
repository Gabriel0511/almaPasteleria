<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <PageHeader
          title="Gestión de Insumos"
          :show-total="true"
          :total="estadisticasStock.total"
          :stats="stockStats"
          :filters="stockFilters"
          :active-filter-type="filtroActivo"
          @stat-click="handleStockStatClick"
          @filter-change="handleStockFilterChange"
          @clear-filters="limpiarFiltrosStock"
        />

        <!-- Card principal de stock -->
        <div class="card stock-card">
          <div v-if="loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i> Cargando stock...
          </div>

          <div v-else-if="stockFiltrado.length === 0" class="empty-state">
            <i class="fas fa-search"></i>
            <p>No hay insumos que coincidan con los filtros seleccionados</p>
          </div>

          <div v-else>
            <!-- Lista de stock con paginación -->
            <div class="stock-list">
              <div
                v-for="item in stockPaginado"
                :key="item.id"
                class="stock-item"
                :class="{
                  'stock-critico': item.cantidad <= item.stock_minimo * 0.5,
                  'bajo-stock':
                    item.bajoStock && item.cantidad > item.stock_minimo * 0.5,
                  expanded: stockDesplegado[item.id],
                }"
              >
                <!-- Contenedor principal compacto -->
                <div class="stock-item-compact">
                  <!-- Indicador de estado -->
                  <div
                    class="estado-indicador"
                    :class="{
                      critico: item.cantidad <= item.stock_minimo * 0.5,
                      bajo:
                        item.bajoStock &&
                        item.cantidad > item.stock_minimo * 0.5,
                      normal: !item.bajoStock,
                    }"
                  ></div>

                  <!-- Información principal -->
                  <div class="info-principal">
                    <div class="info-header">
                      <h4 class="nombre-insumo">{{ item.nombre }}</h4>
                      <div class="badges-container">
                        <span class="badge-categoria">{{
                          item.categoria
                        }}</span>
                        <span class="badge-proveedor">{{
                          item.proveedor
                        }}</span>
                      </div>
                    </div>

                    <div class="info-stock">
                      <div class="stock-actual">
                        <span class="cantidad">{{
                          formatDecimal(item.cantidad)
                        }}</span>
                        <span class="unidad">{{ item.unidad }}</span>
                      </div>
                      <div class="stock-minimo">
                        <span class="label"><b>Mín:</b></span>
                        <span class="valor"
                          >{{ formatDecimal(item.stock_minimo) }}
                          {{ item.unidad }}
                          <span style="margin-left: 10px"
                            ><b>Precio por {{ item.unidad }}:</b> ${{
                              item.precio_unitario
                            }}</span
                          >
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Acciones -->
                  <div class="acciones-container">
                    <button
                      class="btn-accion btn-reposicion-rapida"
                      @click="reponerStockRapido(item)"
                      title="Nueva compra"
                    >
                      <i class="fas fa-shopping-cart"></i>
                    </button>
                    <!-- Botón Registrar Pérdida -->
                    <button
                      class="btn-accion btn-perdida"
                      @click="registrarPerdidaRapida(item)"
                      title="Registrar pérdida"
                    >
                      <i class="fas fa-minus-circle"></i>
                    </button>
                    <button
                      class="btn-accion btn-editar"
                      @click="editarInsumo(item)"
                      title="Editar insumo"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button
                      class="btn-accion btn-eliminar"
                      @click="confirmarEliminarInsumo(item)"
                      title="Eliminar insumo"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Controles de paginación -->
            <div class="pagination-controls" v-if="totalPaginas > 1">
              <div class="pagination-info">
                Mostrando {{ inicioPagina }}-{{ finPagina }} de
                {{ stockFiltrado.length }} insumos
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
        </div>

        <!-- Botón Nuevo Insumo flotante -->
        <button class="btn-nueva-compra-flotante" @click="showNuevoInsumoModal">
          <i class="fas fa-plus"></i>
          <span>Nuevo Insumo</span>
        </button>
      </main>
    </div>

    <!-- MODALES REFACTORIZADOS -->

    <!-- Modal para Nuevo/Editar Insumo -->
    <BaseModal
      v-model:show="showModalInsumo"
      :title="esEdicion ? 'Editar Insumo' : 'Nuevo Insumo'"
      size="large"
      @close="closeModal"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input
            v-model="formInsumo.nombre"
            type="text"
            required
            class="form-input"
            placeholder="Nombre del insumo"
          />
        </div>

        <div class="form-group">
          <label>Categoría:</label>
          <div class="select-with-button">
            <select
              v-model="formInsumo.categoria_id"
              required
              class="form-input"
            >
              <option value="">Seleccione una categoría</option>
              <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                {{ cat.nombre }}
              </option>
            </select>
            <button
              type="button"
              class="btn-agregar"
              @click="showNuevaCategoriaModal = true"
              title="Agregar nueva categoría"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Cantidad:</label>
          <input
            v-model="formInsumo.stockActual"
            type="number"
            step="0.001"
            min="0"
            required
            class="form-input"
            placeholder="0.000"
            @input="validarCantidad"
          />
        </div>

        <div class="form-group">
          <label>Unidad de Medida:</label>
          <select
            v-model="formInsumo.unidad_medida_id"
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
            v-model="formInsumo.stock_minimo"
            type="number"
            step="1"
            min="0"
            required
            class="form-input"
            placeholder="0.000"
          />
        </div>
      </div>

      <template #footer>
        <ModalButtons
          :confirm-text="esEdicion ? 'Actualizar' : 'Guardar'"
          @cancel="closeModal"
          @confirm="guardarInsumo"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nueva Compra -->
    <BaseModal
      v-model:show="showModalCompra"
      :title="esReposicionRapida ? 'Nueva Compra' : 'Nueva Compra'"
      size="large"
      @close="cerrarModalCompra"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Insumo:</label>

          <!-- MODO REPOSICIÓN RÁPIDA: Mostrar insumo fijo -->
          <div
            class="insumo-fijo"
            v-if="esReposicionRapida && insumoReposicionRapida"
          >
            <div class="insumo-fijo-nombre">
              <div class="insumo-fijo-header">
                <i class="fas fa-lock"></i>
                <strong>{{ insumoReposicionRapida.nombre }}</strong>
              </div>
              <div class="insumo-fijo-stock-info">
                <span class="stock-actual-info">
                  Stock actual:
                  {{ formatDecimal(insumoReposicionRapida.cantidad) }}
                  {{ insumoReposicionRapida.unidad }}
                </span>
                <span class="stock-minimo-info">
                  Stock mínimo:
                  {{ formatDecimal(insumoReposicionRapida.stock_minimo) }}
                  {{ insumoReposicionRapida.unidad }}
                </span>
              </div>
            </div>
            <div class="insumo-fijo-categoria">
              {{ insumoReposicionRapida.categoria }}
            </div>
          </div>

          <!-- MODO NORMAL: Selección de insumo -->
          <div v-else class="form-group">
            <input
              type="text"
              v-model="busquedaInsumo"
              @input="filtrarInsumos"
              placeholder="Buscar insumo..."
              class="form-input"
            />
            <select
              v-model="formCompra.insumo_id"
              @change="actualizarUnidadMedida"
              required
              class="form-input"
              size="5"
              style="margin-top: 8px"
            >
              <option value="">Seleccione un insumo</option>
              <option
                v-for="insumo in insumosFiltrados"
                :key="insumo.id"
                :value="insumo.id"
              >
                {{ insumo.nombre }}
                (Stock: {{ formatDecimal(insumo.stock_actual) }} | Mín:
                {{ formatDecimal(insumo.stock_minimo) }}
                {{ insumo.unidad_medida?.abreviatura }})
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Cantidad:</label>
          <input
            v-model="formCompra.cantidad"
            type="number"
            step="1"
            min="0"
            required
            class="form-input"
            placeholder="0.000"
            @input="validarCantidad"
          />
        </div>

        <div class="form-group">
          <label>Unidad de Medida:</label>
          <input
            :value="unidadCompra"
            type="text"
            disabled
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Precio Total:</label>
          <input
            v-model="formCompra.precio_total"
            type="number"
            step="0.01"
            min="0"
            required
            class="form-input"
            placeholder="0.00"
            @input="calcularPrecioUnitario"
          />
        </div>

        <div class="form-group">
          <label>Precio por {{ unidadCompra }}:</label>
          <input
            :value="formCompra.precio_unitario"
            type="number"
            step="0.01"
            disabled
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Proveedor:</label>
          <div class="select-with-button">
            <select
              v-model="formCompra.proveedor_id"
              required
              class="form-input"
            >
              <option value="">Seleccione un proveedor</option>
              <option
                v-for="prov in proveedores"
                :key="prov.id"
                :value="prov.id"
              >
                {{ prov.nombre }}
              </option>
            </select>
            <button
              type="button"
              class="btn-agregar"
              @click="showNuevoProveedorModal = true"
              title="Agregar nuevo proveedor"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>
      </div>

      <template #footer>
        <ModalButtons
          :confirm-text="
            esReposicionRapida ? 'Confirmar Reposición' : 'Registrar Compra'
          "
          @cancel="cerrarModalCompra"
          @confirm="registrarCompra"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nuevo Proveedor -->
    <BaseModal
      v-model:show="showNuevoProveedorModal"
      title="Nuevo Proveedor"
      size="medium"
      @close="showNuevoProveedorModal = false"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input
            v-model="formProveedor.nombre"
            type="text"
            required
            class="form-input"
            placeholder="Nombre del proveedor"
          />
        </div>

        <div class="form-group">
          <label>Contacto:</label>
          <input
            v-model="formProveedor.contacto"
            type="text"
            class="form-input"
            placeholder="Persona de contacto"
          />
        </div>

        <div class="form-group">
          <label>Teléfono:</label>
          <input
            v-model="formProveedor.telefono"
            type="text"
            class="form-input"
            placeholder="Teléfono"
          />
        </div>

        <div class="form-group">
          <label>Email:</label>
          <input
            v-model="formProveedor.email"
            type="email"
            class="form-input"
            placeholder="Email"
          />
        </div>
      </div>

      <template #footer>
        <ModalButtons
          confirm-text="Guardar"
          @cancel="showNuevoProveedorModal = false"
          @confirm="guardarProveedor"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nueva Categoría -->
    <BaseModal
      v-model:show="showNuevaCategoriaModal"
      title="Nueva Categoría"
      size="small"
      @close="showNuevaCategoriaModal = false"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input
            v-model="formCategoria.nombre"
            type="text"
            required
            class="form-input"
            placeholder="Nombre de la categoría"
          />
        </div>

        <div class="form-group full-width">
          <label>Descripción:</label>
          <textarea
            v-model="formCategoria.descripcion"
            class="form-input"
            rows="3"
            placeholder="Descripción de la categoría"
          ></textarea>
        </div>
      </div>

      <template #footer>
        <ModalButtons
          confirm-text="Guardar"
          @cancel="showNuevaCategoriaModal = false"
          @confirm="guardarCategoria"
        />
      </template>
    </BaseModal>

    <!-- Modal de confirmación para eliminar insumo -->
    <ConfirmModal
      :show="showConfirmModal"
      title="Confirmar Eliminación"
      :message="`¿Está seguro de que desea eliminar el insumo '${insumoAEliminar?.nombre}'?`"
      confirm-text="Eliminar"
      @update:show="showConfirmModal = $event"
      @cancel="showConfirmModal = false"
      @confirm="eliminarInsumo"
    />

    <!-- Modal para Registrar Pérdida -->
    <BaseModal
      v-model:show="showRegistrarPerdidaModal"
      :title="esPerdidaRapida ? 'Registrar Pérdida' : 'Registrar Pérdida'"
      size="medium"
      @close="cerrarModalPerdida"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Insumo:</label>

          <!-- MODO PÉRDIDA RÁPIDA: Mostrar insumo fijo -->
          <div
            class="insumo-fijo"
            v-if="esPerdidaRapida && insumoPerdidaRapida"
          >
            <div class="insumo-fijo-nombre">
              <div class="insumo-fijo-header">
                <i class="fas fa-lock"></i>
                <strong>{{ insumoPerdidaRapida.nombre }}</strong>
              </div>
              <div class="insumo-fijo-stock-info">
                <span class="stock-actual-info">
                  Stock actual:
                  {{ formatDecimal(insumoPerdidaRapida.cantidad) }}
                  {{ insumoPerdidaRapida.unidad }}
                </span>
                <span class="stock-minimo-info">
                  Stock mínimo:
                  {{ formatDecimal(insumoPerdidaRapida.stock_minimo) }}
                  {{ insumoPerdidaRapida.unidad }}
                </span>
              </div>
            </div>
            <div class="insumo-fijo-categoria">
              {{ insumoPerdidaRapida.categoria }}
            </div>
          </div>

          <!-- MODO NORMAL: Selección de insumo -->
          <select
            v-else
            v-model="formPerdida.insumo_id"
            required
            class="form-input"
          >
            <option value="">Seleccione un insumo</option>
            <option
              v-for="insumo in insumos"
              :key="insumo.id"
              :value="insumo.id"
            >
              {{ insumo.nombre }}
              (Stock: {{ formatDecimal(insumo.stock_actual) }}
              {{ insumo.unidad_medida?.abreviatura }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Cantidad a descontar:</label>
          <input
            v-model="formPerdida.cantidad"
            type="number"
            step="0.001"
            min="0.001"
            required
            class="form-input"
            placeholder="0.000"
            @input="validarCantidadPerdida"
          />
        </div>

        <div class="form-group">
          <label>Motivo:</label>
          <select v-model="formPerdida.motivo" required class="form-input">
            <option value="">Seleccione un motivo</option>
            <option value="deterioro">Deterioro</option>
            <option value="vencimiento">Vencimiento</option>
            <option value="rotura">Rotura</option>
            <option value="error">Error en registro</option>
            <option value="uso_interno">Uso interno</option>
            <option value="otro">Otro</option>
          </select>
        </div>

        <div class="form-group full-width">
          <label>Observaciones:</label>
          <textarea
            v-model="formPerdida.observaciones"
            class="form-input"
            rows="3"
            placeholder="Observaciones adicionales..."
          ></textarea>
        </div>
      </div>

      <template #footer>
        <ModalButtons
          confirm-text="Registrar Pérdida"
          @cancel="cerrarModalPerdida"
          @confirm="registrarPerdida"
        />
      </template>
    </BaseModal>

    <!-- Modal para reactivar insumo desactivado -->
    <BaseModal
      v-model:show="showReactivarModal"
      title="Insumo Desactivado Encontrado"
      size="medium"
      @close="cancelarReactivacion"
    >
      <div class="reactivar-content">
        <div class="warning-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <p>
          Ya existe un insumo llamado
          <strong>"{{ insumoDesactivado?.nombre }}"</strong>
          pero está desactivado.
        </p>
        <p>¿Deseas reactivarlo con los datos ingresados?</p>

        <div class="insumo-info">
          <div class="info-item">
            <span class="label">Categoría:</span>
            <span class="value">
              {{
                categorias.find((c) => c.id === formInsumo.categoria_id)
                  ?.nombre || "Sin categoría"
              }}
            </span>
          </div>
          <div class="info-item">
            <span class="label">Unidad de medida:</span>
            <span class="value">
              {{
                unidadesPermitidas.find(
                  (u) => u.id === formInsumo.unidad_medida_id
                )?.nombre || "Sin unidad"
              }}
            </span>
          </div>
          <div class="info-item">
            <span class="label">Stock mínimo:</span>
            <span class="value">{{ formInsumo.stock_minimo }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="reactivar-buttons">
          <button
            class="btn-cancelar"
            @click="cancelarReactivacion"
            :disabled="reactivando"
          >
            Cancelar
          </button>
          <button
            class="btn-reactivar"
            @click="reactivarInsumo"
            :disabled="reactivando"
          >
            <i v-if="reactivando" class="fas fa-spinner fa-spin"></i>
            {{ reactivando ? "Reactivando..." : "Reactivar Insumo" }}
          </button>
        </div>
      </template>
    </BaseModal>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted, onUnmounted, watch, inject } from "vue";
import { useRoute } from "vue-router";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import BaseModal from "./Modals/BaseModal.vue";
import ModalButtons from "./Modals/ModalButtons.vue";
import ConfirmModal from "./Modals/ConfirmModal.vue";
import PageHeader from "./PageHeader.vue";
import axios from "axios";

const router = useRouter();
const route = useRoute();
const notificationSystem = inject("notifications");

// Variables de estado
const headerRef = ref(null);
const stock = ref([]);
const insumos = ref([]);
const categorias = ref([]);
const unidadesMedida = ref([]);
const proveedores = ref([]);
const categoriaSeleccionada = ref("");
const proveedorSeleccionado = ref("");
const searchTerm = ref("");
const loading = ref(true);
const stockDesplegado = ref({});
const busquedaInsumo = ref("");
const insumosFiltrados = ref([]);
const filtroActivo = ref(""); // 'critico', 'bajo', 'normal', 'total'
// Variables de estado - Agrega estas después de las variables existentes
const showRegistrarPerdidaModal = ref(false);
const esPerdidaRapida = ref(false);
const insumoPerdidaRapida = ref(null);

const formPerdida = ref({
  insumo_id: "",
  cantidad: 0,
  motivo: "",
  observaciones: "",
});

// Variables para manejo de insumo desactivado
const showReactivarModal = ref(false);
const insumoDesactivado = ref(null);
const reactivando = ref(false);

// Variables de paginación
const paginaActual = ref(1);
const itemsPorPagina = ref(10);

// Modales
const showModalInsumo = ref(false);
const showModalCompra = ref(false);
const showNuevoProveedorModal = ref(false);
const showConfirmModal = ref(false);
const showNuevaCategoriaModal = ref(false);

// Agregar después de las otras variables
const esReposicionRapida = ref(false);
const insumoReposicionRapida = ref(null);

// Formularios
const formInsumo = ref({
  id: null,
  nombre: "",
  categoria_id: "",
  unidad_medida_id: "",
  stock_minimo: 0,
  precio_unitario: null,
  proveedor_id: null,
});

const formCompra = ref({
  insumo_id: "",
  cantidad: 0,
  precio_total: 0,
  precio_unitario: 0,
  proveedor_id: "",
});

const formProveedor = ref({
  nombre: "",
  telefono: "",
  email: "",
});

// Agregar formulario para categoría
const formCategoria = ref({
  nombre: "",
  descripcion: "",
});

const esEdicion = ref(false);
const insumoAEliminar = ref(null);
const unidadCompra = ref("");

// Referencia al sidebar para controlarlo desde el header
const sidebarRef = ref(null);

// Método para alternar el sidebar desde el header
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};

// Método para registrar pérdida rápida
const registrarPerdidaRapida = (item) => {
  esPerdidaRapida.value = true;
  insumoPerdidaRapida.value = item;
  formPerdida.value.insumo_id = item.id;
  formPerdida.value.cantidad = 0;
  formPerdida.value.motivo = "";
  formPerdida.value.observaciones = "";
  showRegistrarPerdidaModal.value = true;
};

// Método para registrar pérdida
const registrarPerdida = async () => {
  try {
    // Validaciones
    if (parseFloat(formPerdida.value.cantidad) <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La cantidad debe ser mayor a 0",
        timeout: 4000,
      });
      return;
    }

    if (!formPerdida.value.motivo) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "Debe seleccionar un motivo",
        timeout: 4000,
      });
      return;
    }

    // Preparar datos para enviar
    const datosPerdida = {
      insumo: formPerdida.value.insumo_id,
      cantidad: parseFloat(formPerdida.value.cantidad),
      motivo: formPerdida.value.motivo,
      observaciones: formPerdida.value.observaciones,
      fecha: new Date().toISOString().split("T")[0], // Fecha actual
    };

    // Enviar al backend
    const response = await axios.post("/api/perdidas/", datosPerdida);

    // Actualizar datos locales
    await fetchStock();
    await fetchInsumos();

    // Cerrar modal y resetear
    showRegistrarPerdidaModal.value = false;
    resetFormPerdida();

    notificationSystem.show({
      type: "success",
      title: "Pérdida registrada",
      message: "La pérdida se registró correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al registrar pérdida:", error);

    let mensajeError = "No se pudo registrar la pérdida";
    if (error.response?.data?.error) {
      mensajeError = error.response.data.error;
    }

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: mensajeError,
      timeout: 6000,
    });
  }
};

// Método para cerrar modal de pérdida
const cerrarModalPerdida = () => {
  showRegistrarPerdidaModal.value = false;
  // Resetear modo pérdida rápida
  esPerdidaRapida.value = false;
  insumoPerdidaRapida.value = null;
  resetFormPerdida();
};

// Método para validar cantidad de pérdida
const validarCantidadPerdida = () => {
  // Solo validar que no sea negativo, pero permitir 0
  if (parseFloat(formPerdida.value.cantidad) < 0) {
    formPerdida.value.cantidad = 0;
  }
};

// Método para resetear formulario de pérdida
const resetFormPerdida = () => {
  formPerdida.value = {
    insumo_id: "",
    cantidad: 0,
    motivo: "",
    observaciones: "",
  };
};
// Computed properties

// Computed properties para el PageHeader
const categoriasStock = computed(() => {
  const categoriasUnicas = [
    ...new Set(stock.value.map((item) => item.categoria)),
  ];
  return categoriasUnicas.filter((cat) => cat && cat !== "Sin categoría");
});

// Agregar proveedores únicos del stock
const proveedoresStock = computed(() => {
  const proveedoresUnicos = [
    ...new Set(stock.value.map((item) => item.proveedor)),
  ];
  return proveedoresUnicos.filter((prov) => prov && prov !== "Sin Proveedor");
});

const stockStats = computed(() => {
  const { critico, bajo, normal, total } = estadisticasStock.value;

  return [
    {
      type: "critico",
      label: `${critico} Crítico`,
      compactLabel: `${critico} Crítico`,
      icon: "fas fa-exclamation-triangle",
      tooltip: "Ver insumos con stock crítico",
      value: critico,
    },
    {
      type: "bajo",
      label: `${bajo} Bajo`,
      compactLabel: `${bajo} Bajo`,
      icon: "fas fa-exclamation-circle",
      tooltip: "Ver insumos con stock bajo",
      value: bajo,
    },
    {
      type: "normal",
      label: `${normal} Normal`,
      compactLabel: `${normal} Normal`,
      icon: "fas fa-check-circle",
      tooltip: "Ver insumos con stock normal",
      value: normal,
    },
    {
      type: "total",
      label: `${total} Total`,
      compactLabel: `${total} Total`,
      icon: "fas fa-boxes",
      tooltip: "Ver todos los insumos",
      value: total,
    },
  ];
});

const stockFilters = computed(() => [
  {
    type: "text",
    placeholder: "Buscar insumo...",
    value: searchTerm.value,
    autocomplete: "off",
  },
  {
    type: "select",
    placeholder: "Categoría",
    value: categoriaSeleccionada.value,
    defaultOption: "Todas las categorías",
    options: categoriasStock.value.map((cat) => ({ label: cat, value: cat })),
  },
  {
    type: "select",
    placeholder: "Proveedor",
    value: proveedorSeleccionado.value,
    defaultOption: "Todos los proveedores",
    options: proveedoresStock.value.map((prov) => ({
      label: prov,
      value: prov,
    })),
  },
]);

// Métodos para manejar eventos del PageHeader
const handleStockStatClick = (stat) => {
  aplicarFiltro(stat.type);
};

const handleStockFilterChange = ({ filter, value }) => {
  if (filter.placeholder?.includes("Buscar")) {
    searchTerm.value = value;
  } else if (filter.placeholder?.includes("Categoría")) {
    categoriaSeleccionada.value = value;
  } else if (filter.placeholder?.includes("Proveedor")) {
    proveedorSeleccionado.value = value;
  }
  resetearPaginacion();
};

const limpiarFiltrosStock = () => {
  limpiarFiltros();
};

// Computed properties para paginación

const stockPaginado = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina.value;
  const fin = inicio + itemsPorPagina.value;
  return stockFiltrado.value.slice(inicio, fin);
});

const totalPaginas = computed(() => {
  return Math.ceil(stockFiltrado.value.length / itemsPorPagina.value);
});

const inicioPagina = computed(() => {
  return (paginaActual.value - 1) * itemsPorPagina.value + 1;
});

const finPagina = computed(() => {
  const fin = paginaActual.value * itemsPorPagina.value;
  return Math.min(fin, stockFiltrado.value.length);
});

const paginasVisibles = computed(() => {
  const total = totalPaginas.value;
  const actual = paginaActual.value;
  const paginas = [];

  if (total <= 7) {
    // Mostrar todas las páginas
    for (let i = 1; i <= total; i++) {
      paginas.push(i);
    }
  } else {
    // Mostrar páginas con puntos suspensivos
    if (actual <= 4) {
      // Primeras páginas
      for (let i = 1; i <= 5; i++) {
        paginas.push(i);
      }
      paginas.push(total);
    } else if (actual >= total - 3) {
      // Últimas páginas
      paginas.push(1);
      for (let i = total - 4; i <= total; i++) {
        paginas.push(i);
      }
    } else {
      // Páginas intermedias
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

const stockFiltrado = computed(() => {
  let filtered = stock.value;

  // Filtrar por categoría
  if (categoriaSeleccionada.value) {
    filtered = filtered.filter(
      (item) => item.categoria === categoriaSeleccionada.value
    );
  }

  //Filtrar por proveedor
  if (proveedorSeleccionado.value) {
    filtered = filtered.filter(
      (item) => item.proveedor === proveedorSeleccionado.value
    );
  }

  // Filtrar por término de búsqueda
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter((item) =>
      item.nombre.toLowerCase().includes(term)
    );
  }

  // Aplicar filtro por nivel de stock si está activo
  if (filtroActivo.value) {
    switch (filtroActivo.value) {
      case "critico":
        filtered = filtered.filter(
          (item) => item.cantidad <= item.stock_minimo * 0.5
        );
        break;
      case "bajo":
        filtered = filtered.filter(
          (item) => item.bajoStock && item.cantidad > item.stock_minimo * 0.5
        );
        break;
      case "normal":
        filtered = filtered.filter((item) => !item.bajoStock);
        break;
      case "total":
        // No aplicar filtro adicional, mostrar todos
        break;
    }
  }
  // Ordenar: stock crítico primero, luego bajo, luego normal
  return filtered.sort((a, b) => {
    const aCritico = a.cantidad <= a.stock_minimo * 0.5;
    const bCritico = b.cantidad <= b.stock_minimo * 0.5;

    if (aCritico && !bCritico) return -1;
    if (!aCritico && bCritico) return 1;
    if (a.bajoStock && !b.bajoStock) return -1;
    if (!a.bajoStock && b.bajoStock) return 1;
    return 0;
  });
});

// Computed properties para notificaciones de stock
const notificacionesStockCritico = computed(() => {
  return stock.value
    .filter((item) => item.cantidad <= item.stock_minimo * 0.5)
    .map((item) => ({
      id: `stock-critico-${item.id}`,
      type: "critical",
      title: "Stock Crítico",
      message: `${item.nombre} está en nivel crítico (${formatDecimal(
        item.cantidad
      )}/${formatDecimal(item.stock_minimo)} ${item.unidad})`,
      timestamp: new Date(),
      read: false,
      item: item,
    }));
});

const notificacionesStockBajo = computed(() => {
  return stock.value
    .filter((item) => item.bajoStock && item.cantidad > item.stock_minimo * 0.5)
    .map((item) => ({
      id: `stock-bajo-${item.id}`,
      type: "warning",
      title: "Stock Bajo",
      message: `${item.nombre} está por debajo del mínimo (${formatDecimal(
        item.cantidad
      )}/${formatDecimal(item.stock_minimo)} ${item.unidad})`,
      timestamp: new Date(),
      read: false,
      item: item,
    }));
});

const todasLasNotificacionesStock = computed(() => {
  return [
    ...notificacionesStockCritico.value,
    ...notificacionesStockBajo.value,
  ];
});

const estadisticasStock = computed(() => {
  const critico = notificacionesStockCritico.value.length;
  const bajo = notificacionesStockBajo.value.length;
  const total = stock.value.length;
  const normal = total - critico - bajo;

  return {
    critico,
    bajo,
    normal,
    total,
  };
});

// AGREGAR: Métodos para manejar filtros
const aplicarFiltro = (tipo) => {
  // Si es "total", no hacer nada (no aplicar filtro)
  if (tipo === "total") {
    return; // Salir sin hacer cambios
  }

  // Si ya está activo el mismo filtro, desactivarlo
  if (filtroActivo.value === tipo) {
    filtroActivo.value = "";
  } else {
    filtroActivo.value = tipo;
  }
};

const limpiarFiltros = () => {
  filtroActivo.value = "";
  categoriaSeleccionada.value = "";
  proveedorSeleccionado.value = "";
  searchTerm.value = "";
  resetearPaginacion();
};

// 🔍 MÉTODO PARA FILTRAR INSUMOS EN MODAL DE COMPRA
const filtrarInsumos = () => {
  if (!busquedaInsumo.value) {
    insumosFiltrados.value = insumos.value;
    return;
  }

  const termino = busquedaInsumo.value.toLowerCase().trim();
  insumosFiltrados.value = insumos.value.filter((insumo) =>
    insumo.nombre.toLowerCase().includes(termino)
  );
};

// Métodos de paginación
const cambiarPagina = (pagina) => {
  if (pagina >= 1 && pagina <= totalPaginas.value) {
    paginaActual.value = pagina;
    // Scroll suave hacia arriba
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};

const resetearPaginacion = () => {
  paginaActual.value = 1;
};

// Métodos
const handleNavigation = (route) => {
  router.push(route);
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

  // Convertir coma a punto para poder parsear correctamente
  const numericValue =
    typeof value === "string" ? parseFloat(value.replace(",", ".")) : value;

  return Number(numericValue).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

// Método para guardar categoría
const guardarCategoria = async () => {
  try {
    if (!formCategoria.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre de la categoría es requerido",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.post(
      "/api/categorias/crear/",
      formCategoria.value
    );

    // Actualizar lista de categorías
    await fetchCategorias();

    // Seleccionar la nueva categoría automáticamente
    formInsumo.value.categoria_id = response.data.id;

    showNuevaCategoriaModal.value = false;
    resetFormCategoria();

    notificationSystem.show({
      type: "success",
      title: "Categoría creada",
      message: "Categoría creada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar categoría:", error);
    if (error.response?.status === 400 && error.response?.data?.error) {
      notificationSystem.show({
        type: "error",
        title: "Error al crear categoría",
        message: error.response.data.error,
        timeout: 6000,
      });
      resetFormCategoria();
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al guardar la categoría",
        timeout: 6000,
      });
      resetFormCategoria();
    }
  }
};

// Resetear formulario de categoría
const resetFormCategoria = () => {
  formCategoria.value = {
    nombre: "",
    descripcion: "",
  };
};

// Función auxiliar para parsear números con comas
const parsearNumero = (valor) => {
  if (valor === null || valor === undefined) return 0;
  if (typeof valor === "number") return valor;
  if (typeof valor === "string") {
    return parseFloat(valor.replace(",", "."));
  }
  return parseFloat(valor);
};

const resetFilters = () => {
  categoriaSeleccionada.value = "";
  searchTerm.value = "";
};

const showNuevoInsumoModal = () => {
  esEdicion.value = false;
  resetFormInsumo();
  showModalInsumo.value = true;
};

const showNuevaCompraModal = () => {
  resetFormCompra();
  showModalCompra.value = true;
};

const editarInsumo = (insumo) => {
  esEdicion.value = true;

  // Parsear los valores numéricos para mostrarlos correctamente en el formulario
  formInsumo.value = {
    id: insumo.id,
    nombre: insumo.nombre,
    categoria_id:
      categorias.value.find((c) => c.nombre === insumo.categoria)?.id || "",
    unidad_medida_id:
      unidadesMedida.value.find((u) => u.abreviatura === insumo.unidad)?.id ||
      "",
    stock_minimo: parsearNumero(insumo.stock_minimo),
    precio_unitario: parsearNumero(insumo.precio_unitario),
    proveedor_id: insumo.proveedor_id,
    stockActual: parsearNumero(insumo.cantidad),
  };
  showModalInsumo.value = true;
};

const confirmarEliminarInsumo = (insumo) => {
  insumoAEliminar.value = insumo;
  showConfirmModal.value = true;
};

const eliminarInsumo = async () => {
  try {
    await axios.delete(`/api/insumos/${insumoAEliminar.value.id}/eliminar/`);

    // Actualizar la lista local inmediatamente sin recargar toda la data
    const index = stock.value.findIndex(
      (item) => item.id === insumoAEliminar.value.id
    );
    if (index !== -1) {
      stock.value.splice(index, 1);
    }

    showConfirmModal.value = false;

    actualizarNotificacionesStock();

    notificationSystem.show({
      type: "success",
      title: "Insumo eliminado",
      message: "Insumo eliminado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al eliminar insumo:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al eliminar el insumo",
      timeout: 6000,
    });
  }
};

const guardarInsumo = async () => {
  try {
    const nombreNuevo = formInsumo.value.nombre;

    const datosParaEnviar = {
      nombre: nombreNuevo,
      categoria_id: formInsumo.value.categoria_id,
      unidad_medida_id: formInsumo.value.unidad_medida_id,
      stock_minimo: formInsumo.value.stock_minimo,
    };

    // 👉 SOLO para creación
    if (!esEdicion.value) {
      datosParaEnviar.stock_actual = 0;
    }

    console.log("📤 Payload enviado al servidor:", datosParaEnviar);

    let response;

    // -----------------------------
    // ✔ EDICIÓN
    // -----------------------------
    if (esEdicion.value) {
      datosParaEnviar.stock_actual = formInsumo.value.stockActual;

      response = await axios.patch(
        `/api/insumos/${formInsumo.value.id}/actualizar-parcial/`,
        datosParaEnviar
      );

      notificationSystem.show({
        type: "success",
        title: "Insumo editado",
        message: "Los cambios se guardaron correctamente",
        timeout: 3000,
      });

      closeModal();
      await fetchStock();
      await fetchInsumos();
      return;
    }

    // -----------------------------
    // ✔ CREACIÓN - Manejo de insumo desactivado
    // -----------------------------
    try {
      response = await axios.post("/api/insumos/crear/", datosParaEnviar);
    } catch (error) {
      // DEBUG: Mostrar toda la respuesta del error
      console.log("🔍🔍🔍 DEBUG COMPLETO DEL ERROR:");
      console.log("Status:", error.response?.status);
      console.log("Data:", error.response?.data);
      console.log("Error completo:", error);

      // Manejar el caso de insumo desactivado
      if (error.response?.data?.error === "insumo_desactivado") {
        console.log("✅ BACKEND CORRECTO - Detectó insumo desactivado");
        insumoDesactivado.value = error.response.data;
        showReactivarModal.value = true;
        return;
      }
      // Manejar el caso de insumo activo (nombre duplicado)
      else if (
        error.response?.data?.error &&
        error.response.data.error.includes("Ya existe un insumo")
      ) {
        console.log("❌ BACKEND - Insumo activo con mismo nombre");
        notificationSystem.show({
          type: "error",
          title: "Error",
          message: error.response.data.error,
          timeout: 4000,
        });
        return;
      }
      // Otros errores
      else {
        console.log("❌ ERROR DESCONOCIDO");
        notificationSystem.show({
          type: "error",
          title: "Error",
          message:
            error.response?.data?.error || "No se pudo guardar el insumo",
          timeout: 4000,
        });
        return;
      }
    }

    console.log("📥 Respuesta del servidor:", response.data);

    const nuevoID = response.data?.id;

    await fetchStock();
    await fetchInsumos();

    closeModal();

    notificationSystem.show({
      type: "success",
      title: "Insumo creado",
      message: "Insumo creado correctamente",
      timeout: 4000,
    });

    let nuevoInsumoCompleto = null;

    if (nuevoID) {
      nuevoInsumoCompleto = stock.value.find((i) => i.id === nuevoID);
    }

    if (!nuevoInsumoCompleto) {
      nuevoInsumoCompleto = stock.value.find(
        (i) => i.nombre?.toLowerCase() === nombreNuevo.toLowerCase()
      );
    }

    console.log("🔍 Insumo creado:", nuevoInsumoCompleto);

    if (nuevoInsumoCompleto) {
      setTimeout(() => {
        reponerStockRapido(nuevoInsumoCompleto);
      }, 300);
    }
  } catch (error) {
    console.error("❌ ERROR COMPLETO NO MANEJADO:", error);

    // Este catch solo debería ejecutarse para errores no manejados
    notificationSystem.show({
      type: "error",
      title: "Error inesperado",
      message: "Ocurrió un error inesperado al guardar el insumo",
      timeout: 4000,
    });
  }
};

const reactivarInsumo = async () => {
  try {
    reactivando.value = true;

    const response = await axios.post(
      `/api/insumos/${insumoDesactivado.value.insumo_id}/reactivar/`,
      {
        nombre: formInsumo.value.nombre,
        categoria_id: formInsumo.value.categoria_id,
        unidad_medida_id: formInsumo.value.unidad_medida_id,
        stock_minimo: formInsumo.value.stock_minimo,
        stock_actual: 0,
      }
    );

    notificationSystem.show({
      type: "success",
      title: "Insumo reactivado",
      message: "El insumo ha sido reactivado exitosamente",
      timeout: 4000,
    });

    // Cerrar modales y actualizar datos
    showReactivarModal.value = false;
    showModalInsumo.value = false;

    await fetchStock();
    await fetchInsumos();

    // Opcional: Abrir modal de compra para el insumo reactivado
    const insumoReactivado = stock.value.find(
      (i) => i.id === insumoDesactivado.value.insumo_id
    );

    if (insumoReactivado) {
      setTimeout(() => {
        reponerStockRapido(insumoReactivado);
      }, 300);
    }
  } catch (error) {
    console.error("Error al reactivar insumo:", error);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "No se pudo reactivar el insumo",
      timeout: 4000,
    });
  } finally {
    reactivando.value = false;
    insumoDesactivado.value = null;
  }
};

const cancelarReactivacion = () => {
  showReactivarModal.value = false;
  insumoDesactivado.value = null;
  // Mantener el modal de insumo abierto para que el usuario pueda cambiar el nombre
};

const registrarCompra = async () => {
  try {
    // Validar que la cantidad sea mayor a 0
    if (parseFloat(formCompra.value.cantidad) <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La cantidad debe ser mayor a 0",
        timeout: 4000,
      });
      return;
    }

    const insumo = insumos.value.find(
      (i) => i.id === parseInt(formCompra.value.insumo_id)
    );

    if (!insumo) {
      throw new Error("Insumo no encontrado");
    }

    // Convertir valores con coma a número
    const parsearNumeroConComa = (valor) => {
      if (typeof valor === "string") {
        return parseFloat(valor.replace(",", "."));
      }
      return valor;
    };

    const stockActual = parsearNumeroConComa(insumo.stock_actual);
    const cantidadComprada = parseFloat(formCompra.value.cantidad);

    // Suma precisa de decimales
    const nuevoStock = (stockActual * 1000 + cantidadComprada * 1000) / 1000;

    const datosActualizacion = {
      stock_actual: nuevoStock.toFixed(3).replace(".", ","),
    };

    // Si también quieres actualizar el precio unitario
    if (formCompra.value.precio_unitario) {
      datosActualizacion.precio_unitario = formCompra.value.precio_unitario
        .toString()
        .replace(".", ",");
    }

    if (formCompra.value.proveedor_id) {
      datosActualizacion.proveedor_id = formCompra.value.proveedor_id;
    }

    // Usa PATCH para actualización parcial
    const response = await axios.patch(
      `/api/insumos/${formCompra.value.insumo_id}/actualizar-parcial/`,
      datosActualizacion
    );
    // Refrescar tanto stock como insumos
    await fetchStock();
    await fetchInsumos();

    const itemActualizado = stock.value.find(
      (item) => item.id === parseInt(formCompra.value.insumo_id)
    );
    if (itemActualizado) {
      verificarStockYNotificar(itemActualizado, "reposicion");
    }

    closeModal();

    notificationSystem.show({
      type: "success",
      title: esReposicionRapida.value
        ? "Reposición registrada"
        : "Compra registrada",
      message: esReposicionRapida.value
        ? "Reposición registrada correctamente"
        : "Compra registrada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error completo al registrar compra:", error);
    console.error("Response data:", error.response?.data);
    console.error("Response status:", error.response?.status);

    notificationSystem.show({
      type: "error",
      title: "Error al registrar compra",
      message: error.response?.data?.message || error.message,
      timeout: 6000,
    });
  }
};

const guardarProveedor = async () => {
  try {
    const response = await axios.post(
      "/api/proveedores/crear/",
      formProveedor.value
    );
    await fetchProveedores();
    showNuevoProveedorModal.value = false;
    resetFormProveedor();

    notificationSystem.show({
      type: "success",
      title: "Proveedor creado",
      message: "Proveedor creado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar proveedor:", error);
    if (error.response?.status === 400 && error.response?.data?.error) {
      notificationSystem.show({
        type: "error",
        title: "Error al crear proveedor",
        message: error.response.data.error,
        timeout: 6000,
      });
      resetFormProveedor();
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al guardar el proveedor",
        timeout: 6000,
      });
      resetFormProveedor();
    }
  }
};

const actualizarUnidadMedida = () => {
  // Si estamos en modo reposición rápida, usar el insumo fijo
  if (esReposicionRapida.value && insumoReposicionRapida.value) {
    unidadCompra.value = insumoReposicionRapida.value.unidad;
    return;
  }

  // Modo normal: buscar en la lista de insumos
  const insumo = insumos.value.find(
    (i) => i.id === parseInt(formCompra.value.insumo_id)
  );
  if (insumo && insumo.unidad_medida) {
    unidadCompra.value = insumo.unidad_medida.abreviatura;
  } else {
    unidadCompra.value = "";
  }
};

const calcularPrecioUnitario = () => {
  if (formCompra.value.cantidad > 0 && formCompra.value.precio_total > 0) {
    const precioTotal = parseFloat(formCompra.value.precio_total);
    const cantidad = parseFloat(formCompra.value.cantidad);
    formCompra.value.precio_unitario = (precioTotal / cantidad).toFixed(2);
  }
};

const closeModal = () => {
  showModalInsumo.value = false;
  showModalCompra.value = false;
  showNuevoProveedorModal.value = false;
  showNuevaCategoriaModal.value = false;
  resetForms();
};

const resetFormInsumo = () => {
  formInsumo.value = {
    id: null,
    nombre: "",
    categoria_id: "",
    unidad_medida_id: "",
    stock_minimo: 0,
    precio_unitario: null,
    proveedor_id: null,
    stockActual: 0,
  };
};

const resetFormCompra = () => {
  formCompra.value = {
    insumo_id: "",
    cantidad: 0,
    precio_total: 0,
    precio_unitario: 0,
    proveedor_id: "",
  };
  unidadCompra.value = "";
  // Remover las variables de búsqueda que ya no usamos
  esReposicionRapida.value = false;
  insumoReposicionRapida.value = null;
};

const resetFormProveedor = () => {
  formProveedor.value = {
    nombre: "",
    telefono: "",
    email: "",
  };
};

const resetForms = () => {
  resetFormInsumo();
  resetFormCompra();
  resetFormProveedor();
  resetFormPerdida();
  esEdicion.value = false;
};

// Funciones para cargar datos
const fetchStock = async () => {
  try {
    loading.value = true;
    console.log("Fetching stock...");
    const response = await axios.get("/api/insumos/");
    console.log("Respuesta del servidor:", response.data);

    stock.value = response.data.insumos
      .map((insumo) => ({
        id: insumo.id,
        nombre: insumo.nombre,
        cantidad: parsearNumero(insumo.stock_actual),
        unidad: insumo.unidad_medida?.abreviatura || "N/A",
        bajoStock: insumo.necesita_reposicion,
        categoria: insumo.categoria?.nombre || "Sin categoría",
        stock_minimo: parsearNumero(insumo.stock_minimo),
        precio_unitario: parsearNumero(insumo.precio_unitario),
        proveedor_id: insumo.proveedor?.id || null,
        proveedor: insumo.proveedor?.nombre || "Sin Proveedor",
      }))
      .sort((a, b) => {
        if (a.bajoStock && !b.bajoStock) return -1;
        if (!a.bajoStock && b.bajoStock) return 1;
        return 0;
      });

    console.log("Stock procesado:", stock.value);
    loading.value = false;
  } catch (err) {
    console.error("Error en fetchStock:", err);
    loading.value = false;
    if (err.response?.status === 401) {
      logout();
    }
  }
};

const fetchInsumos = async () => {
  try {
    const response = await axios.get("/api/insumos/");
    insumos.value = response.data.insumos;
    // 🔍 CORREGIR: Usar insumosFiltrados.value en lugar de insumosFiltrados
    insumosFiltrados.value = response.data.insumos;
  } catch (err) {
    console.error("Error en fetchInsumos:", err);
  }
};

const fetchCategorias = async () => {
  try {
    const response = await axios.get("/api/categorias/");
    categorias.value = response.data;
  } catch (err) {
    console.error("Error en fetchCategorias:", err);
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

const fetchProveedores = async () => {
  try {
    const response = await axios.get("/api/proveedores/");
    proveedores.value = response.data;
  } catch (err) {
    console.error("Error en fetchProveedores:", err);
  }
};

// Watchers para resetear paginación cuando cambian los filtros
watch(
  [searchTerm, categoriaSeleccionada, proveedorSeleccionado, filtroActivo],
  () => {
    resetearPaginacion();
  }
);

// Computed para unidades permitidas
const unidadesPermitidas = computed(() => {
  return unidadesMedida.value;
});

// Watch para calcular precio unitario cuando cambia cantidad o precio total
watch(
  () => [formCompra.value.cantidad, formCompra.value.precio_total],
  () => {
    calcularPrecioUnitario();
  }
);

// AGREGAR: Watch para notificaciones de stock
watch(
  () => [...notificacionesStockCritico.value, ...notificacionesStockBajo.value],
  (nuevasNotificaciones, anterioresNotificaciones) => {
    // Aquí podrías integrar con el sistema de notificaciones del header
    if (headerRef.value && headerRef.value.actualizarNotificacionesStock) {
      headerRef.value.actualizarNotificacionesStock(nuevasNotificaciones);
    }
  },
  { deep: true }
);

const reponerStockRapido = (item) => {
  esReposicionRapida.value = true;
  insumoReposicionRapida.value = item;
  formCompra.value.insumo_id = item.id;
  // Siempre poner 0 en lugar de calcular
  formCompra.value.cantidad = 0;
  formCompra.value.precio_total = 0;
  formCompra.value.precio_unitario = 0;
  actualizarUnidadMedida();
  showModalCompra.value = true;
};

// AGREGAR: Método para actualizar notificaciones en el Header
const actualizarNotificacionesStock = () => {
  if (headerRef.value && headerRef.value.actualizarNotificaciones) {
    headerRef.value.actualizarNotificaciones();
  }
};

// Método para verificar y notificar cambios en stock
const verificarStockYNotificar = (item, accion) => {
  // Notificar si el stock está crítico
  if (item.cantidad <= item.stock_minimo * 0.5) {
    notificationSystem.show({
      type: "warning",
      title: "Stock Crítico",
      message: `${item.nombre} necesita reposición urgente`,
      timeout: 6000,
    });
  }
  // Notificar si el stock está bajo
  else if (item.bajoStock) {
    notificationSystem.show({
      type: "info",
      title: "Stock Bajo",
      message: `${item.nombre} está por debajo del stock mínimo`,
      timeout: 5000,
    });
  }

  // Actualizar notificaciones en el header
  actualizarNotificacionesStock();
};

// Método para verificar parámetro de búsqueda en la URL
const verificarParametroBusqueda = () => {
  // Verificar si hay un parámetro 'search' en la URL
  if (route.query.search) {
    // Asignar el valor del parámetro al campo de búsqueda
    searchTerm.value = route.query.search;

    // Opcional: Mostrar un mensaje indicando que se aplicó un filtro
    notificationSystem.show({
      type: "info",
      title: "Búsqueda aplicada",
      message: `Mostrando resultados para: "${route.query.search}"`,
      timeout: 3000,
    });
  }
};

// Watchers
watch(() => formCompra.value.insumo_id, actualizarUnidadMedida);
watch(
  () => [formCompra.value.cantidad, formCompra.value.precio_total],
  () => {
    calcularPrecioUnitario();
  }
);

// Watcher para limpiar el parámetro de la URL cuando se limpie la búsqueda
watch(searchTerm, (newValue) => {
  if (!newValue) {
    // Si se limpia la búsqueda, también limpiar el parámetro de la URL
    if (route.query.search) {
      router.replace({ query: {} });
    }
  }
});

// 🔒 WATCHER PARA RESETEAR MODO REPOSICIÓN RÁPIDA AL CERRAR EL MODAL
watch(
  () => showModalCompra.value,
  (newVal) => {
    if (!newVal) {
      // Resetear modo reposición rápida cuando se cierra el modal
      esReposicionRapida.value = false;
      insumoReposicionRapida.value = null;
    }
  }
);

watch(
  stock,
  () => {
    actualizarNotificacionesStock();
  },
  { deep: true }
);

// Cargar datos al montar el componente
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  // Cargar datos del usuario y stock
  Promise.all([
    fetchStock(),
    fetchInsumos(),
    fetchCategorias(),
    fetchUnidadesMedida(),
    fetchProveedores(),
  ])
    .then(() => {
      // AGREGAR: Actualizar notificaciones después de cargar stock
      actualizarNotificacionesStock();

      // AGREGAR: Verificar si hay un parámetro de búsqueda en la URL
      verificarParametroBusqueda();
    })
    .catch((error) => {
      console.error("Error cargando datos:", error);
      loading.value = false;
      if (error.response?.status === 401) {
        logout();
      }
    });
});

const cerrarModalCompra = () => {
  showModalCompra.value = false;
  // Resetear modo reposición rápida
  esReposicionRapida.value = false;
  insumoReposicionRapida.value = null;
  resetFormCompra();
};

const validarCantidad = () => {
  // Solo validar que no sea negativo, pero permitir 0
  if (parseFloat(formCompra.value.cantidad) < 0) {
    formCompra.value.cantidad = 0;
  }
};

// Agregar en el script
const isMobile = ref(false);

const checkViewport = () => {
  isMobile.value = window.innerWidth <= 768;
};

onMounted(() => {
  checkViewport();
  window.addEventListener("resize", checkViewport);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkViewport);
});
</script>

<style scoped>
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css");

/* ----------------------------- BOTONES GENERALES ----------------------------- */
.botones-acciones {
  display: flex;
  gap: 10px;
}

.btn-nuevo-insumo,
.btn-nueva-compra {
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

.btn-nuevo-insumo:hover,
.btn-nueva-compra:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
}

.btn-nueva-compra {
  background: linear-gradient(135deg, #17a2b8, #138496);
}

.btn-nueva-compra:hover {
  box-shadow: 0 6px 20px rgba(23, 162, 184, 0.3);
}

/* ----------------------------- CARD DE STOCK MEJORADA ----------------------------- */
.stock-card {
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 16px;
  margin: 0 auto;
  border: 1px solid #eaeaea;
}

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stock-item {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stock-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
  border-color: var(--color-primary);
}

.stock-item.stock-critico {
  border-left: 4px solid #dc3545;
}

.stock-item.bajo-stock {
  border-left: 4px solid #ffc107;
}

.stock-item:not(.bajo-stock):not(.stock-critico) {
  border-left: 4px solid #28a745;
}

/* Contenedor compacto */
.stock-item-compact {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
}

/* Indicador de estado */
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

.estado-indicador.bajo {
  background-color: #ffc107;
  box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.2);
}

.estado-indicador.normal {
  background-color: #28a745;
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.2);
}

/* Información principal */
.info-principal {
  flex: 1;
  min-width: 0;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
  gap: 8px;
}

.nombre-insumo {
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

.badge-categoria,
.badge-proveedor {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-categoria {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
}

.badge-proveedor {
  background: #e9ecef;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.info-stock {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stock-actual {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.cantidad {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
}

.unidad {
  font-size: 0.8rem;
  color: #6c757d;
  font-weight: 500;
}

.stock-minimo {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
}

.stock-minimo .label {
  color: #6c757d;
}

.stock-minimo .valor {
  color: #495057;
  font-weight: 500;
}

/* Acciones */
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

.btn-reposicion-rapida {
  background: linear-gradient(135deg, #218838, #1e7e34);
  color: white;
}

.btn-reposicion-rapida:hover {
  background: linear-gradient(135deg, #1e7e34, #1c7430);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(33, 136, 56, 0.3);
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

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 200px;
  }
}

.detalles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.detalle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.detalle-label {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.detalle-valor {
  font-size: 0.85rem;
  font-weight: 600;
}

.detalle-valor.critico {
  color: #dc3545;
}

.detalle-valor.bajo {
  color: #e0a800;
}

.detalle-valor.normal {
  color: #28a745;
}

.detalle-valor.negativo {
  color: #dc3545;
}

.detalle-valor.positivo {
  color: #28a745;
}

/* Alerta de stock */
.alerta-stock {
  padding: 10px 12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 500;
}

.alerta-stock.critica {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alerta-stock.advertencia {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

/* ----------------------------- BOTÓN FLOTANTE NUEVA COMPRA ----------------------------- */
.btn-nueva-compra-flotante {
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

.btn-nueva-compra-flotante:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
  color: #212529;
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

/* ----------------------------- ESTADÍSTICAS STOCK ----------------------------- */

/* Estilos para la paginación */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: auto;
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

/* Estilos para la información del insumo fijo en reposición rápida */
.insumo-fijo-stock-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
  font-size: 0.85rem;
}

.stock-actual-info {
  color: #2c3e50;
  font-weight: 500;
}

.stock-minimo-info {
  color: #6c757d;
  font-weight: 500;
}

.insumo-fijo-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.insumo-fijo-header i {
  color: #6c757d;
}

/* Estilos para el select de insumos en modo normal */
.form-input option {
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.form-input option:hover {
  background-color: #f8f9fa;
}

/* ----------------------------- UTILIDADES ----------------------------- */
.cursor-pointer {
  cursor: pointer;
}

/* Estilos para el modal de reactivación */
.reactivar-content {
  text-align: center;
  padding: 20px 0;
}

.warning-icon {
  font-size: 3rem;
  color: #ffc107;
  margin-bottom: 15px;
}

.insumo-info {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
  text-align: left;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e9ecef;
}

.info-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.info-item .label {
  font-weight: 600;
  color: #495057;
}

.info-item .value {
  color: #6c757d;
}

.reactivar-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-reactivar {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-reactivar:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
}

.btn-reactivar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancelar {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-cancelar:hover:not(:disabled) {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Estilo para el botón de pérdida */
.btn-perdida {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.btn-perdida:hover {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
}

/* ----------------------------- RESPONSIVE ----------------------------- */

/* Tablets */
@media (max-width: 1024px) {
  .stock-card {
    padding: 15px;
  }
}

/* Tablets pequeñas y móviles grandes */
@media (max-width: 768px) {
  .botones-acciones {
    width: 100%;
  }

  .btn-nuevo-insumo {
    width: 100%;
    justify-content: center;
  }

  .stock-card {
    padding: 12px;
  }

  .stock-item-compact {
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

  .info-stock {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .detalles-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .detalle-item {
    padding: 6px 10px;
  }

  .btn-nueva-compra-flotante {
    bottom: 20px;
    right: 20px;
    padding: 14px 20px;
    font-size: 0.9rem;
  }

  .loading-state,
  .empty-state {
    padding: 40px 20px;
  }

  .loading-state i,
  .empty-state i {
    font-size: 1.5rem;
  }

  .loading-state p,
  .empty-state p {
    font-size: 1rem;
  }

  .pagination-controls {
    flex-direction: column;
    gap: 12px;
  }

  .pagination-buttons {
    order: -1;
  }

  .pagination-info {
    text-align: center;
  }
}

/* Móviles pequeños */
@media (max-width: 480px) {
  .stock-card {
    padding: 8px;
  }

  .stock-item-compact {
    padding: 8px 10px;
    gap: 8px;
  }

  .nombre-insumo {
    font-size: 0.9rem;
  }

  .badge-categoria,
  .badge-proveedor {
    font-size: 0.65rem;
    padding: 2px 6px;
  }

  .cantidad {
    font-size: 1rem;
  }

  .stock-detalles {
    padding: 12px;
  }

  .alerta-stock {
    padding: 8px 10px;
    font-size: 0.8rem;
  }

  .acciones-container {
    gap: 4px;
  }

  .btn-accion {
    width: 28px;
    height: 28px;
    padding: 6px;
  }

  .btn-nueva-compra-flotante {
    bottom: 15px;
    right: 15px;
    padding: 12px 18px;
    font-size: 0.8rem;
  }

  .btn-nueva-compra-flotante span {
    display: none;
  }

  .pagination-numbers {
    gap: 2px;
  }

  .pagination-number {
    min-width: 32px;
    height: 32px;
    font-size: 0.8rem;
  }

  .pagination-btn {
    width: 32px;
    height: 32px;
  }
}

/* Pantallas muy pequeñas */
@media (max-width: 360px) {
  .stock-item-compact {
    padding: 6px 8px;
    gap: 6px;
  }

  .nombre-insumo {
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
  .stock-item:hover {
    transform: none;
  }

  .btn-accion {
    min-height: 44px;
    min-width: 44px;
  }

  .btn-nuevo-insumo,
  .btn-nueva-compra-flotante {
    min-height: 44px;
  }
}
.total-counter-small {
  font-size: 0.7em;
  color: var(--color-primary);
  font-weight: 600;
  margin-left: 0;
  background: rgba(108, 117, 125, 0.1);
  padding: 0;
  border-radius: 8px;
}
</style>
