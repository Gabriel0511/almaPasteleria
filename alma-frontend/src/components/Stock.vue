<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <section class="principal-content">
          <h3 class="card-title1" :class="{ 'mobile-center': isMobile }">
            Gestión de Stock
          </h3>

          <!-- AGREGAR: Estadísticas de stock con badges -->
          <div class="estadisticas-stock">
            <div class="estadistica-item" v-if="estadisticasStock.critico > 0">
              <span class="estadistica-badge critico">
                <i class="fas fa-exclamation-triangle"></i>
                {{ estadisticasStock.critico }} crítico
              </span>
            </div>
            <div class="estadistica-item" v-if="estadisticasStock.bajo > 0">
              <span class="estadistica-badge bajo">
                <i class="fas fa-exclamation-circle"></i>
                {{ estadisticasStock.bajo }} bajo
              </span>
            </div>
            <div class="estadistica-item">
              <span class="estadistica-badge normal">
                <i class="fas fa-check-circle"></i>
                {{ estadisticasStock.normal }} normal
              </span>
            </div>
            <div class="estadistica-item">
              <span class="estadistica-badge total">
                <i class="fas fa-boxes"></i>
                {{ estadisticasStock.total }} total
              </span>
            </div>
          </div>

          <!-- Filtros de stock -->
          <div class="filtros-derecha">
            <div class="filtro-group">
              <input
                type="text"
                v-model="searchTerm"
                placeholder="Buscar insumo..."
                class="filtro-input"
              />
            </div>

            <div class="filtro-group">
              <select v-model="categoriaSeleccionada" class="filtro-select">
                <option value="">Todas las categorías</option>
                <option v-for="cat in categoriasStock" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>

            <div class="botones-acciones">
              <button class="btn-nuevo-insumo" @click="showNuevoInsumoModal">
                <i class="fas fa-plus"></i> Nuevo Insumo
              </button>
            </div>
          </div>
        </section>

        <!-- Card principal de stock -->
        <div class="card stock-card">
          <div v-if="loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i> Cargando stock...
          </div>

          <div v-else-if="stockFiltrado.length === 0" class="empty-state">
            <i class="fas fa-search"></i>
            <p>No hay insumos que coincidan con los filtros seleccionados</p>
          </div>

          <div v-else class="stock-list">
            <div
              v-for="item in stockFiltrado"
              :key="item.id"
              class="stock-item"
              :class="{
                'bajo-stock': item.bajoStock,
                'stock-critico': item.cantidad <= item.stock_minimo * 0.5,
                expanded: stockDesplegado[item.id],
              }"
            >
              <!-- AGREGAR: Indicador de urgencia -->
              <div
                v-if="item.cantidad <= item.stock_minimo * 0.5"
                class="indicador-urgencia critico"
                title="Stock crítico - Reposición urgente"
              >
                <i class="fas fa-exclamation-circle"></i>
                URGENTE
              </div>

              <div
                v-else-if="item.bajoStock"
                class="indicador-urgencia bajo"
                title="Stock bajo - Considerar reposición"
              >
                <i class="fas fa-exclamation-circle"></i>
                BAJO
              </div>

              <!-- Contenedor principal del header -->
              <div class="stock-item-main">
                <!-- Header compacto para móviles -->
                <div
                  class="stock-header-compact cursor-pointer"
                  @click="toggleStock(item.id)"
                >
                  <div class="stock-header-content">
                    <div class="stock-info-main">
                      <div class="stock-titulo">
                        <span class="insumo-nombre">{{ item.nombre }}</span>
                        <span class="insumo-badge" v-if="!isMobile">{{
                          item.categoria
                        }}</span>
                      </div>
                      <div class="stock-datos-compact">
                        <div class="dato-grupo">
                          <i class="fas fa-box"></i>
                          <span class="stock-cantidad">
                            {{ formatDecimal(item.cantidad) }} {{ item.unidad }}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div class="stock-header-right" @click.stop>
                      <div class="stock-acciones">
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
                        <button
                          class="btn-accion btn-desplegable"
                          @click="toggleStock(item.id)"
                          :title="
                            stockDesplegado[item.id]
                              ? 'Ocultar detalles'
                              : 'Mostrar detalles'
                          "
                        >
                          <i
                            class="fas"
                            :class="
                              stockDesplegado[item.id]
                                ? 'fa-chevron-up'
                                : 'fa-chevron-down'
                            "
                          ></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Desplegable que aparece en la parte inferior del stock-item -->
                <div
                  v-if="stockDesplegado[item.id]"
                  class="stock-detalles-container"
                >
                  <div class="detalles-content">
                    <!-- Información de stock mínimo -->
                    <div class="stock-minimo-info">
                      <h4>
                        <i class="fas fa-info-circle"></i> Información de Stock
                      </h4>
                      <div class="stock-minimo-grid">
                        <div class="minimo-item">
                          <span class="minimo-label">Stock Mínimo:</span>
                          <span class="minimo-valor">
                            {{ formatDecimal(item.stock_minimo) }}
                            {{ item.unidad }}
                          </span>
                        </div>
                        <div class="minimo-item">
                          <span class="minimo-label">Stock Actual:</span>
                          <span
                            class="minimo-valor"
                            :class="{
                              critico: item.cantidad <= item.stock_minimo * 0.5,
                              bajo:
                                item.bajoStock &&
                                item.cantidad > item.stock_minimo * 0.5,
                              normal: !item.bajoStock,
                            }"
                          >
                            {{ formatDecimal(item.cantidad) }} {{ item.unidad }}
                          </span>
                        </div>
                        <div class="minimo-item">
                          <span class="minimo-label">Diferencia:</span>
                          <span
                            class="minimo-valor"
                            :class="{
                              negativo: item.cantidad < item.stock_minimo,
                              positivo: item.cantidad >= item.stock_minimo,
                            }"
                          >
                            {{
                              formatDecimal(item.cantidad - item.stock_minimo)
                            }}
                            {{ item.unidad }}
                          </span>
                        </div>
                        <div class="minimo-item" v-if="item.precio_unitario">
                          <span class="minimo-label">Precio Unitario:</span>
                          <span class="minimo-valor">
                            ${{ formatDecimal(item.precio_unitario) }}
                          </span>
                        </div>
                        <div class="minimo-item">
                          <span class="minimo-label">Proveedor:</span>
                          <span class="minimo-valor">{{ item.proveedor }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Alertas de stock -->
                    <div
                      v-if="item.bajoStock"
                      class="stock-alerta"
                      :class="{
                        'alerta-critica':
                          item.cantidad <= item.stock_minimo * 0.5,
                        'alerta-baja':
                          item.bajoStock &&
                          item.cantidad > item.stock_minimo * 0.5,
                      }"
                    >
                      <i
                        class="fas"
                        :class="{
                          'fa-exclamation-triangle':
                            item.cantidad <= item.stock_minimo * 0.5,
                          'fa-exclamation-circle':
                            item.bajoStock &&
                            item.cantidad > item.stock_minimo * 0.5,
                        }"
                      ></i>
                      <span v-if="item.cantidad <= item.stock_minimo * 0.5">
                        ¡Stock crítico! Necesita reposición urgente.
                      </span>
                      <span v-else> Stock bajo. Considerar reposición. </span>
                    </div>

                    <!-- Acciones rápidas -->
                    <div class="stock-acciones-rapidas" v-if="item.bajoStock">
                      <button
                        class="btn-reposicion"
                        @click="reponerStockRapido(item)"
                      >
                        <i class="fas fa-bolt"></i> Reposición Rápida
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón Nueva Compra flotante -->
        <button class="btn-nueva-compra-flotante" @click="showNuevaCompraModal">
          <i class="fas fa-shopping-cart"></i>
          <span>Nueva Compra</span>
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
          <label>Unidad de Medida:</label>
          <div class="select-with-button">
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
            <button
              type="button"
              class="btn-agregar"
              @click="showNuevaUnidadDeMedidaModal = true"
              title="Agregar nueva unidad de medida"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Stock Mínimo:</label>
          <input
            v-model="formInsumo.stock_minimo"
            type="number"
            step="0.001"
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
      :title="esReposicionRapida ? 'Reposición Rápida' : 'Nueva Compra'"
      size="large"
      @close="cerrarModalCompra"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Insumo:</label>

          <!-- MODO REPOSICIÓN RÁPIDA: Mostrar insumo fijo -->
          <div
            v-if="esReposicionRapida && insumoReposicionRapida"
            class="insumo-fijo-container"
          >
            <div class="insumo-fijo">
              <div class="insumo-fijo-nombre">
                <div class="insumo-fijo-header">
                  <i class="fas fa-lock"></i>
                  <strong>{{ insumoReposicionRapida.nombre }}</strong>
                </div>
                <span class="insumo-fijo-stock">
                  (Stock actual:
                  {{ formatDecimal(insumoReposicionRapida.cantidad) }}
                  {{ insumoReposicionRapida.unidad }})
                </span>
              </div>
              <div class="insumo-fijo-categoria">
                {{ insumoReposicionRapida.categoria }}
              </div>
            </div>
            <input type="hidden" v-model="formCompra.insumo_id" />
          </div>

          <!-- MODO NORMAL: Select de insumos (desplegable normal) -->
          <select
            v-else
            v-model="formCompra.insumo_id"
            required
            class="form-input"
            @change="actualizarUnidadMedida"
          >
            <option value="">Seleccione un insumo</option>
            <option
              v-for="insumo in insumos"
              :key="insumo.id"
              :value="insumo.id"
            >
              {{ insumo.nombre }} (Stock:
              {{ formatDecimal(insumo.stock_actual) }}
              {{ insumo.unidad_medida.abreviatura }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Cantidad:</label>
          <input
            v-model="formCompra.cantidad"
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
          <label>Precio Unitario:</label>
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

    <!-- Modal para Nueva Unidad de Medida -->
    <BaseModal
      v-model:show="showNuevaUnidadDeMedidaModal"
      title="Nueva Unidad de Medida"
      size="small"
      @close="showNuevaUnidadDeMedidaModal = false"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Nombre:</label>
          <input
            v-model="formUnidad.nombre"
            type="text"
            required
            class="form-input"
            placeholder="Nombre completo"
          />
        </div>

        <div class="form-group">
          <label>Abreviatura:</label>
          <input
            v-model="formUnidad.abreviatura"
            type="text"
            required
            class="form-input"
            placeholder="Ej: kg, g, l, ml"
            maxlength="10"
          />
        </div>

        <div class="form-group full-width">
          <label>Descripción:</label>
          <textarea
            v-model="formUnidad.descripcion"
            class="form-input"
            rows="3"
            placeholder="Descripción de la unidad"
          ></textarea>
        </div>
      </div>

      <template #footer>
        <ModalButtons
          confirm-text="Guardar"
          @cancel="showNuevaUnidadDeMedidaModal = false"
          @confirm="guardarUnidadDeMedida"
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
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted, onUnmounted, watch, inject } from "vue";
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
const stock = ref([]);
const insumos = ref([]);
const categorias = ref([]);
const unidadesMedida = ref([]);
const proveedores = ref([]);
const categoriaSeleccionada = ref("");
const searchTerm = ref("");
const loading = ref(true);
const stockDesplegado = ref({});
const busquedaInsumo = ref("");
const insumosFiltrados = ref([]);

// Modales
const showModalInsumo = ref(false);
const showModalCompra = ref(false);
const showNuevoProveedorModal = ref(false);
const showConfirmModal = ref(false);
const showNuevaCategoriaModal = ref(false);
const showNuevaUnidadDeMedidaModal = ref(false);

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

// Agregar formulario para categoría
const formUnidad = ref({
  nombre: "",
  abreviatura: "",
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

// Computed properties
const insumosBajoStock = computed(() => {
  return stock.value.filter((item) => item.bajoStock).length;
});

const categoriasStock = computed(() => {
  const categorias = stock.value.map((item) => item.categoria);
  return [...new Set(categorias)];
});

const stockFiltrado = computed(() => {
  let filtered = stock.value;

  // Filtrar por categoría
  if (categoriaSeleccionada.value) {
    filtered = filtered.filter(
      (item) => item.categoria === categoriaSeleccionada.value
    );
  }

  // Filtrar por término de búsqueda
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter((item) =>
      item.nombre.toLowerCase().includes(term)
    );
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

// AGREGAR: Computed properties para notificaciones de stock
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

// Nuevo método para toggle del desplegable
const toggleStock = (stockId) => {
  stockDesplegado.value = {
    ...stockDesplegado.value,
    [stockId]: !stockDesplegado.value[stockId],
  };
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

// Método para guardar unidad de medida
const guardarUnidadDeMedida = async () => {
  try {
    if (!formUnidad.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre de la unidad es requerido",
        timeout: 4000,
      });
      return;
    }
    if (!formUnidad.value.abreviatura) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La abreviatura es requerida",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.post(
      "/api/unidades-medida/crear/",
      formUnidad.value
    );

    // Actualizar lista de unidades
    await fetchUnidadesMedida();

    showNuevaUnidadDeMedidaModal.value = false;
    resetFormUnidad();

    notificationSystem.show({
      type: "success",
      title: "Unidad de medida creada",
      message: "Unidad de Medida creada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar la unidad de medida:", error);
    if (error.response?.status === 400 && error.response?.data?.error) {
      notificationSystem.show({
        type: "error",
        title: "Error al crear unidad",
        message: error.response.data.error,
        timeout: 6000,
      });
      resetFormUnidad();
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al guardar la unidad de medida",
        timeout: 6000,
      });
      resetFormUnidad();
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

// Resetear formulario de unidad
const resetFormUnidad = () => {
  formUnidad.value = {
    nombre: "",
    abreviatura: "",
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
    if (!formInsumo.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre es requerido",
        timeout: 4000,
      });
      return;
    }
    if (!formInsumo.value.unidad_medida_id) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La unidad de medida es requerida",
        timeout: 4000,
      });
      return;
    }
    if (!formInsumo.value.stock_minimo && formInsumo.value.stock_minimo !== 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El stock mínimo es requerido",
        timeout: 4000,
      });
      return;
    }

    const formatearParaBackend = (valor) => {
      if (valor === null || valor === undefined) return null;
      return valor.toString().replace(".", ",");
    };

    // Preparar datos
    const datosParaEnviar = {
      nombre: formInsumo.value.nombre,
      categoria_id: formInsumo.value.categoria_id || null,
      unidad_medida_id: formInsumo.value.unidad_medida_id,
      stock_minimo: formatearParaBackend(
        parseFloat(formInsumo.value.stock_minimo)
      ),
      precio_unitario: formInsumo.value.precio_unitario
        ? formatearParaBackend(parseFloat(formInsumo.value.precio_unitario))
        : null,
      proveedor_id: formInsumo.value.proveedor_id || null,
      activo: true,
    };

    // Solo agregar stock_actual = 0 cuando sea un insumo nuevo
    if (!esEdicion.value) {
      datosParaEnviar.stock_actual = 0;
    }

    let response;
    if (esEdicion.value) {
      response = await axios.patch(
        `/api/insumos/${formInsumo.value.id}/actualizar-parcial/`,
        datosParaEnviar
      );
    } else {
      response = await axios.post("/api/insumos/crear/", datosParaEnviar);
    }

    // Refrescar tanto stock como insumos
    await fetchStock();
    await fetchInsumos();
    closeModal();

    const insumoGuardado = response.data;
    if (esEdicion.value) {
      // Buscar el item actualizado en el stock
      const itemActualizado = stock.value.find(
        (item) => item.id === insumoGuardado.id
      );
      if (itemActualizado) {
        verificarStockYNotificar(itemActualizado, "actualizado");
      }
    }

    notificationSystem.show({
      type: "success",
      title: esEdicion.value ? "Insumo actualizado" : "Insumo creado",
      message: esEdicion.value
        ? "Insumo actualizado correctamente"
        : "Insumo creado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    if (error.response?.status === 400 && error.response?.data?.error) {
      notificationSystem.show({
        type: "error",
        title: "Error al guardar insumo",
        message: error.response.data.error,
        timeout: 6000,
      });
      resetFormInsumo();
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al guardar el insumo",
        timeout: 6000,
      });
      resetFormInsumo();
    }
  }
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

    console.log("Stock actual:", stockActual);
    console.log("Cantidad comprada:", cantidadComprada);
    console.log("Nuevo stock calculado:", nuevoStock);

    const datosActualizacion = {
      stock_actual: nuevoStock.toFixed(3).replace(".", ","), // Formato con coma para el backend
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

    console.log("Datos a enviar:", datosActualizacion);

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
  };
};

