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
              <!-- Contenedor principal compacto -->
              <div class="stock-item-compact">
                <!-- Indicador de estado -->
                <div
                  class="estado-indicador"
                  :class="{
                    critico: item.cantidad <= item.stock_minimo * 0.5,
                    bajo:
                      item.bajoStock && item.cantidad > item.stock_minimo * 0.5,
                    normal: !item.bajoStock,
                  }"
                ></div>

                <!-- Información principal -->
                <div class="info-principal" @click="toggleStock(item.id)">
                  <div class="info-header">
                    <h4 class="nombre-insumo">{{ item.nombre }}</h4>
                    <div class="badges-container">
                      <span class="badge-categoria">{{ item.categoria }}</span>
                      <span class="badge-proveedor">{{ item.proveedor }}</span>
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
                      <span class="label">Mín:</span>
                      <span class="valor"
                        >{{ formatDecimal(item.stock_minimo) }}
                        {{ item.unidad }}</span
                      >
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
        </div>

        <!-- Botón Nueva Compra flotante -->
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
      :title="esReposicionRapida ? 'Nueva Compra' : 'Nueva Compra'"
      size="large"
      @close="cerrarModalCompra"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Insumo:</label>

          <!-- MODO REPOSICIÓN RÁPIDA: Mostrar insumo fijo -->
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
  insumoReposicionRapida.value = 0;
  formCompra.value.insumo_id = item.id;
  // Siempre poner 0 en lugar de calcular
  formCompra.value.cantidad = 0;
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

/* ----------------------------- CARD DE STOCK MEJORADA ----------------------------- */
.stock-card {
  max-height: calc(100vh - 200px);
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
  background: linear-gradient(135deg, #218838, #1e7e34);
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
  box-shadow: 0 6px 20px rgba(33, 136, 56, 0.3);
  z-index: 100;
  font-size: 1rem;
}

.btn-nueva-compra-flotante:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(33, 136, 56, 0.4);
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

/* ----------------------------- UTILIDADES ----------------------------- */
.cursor-pointer {
  cursor: pointer;
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
</style>