const resetFormCompra = () => {
  formCompra.value = {
    insumo_id: "",
    cantidad: 0, // Cambiar a 0 en lugar de 0.001
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

// AGREGAR: Método para reposición rápida
const reponerStockRapido = (item) => {
  esReposicionRapida.value = true;
  insumoReposicionRapida.value = item;
  formCompra.value.insumo_id = item.id;
  // Calcular cantidad sugerida: suficiente para llegar al stock mínimo + 20%
  const cantidadSugerida = Math.max(
    item.stock_minimo * 1.2 - item.cantidad,
    item.stock_minimo * 0.5
  );
  formCompra.value.cantidad = Math.ceil(cantidadSugerida * 100) / 100;
  actualizarUnidadMedida();
  showModalCompra.value = true;
};

// AGREGAR: Método para actualizar notificaciones en el Header
const actualizarNotificacionesStock = () => {
  if (headerRef.value && headerRef.value.actualizarNotificaciones) {
    headerRef.value.actualizarNotificaciones();
  }
};

// AGREGAR: Método para verificar y notificar cambios en stock
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

  // Notificar cuando se repone stock
  if (accion === "reposicion" && !item.bajoStock) {
    notificationSystem.show({
      type: "success",
      title: "Stock Repuesto",
      message: `${item.nombre} ha sido repuesto correctamente`,
      timeout: 4000,
    });
  }

  // Actualizar notificaciones en el header
  actualizarNotificacionesStock();
};

// Watchers
watch(() => formCompra.value.insumo_id, actualizarUnidadMedida);
watch(
  () => [formCompra.value.cantidad, formCompra.value.precio_total],
  () => {
    calcularPrecioUnitario();
  }
);

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

/* ----------------------------- CARD DE STOCK ----------------------------- */
.stock-card {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(123, 90, 80, 0.1);
  padding: 25px;
  margin: 0 auto;
  border: 1px solid rgba(123, 90, 80, 0.1);
}

.stock-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stock-item {
  position: relative;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.stock-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, var(--color-primary), #f1d0cb);
  opacity: 0.8;
}

.stock-item.bajo-stock::before {
  background: linear-gradient(to bottom, #ffc107, #ffcd39);
}

.stock-item.stock-critico::before {
  background: linear-gradient(to bottom, #dc3545, #e74c3c);
}

.stock-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(123, 90, 80, 0.15);
  border-color: var(--color-primary);
}

.stock-item.expanded {
  padding-bottom: 0;
}

.stock-item-main {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.stock-header-full {
  width: 100%;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  padding: 15px 20px;
  flex-shrink: 0;
}

.stock-header-full:hover {
  background-color: rgba(123, 90, 80, 0.05);
}

.stock-header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  gap: 20px;
}

.stock-info-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stock-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.insumo-nombre {
  font-weight: 700;
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0;
}

.insumo-badge {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.stock-datos-compact {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stock-datos-compact .dato-grupo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
  background: rgba(123, 90, 80, 0.05);
  padding: 6px 12px;
  border-radius: 6px;
}

.stock-datos-compact .dato-grupo i {
  color: var(--color-primary);
  width: 14px;
  text-align: center;
  font-size: 0.8rem;
}

.stock-header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

/* ----------------------------- BOTONES DE ACCIÓN ----------------------------- */
.stock-acciones {
  display: flex;
  align-items: center;
  margin-top: 12px;
  gap: 8px;
  flex-shrink: 0;
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
.stock-detalles-container {
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

.stock-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.stock-minimo-info h4 {
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  color: var(--color-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stock-minimo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.minimo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.minimo-label {
  font-weight: 500;
  color: #6c757d;
}

.minimo-valor {
  font-weight: 600;
}

.minimo-valor.critico {
  color: #dc3545;
}

.minimo-valor.bajo {
  color: #ffc107;
}

.minimo-valor.normal {
  color: #28a745;
}

.minimo-valor.negativo {
  color: #dc3545;
}

.minimo-valor.positivo {
  color: #28a745;
}

/* ----------------------------- ALERTAS DE STOCK ----------------------------- */
.stock-alerta {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
}

.alerta-critica {
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alerta-baja {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  color: #856404;
  border: 1px solid #ffeaa7;
}

/* ----------------------------- ACCIONES RÁPIDAS ----------------------------- */
.stock-acciones-rapidas {
  text-align: right;
}

.btn-reposicion {
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

.btn-reposicion:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(23, 162, 184, 0.3);
}

/* ----------------------------- BOTÓN FLOTANTE NUEVA COMPRA ----------------------------- */
.btn-nueva-compra-flotante {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #218838);
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
  box-shadow: 0 6px 20px rgba(23, 162, 184, 0.3);
  z-index: 100;
  font-size: 1rem;
}

.btn-nueva-compra-flotante:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(23, 162, 184, 0.4);
  background: linear-gradient(135deg, #218838);
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

/* ----------------------------- MODALES Y FORMULARIOS ----------------------------- */
/* Campo de búsqueda que ocupa todo el ancho */
.full-width {
  grid-column: 1 / -1;
  width: 100%;
}

.full-width .form-input {
  width: 100%;
  box-sizing: border-box;
}

/* Estilo específico para el campo de búsqueda con lupa */
.form-input.search-input {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%236c757d' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: 12px center;
  background-size: 16px;
  padding-left: 40px;
  width: 100%;
}

.search-info {
  margin-top: 5px;
  color: #6c757d;
  font-size: 0.8rem;
  text-align: right;
}

/* Mejorar la apariencia del select más grande */
.form-input[size] {
  min-height: 120px;
  width: 100%;
}

/* Asegurar que los formularios en modales usen una sola columna */
.modal-content .form-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.modal-content .form-group {
  width: 100%;
}

.modal-content .form-input {
  width: 100%;
  box-sizing: border-box;
}

/* Añadir al final de la sección de estilos */
.cursor-pointer {
  cursor: pointer;
}

.stock-header-full:hover {
  background-color: rgba(123, 90, 80, 0.05);
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

/* Indicador visual de que es clickeable */
.stock-header-full::after {
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

.stock-header-full:hover::after {
  box-shadow: inset 0 0 0 2px rgba(123, 90, 80, 0.1);
}

/* Mejorar la transición del desplegable */
.stock-detalles-container {
  transition: all 0.3s ease;
  max-height: 0;
  overflow: hidden;
}

.stock-item.expanded .stock-detalles-container {
  max-height: 1000px;
}

/* Indicador de clickeabilidad en el título */
.insumo-nombre {
  position: relative;
  transition: color 0.2s ease;
}

.stock-header-full:hover .insumo-nombre {
  color: var(--color-primary);
}

.stock-header-full:hover .insumo-nombre::after {
  content: " (click para detalles)";
  font-size: 0.7em;
  opacity: 0.7;
  font-weight: normal;
  margin-left: 5px;
}

/* Efecto de pulso para stock crítico */
.stock-item.stock-critico .stock-header-full:hover {
  animation: pulse-alert 2s infinite;
}

@keyframes pulse-alert {
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

/* Efecto de pulso para stock bajo */
.stock-item.bajo-stock .stock-header-full:hover {
  animation: pulse-warning 2s infinite;
}

@keyframes pulse-warning {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4);
  }

  70% {
    box-shadow: 0 0 0 10px rgba(255, 193, 7, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0);
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(220, 53, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
  }
}

/* AGREGAR: Indicadores de urgencia en items de stock */
.indicador-urgencia {
  position: absolute;
  top: 5px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 2;
}

.indicador-urgencia.critico {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  animation: pulse 2s infinite;
}

.indicador-urgencia.bajo {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

/* AGREGAR: Estilos para cantidades críticas y bajas */
.cantidad-critica {
  color: #dc3545 !important;
  font-weight: 700;
}

.cantidad-baja {
  color: #e0a800 !important;
  font-weight: 600;
}

/* ----------------------------- RESPONSIVE IMPROVEMENTS ----------------------------- */

/* Pantallas medianas (tablets) */
@media (max-width: 1024px) {
  .stock-card {
    padding: 15px;
  }

  .stock-minimo-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Pantallas pequeñas (tablets pequeñas y móviles grandes) */
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
    border-radius: 12px;
  }

  .stock-header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .stock-header-right {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .stock-datos-compact {
    flex-direction: column;
    gap: 8px;
  }

  .stock-datos-compact .dato-grupo {
    justify-content: flex-start;
  }

  .stock-minimo-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .minimo-item {
    padding: 8px;
  }

  .detalles-content {
    padding: 15px;
  }

  .indicador-urgencia {
    position: relative;
    top: auto;
    right: auto;
    align-self: flex-start;
    margin-bottom: 10px;
  }

  /* Modal responsive */
  .form-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .select-with-button {
    flex-direction: column;
    gap: 8px;
  }

  .btn-nueva-compra-flotante {
    bottom: 20px;
    right: 20px;
    padding: 14px 20px;
    font-size: 0.9rem;
  }
}

/* Móviles pequeños */
@media (max-width: 480px) {
  .stock-list {
    padding: 0.5rem;
    gap: 0.5rem;
  }

  .stock-header-compact {
    padding: 0.75rem;
  }

  .stock-titulo {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .insumo-nombre {
    font-size: 0.875rem;
  }

  .stock-datos-compact {
    gap: 0.25rem;
  }

  .dato-grupo {
    font-size: 0.75rem;
  }

  .detalles-content {
    padding: 0.75rem;
  }

  .stock-alerta {
    padding: 0.75rem;
    font-size: 0.75rem;
  }

  .btn-reposicion {
    width: 100%;
    justify-content: center;
    padding: 0.625rem;
    font-size: 0.75rem;
  }

  .indicador-urgencia {
    position: static;
    margin-bottom: 0.5rem;
    justify-content: center;
    font-size: 0.625rem;
  }

  .stock-acciones {
    gap: 4px;
  }

  .btn-accion {
    width: 36px;
    height: 36px;
    padding: 8px;
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

  .btn-nueva-compra-flotante::after {
    display: none;
    margin-left: 5px;
  }
}

/* Pantallas muy pequeñas */
@media (max-width: 360px) {
  .stock-header-compact {
    padding: 0.5rem;
  }

  .insumo-nombre {
    font-size: 0.8rem;
  }

  .stock-acciones {
    gap: 2px;
  }

  .btn-accion {
    width: 32px;
    height: 32px;
    padding: 6px;
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
  .btn-reposicion,
  .btn-nueva-compra-flotante {
    min-height: 44px;
  }
}

/* Estados de carga y vacío responsive */
@media (max-width: 768px) {
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
    text-align: center;
  }
}

/* Mejoras de accesibilidad en móviles */
@media (max-width: 768px) {
  .stock-header-compact {
    padding: 12px;
  }

  .stock-item {
    margin-bottom: 8px;
  }

  /* Asegurar contraste suficiente */
  .insumo-nombre {
    color: #2c3e50;
  }

  .minimo-label {
    font-size: 0.85rem;
  }

  .minimo-valor {
    font-size: 0.9rem;
  }
}

/* Estados de interacción */
.cursor-pointer {
  cursor: pointer;
}

/* Utilidades de texto */
.text-sm {
  font-size: 0.875rem;
}

.text-xs {
  font-size: 0.75rem;
}

.font-medium {
  font-weight: 500;
}

.font-semibold {
  font-weight: 600;
}

/* Estados de hover mejorados */
@media (hover: hover) {
  .stock-item:hover {
    transform: translateY(-1px);
  }

  .btn-accion:hover {
    transform: translateY(-1px);
  }
}

/* ----------------------------- BOTÓN REPOSICIÓN RÁPIDA CON NUEVO COLOR ----------------------------- */
.btn-reposicion {
  background: linear-gradient(135deg, #218838, #1e7e34);
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
  box-shadow: 0 2px 6px rgba(33, 136, 56, 0.3);
}

.btn-reposicion:hover {
  background: linear-gradient(135deg, #1e7e34, #1c7430);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 136, 56, 0.4);
}

/* ----------------------------- ESTILOS PARA INSUMO FIJO EN MODAL ----------------------------- */
.insumo-fijo-container {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-left: 4px solid #218838;
}

.insumo-fijo {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.insumo-fijo-nombre {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
}

.insumo-fijo-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.insumo-fijo-header i {
  color: #218838;
  font-size: 0.9rem;
}

.insumo-fijo-header strong {
  color: #2c3e50;
  font-size: 1rem;
}

.insumo-fijo-stock {
  color: #6c757d;
  font-size: 0.85rem;
  font-weight: 500;
  background: rgba(33, 136, 56, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

.insumo-fijo-categoria {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  align-self: flex-start;
}

/* ----------------------------- ESTILOS DE VALIDACIÓN ----------------------------- */
.required-asterisk {
  color: #dc3545;
}

.input-error {
  border-color: #dc3545 !important;
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1) !important;
}

.error-message {
  color: #dc3545;
  font-size: 0.8rem;
  margin-top: 4px;
  font-weight: 500;
}

/* ----------------------------- ESTILOS PARA BÚSQUEDA EN MODAL COMPRA ----------------------------- */
.search-container {
  margin-bottom: 12px;
}

.search-container .search-input {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%236c757d' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: 12px center;
  background-size: 16px;
  padding-left: 40px;
  width: 100%;
  margin-bottom: 5px;
}

.search-info {
  color: #6c757d;
  font-size: 0.8rem;
  text-align: left;
}
</style>
