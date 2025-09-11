<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header
        :userEmail="userEmail"
        title="Gestión de Stock"
        @openPasswordModal="showPasswordModal = true"
        @logout="logout"
      />
      <main class="main-content">
        <section class="content stock-content">
          <h3 class="card-title1">Gestión de Stock</h3>
          <div class="botones-acciones">
            <button class="btn-nuevo-pedido" @click="showNuevoInsumoModal">
              <i class="fas fa-plus"></i> Nuevo Insumo
            </button>
            <button class="btn-nuevo-pedido" @click="showNuevaCompraModal">
              <i class="fas fa-shopping-cart"></i> Nueva Compra
            </button>
          </div>

          <!-- Filtros de stock alineados a la derecha -->
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
            No hay insumos que coincidan con los filtros seleccionados
          </div>

          <div v-else class="pedidos-list">
            <div
              v-for="item in stockFiltrado"
              :key="item.id"
              class="pedido-item"
              :class="{ 'bajo-stock': item.bajoStock }"
            >
              <div class="pedido-header">
                <div class="pedido-info">
                  <span class="insumo-container">
                    <span class="insumo-nombre"
                      >{{ item.nombre }}
                      <span class="insumo-categoria"
                        >({{ item.categoria }})</span
                      >
                    </span>
                    <span class="insumo-cantidad"
                      >{{ formatDecimal(item.cantidad) }}{{ item.unidad }}</span
                    >
                    <span class="insumo-precio" v-if="item.precio_unitario"
                      >${{ formatDecimal(item.precio_unitario) }}/{{
                        item.unidad
                      }}</span
                    >
                    <span class="insumo-categoria">{{ item.proveedor }}</span>
                  </span>
                </div>
                <div class="pedido-acciones">
                  <span
                    class="estado-badge"
                    :class="item.bajoStock ? 'bajo' : 'normal'"
                    v-if="item.bajoStock"
                  >
                    Stock Bajo
                  </span>
                  <button
                    class="btn-accion"
                    @click="editarInsumo(item)"
                    title="Editar insumo"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="btn-accion"
                    @click="confirmarEliminarInsumo(item)"
                    title="Eliminar insumo"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <div class="stock-minimo" v-if="item.bajoStock">
                ⚠️ Stock mínimo: {{ formatDecimal(item.stock_minimo) }}
                {{ item.unidad }}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Modal para Nuevo/Editar Insumo -->
    <div v-if="showModalInsumo" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ esEdicion ? "Editar Insumo" : "Nuevo Insumo" }}</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre:</label>
            <input
              v-model="formInsumo.nombre"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Categoría:</label>
            <div class="cliente-select-container">
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
                class="btn-agregar-cliente"
                @click="showNuevaCategoriaModal = true"
                title="Agregar nueva categoría"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Unidad de Medida:</label>
            <div class="cliente-select-container">
              <select
              v-model="formInsumo.unidad_medida_id"
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
            <button
                type="button"
                class="btn-agregar-cliente"
                @click="showNuevaUnidadDeMedidaModal = true"
                title="Agregar nueva categoría"
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
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Precio Unitario:</label>
            <input
              v-model="formInsumo.precio_unitario"
              type="number"
              step="0.01"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Proveedor:</label>
            <div class="cliente-select-container">
              <select v-model="formInsumo.proveedor_id" class="form-input">
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
                class="btn-agregar-cliente"
                @click="showNuevoProveedorModal = true"
                title="Agregar nuevo proveedor"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="closeModal" class="cancel-button">Cancelar</button>
          <button @click="guardarInsumo" class="confirm-button">
            {{ esEdicion ? "Actualizar" : "Guardar" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Nueva Compra -->
    <div v-if="showModalCompra" class="modal-overlay">
      <div class="modal-content">
        <h3>Nueva Compra</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Insumo:</label>
            <select
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
              required
              class="form-input"
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
              required
              class="form-input"
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
            <div class="cliente-select-container">
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
                class="btn-agregar-cliente"
                @click="showNuevoProveedorModal = true"
                title="Agregar nuevo proveedor"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="closeModal" class="cancel-button">Cancelar</button>
          <button @click="registrarCompra" class="confirm-button">
            Registrar Compra
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Nuevo Proveedor -->
    <div v-if="showNuevoProveedorModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nuevo Proveedor</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre:</label>
            <input
              v-model="formProveedor.nombre"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Teléfono:</label>
            <input
              v-model="formProveedor.telefono"
              type="text"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Email:</label>
            <input
              v-model="formProveedor.email"
              type="email"
              class="form-input"
            />
          </div>
        </div>

        <div class="modal-buttons">
          <button
            @click="showNuevoProveedorModal = false"
            class="cancel-button"
          >
            Cancelar
          </button>
          <button @click="guardarProveedor" class="confirm-button">
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Nueva Categoría -->
    <div v-if="showNuevaCategoriaModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nueva Categoría</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre:</label>
            <input
              v-model="formCategoria.nombre"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Descripción:</label>
            <textarea
              v-model="formCategoria.descripcion"
              class="form-input"
            ></textarea>
          </div>
        </div>

        <div class="modal-buttons">
          <button
            @click="showNuevaCategoriaModal = false"
            class="cancel-button"
          >
            Cancelar
          </button>
          <button @click="guardarCategoria" class="confirm-button">
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Nueva Unidad medida -->
    <div v-if="showNuevaUnidadDeMedidaModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nueva Unidad de Medida</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre:</label>
            <input
              v-model="formUnidad.nombre"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>abreviatura:</label>
            <input
              v-model="formUnidad.abreviatura"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Descripción:</label>
            <textarea
              v-model="formUnidad.descripcion"
              class="form-input"
            ></textarea>
          </div>
        </div>

        <div class="modal-buttons">
          <button
            @click="showNuevaUnidadDeMedidaModal = false"
            class="cancel-button"
          >
            Cancelar
          </button>
          <button @click="guardarUnidadDeMedida" class="confirm-button">
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirmar Eliminación</h3>
        <p>
          ¿Está seguro de que desea eliminar el insumo "{{
            insumoAEliminar?.nombre
          }}"?
        </p>

        <div class="modal-buttons">
          <button @click="showConfirmModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="eliminarInsumo" class="confirm-button">
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para cambiar contraseña -->
    <div v-if="showPasswordModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Cambiar contraseña</h3>
        <div class="form-group">
          <label>Contraseña actual:</label>
          <input type="password" v-model="currentPassword" class="form-input" />
        </div>
        <div class="form-group">
          <label>Nueva contraseña:</label>
          <input type="password" v-model="newPassword" class="form-input" />
        </div>
        <div class="form-group">
          <label>Repita la nueva contraseña:</label>
          <input type="password" v-model="confirmPassword" class="form-input" />
        </div>
        <div class="modal-buttons">
          <button @click="showPasswordModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="changePassword" class="confirm-button">
            Aceptar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted, watch } from "vue";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import axios from "axios";

const router = useRouter();

// Variables de estado
const userEmail = ref("Usuario");
const showPasswordModal = ref(false);
const stock = ref([]);
const insumos = ref([]);
const categorias = ref([]);
const unidadesMedida = ref([]);
const proveedores = ref([]);
const categoriaSeleccionada = ref("");
const searchTerm = ref("");
const loading = ref(true);

// Modales
const showModalInsumo = ref(false);
const showModalCompra = ref(false);
const showNuevoProveedorModal = ref(false);
const showConfirmModal = ref(false);
const showNuevaCategoriaModal = ref(false);
const showNuevaUnidadDeMedidaModal = ref(false);

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
  descripcion:"",
});

const esEdicion = ref(false);
const insumoAEliminar = ref(null);
const unidadCompra = ref("");

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
    filtered = filtered.filter(
      (item) =>
        item.nombre.toLowerCase().includes(term) 
    );
  }

  return filtered;
});

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
      alert("El nombre de la categoría es requerido");
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
    alert("Categoría creada correctamente");
  } catch (error) {
    console.error("Error al guardar categoría:", error);
    if (error.response?.status === 400 && error.response?.data?.error) {
      alert(error.response.data.error);
      resetFormCategoria();
    }
    else {
      alert("Error al guardar la categoría");
      resetFormCategoria();
    }
  }
};

// Método para guardar unidad de medida
const guardarUnidadDeMedida = async () => {
  try {
    if (!formUnidad.value.nombre) {
      alert("El nombre de la unidad es requerido");
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
    alert("Unidad de Medida creada correctamente");
  } catch (error) {
    console.error("Error al guardar la unidad de medida:", error);
    if (error.response?.status === 400 && error.response?.data?.error) {
      alert(error.response.data.error);
      resetFormUnidad();
    }
    else {
      alert("Error al guardar la categoría");
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
    abreviatura:"",
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
    alert("Insumo eliminado correctamente");
  } catch (error) {
    console.error("Error al eliminar insumo:", error);
    alert("Error al eliminar el insumo");
  }
};

const guardarInsumo = async () => {
  try {
    if (!formInsumo.value.nombre) {
      alert("El nombre es requerido");
      return;
    }
    if (!formInsumo.value.unidad_medida_id) {
      alert("La unidad de medida es requerida");
      return;
    }
    if (!formInsumo.value.stock_minimo && formInsumo.value.stock_minimo !== 0) {
      alert("El stock mínimo es requerido");
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

    await fetchStock();
    closeModal();
    alert(
      esEdicion.value
        ? "Insumo actualizado correctamente"
        : "Insumo creado correctamente"
    );
  } catch (error) {
    if (error.response?.status === 400 && error.response?.data?.error) {
      alert(error.response.data.error);
      resetFormInsumo();
    }
    else {
      alert("Error al guardar el insumo");
      resetFormInsumo();
    }
  }
};

const registrarCompra = async () => {
  try {
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

    console.log("Respuesta del servidor:", response.data);

    await fetchStock();
    closeModal();
    alert("Compra registrada correctamente");
  } catch (error) {
    console.error("Error completo al registrar compra:", error);
    console.error("Response data:", error.response?.data);
    console.error("Response status:", error.response?.status);
    alert(
      "Error al registrar la compra: " +
        (error.response?.data?.message || error.message)
    );
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
    alert("Proveedor creado correctamente");
  } catch (error) {
    console.error("Error al guardar proveedor:", error);
    if (error.response?.status === 400 && error.response?.data?.error) {
      alert(error.response.data.error);
      resetFormProveedor();
    } else {
      alert("Error al guardar el proveedor");
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
    cantidad: 0,
    precio_total: 0,
    precio_unitario: 0,
    proveedor_id: "",
  };
  unidadCompra.value = "";
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

// Watchers
watch(() => formCompra.value.insumo_id, actualizarUnidadMedida);
watch(
  () => [formCompra.value.cantidad, formCompra.value.precio_total],
  calcularPrecioUnitario
);

// Cargar datos al montar el componente
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  // Cargar datos del usuario y stock
  Promise.all([
    axios.get("/api/auth/perfil/").then((res) => {
      userEmail.value = res.data.email || "Usuario";
    }),
    fetchStock(),
    fetchInsumos(),
    fetchCategorias(),
    fetchUnidadesMedida(),
    fetchProveedores(),
  ]).catch((error) => {
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

/* ----------------------------- CONTENIDO Y CARDS ESPECÍFICOS ----------------------------- */
.stock-content {
  display: flex;
  padding: 0 20px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: nowrap;
  /* Evita que se envuelvan a la siguiente línea */
  gap: 20px;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
  /* Evita que se encojan demasiado */
}

.filtros-derecha {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filtro-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filtro-input,
.filtro-select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  height: 38px;
  /* Misma altura que los botones */
}

/* BOTONES */
.botones-acciones {
  display: flex;
  gap: 10px;
  margin-right: auto;
  /* ← Esto los lleva a la izq */
  margin-bottom: 25px;
}

.btn-nuevo-pedido {
  background-color: #b8e6b8;
  color: #2b5d2b;
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
  height: 38px;
  /* Altura consistente */
}

.btn-nuevo-pedido:hover {
  background-color: #a1dca1;
}

/* ----------------------------- CARD DE STOCK ----------------------------- */
.stock-card {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.pedidos-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.pedido-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
}

.pedido-item.bajo-stock {
  border-left: 4px solid #ffcc00;
  background-color: #fff9e6;
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.pedido-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

.insumo-nombre {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.insumo-categoria {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

.insumo-cantidad {
  font-size: 14px;
  color: #666;
}

.insumo-precio {
  font-size: 14px;
  color: #2e7d32;
  font-weight: bold;
}

.pedido-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
}

.estado-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.estado-badge.bajo {
  background-color: #fff3cd;
  color: #856404;
}

.estado-badge.normal {
  background-color: #d4edda;
  color: #155724;
}

.btn-accion {
  background: none;
  border: none;
  cursor: pointer;
  color: #7b5a50;
  font-size: 16px;
}

.btn-accion:hover {
  color: #5a3f36;
}

.stock-minimo {
  padding: 8px;
  background-color: #fff3cd;
  border-radius: 4px;
  color: #856404;
  font-size: 14px;
}

.loading-state {
  text-align: center;
  padding: 20px;
  color: #7b5a50;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
  font-style: italic;
}

/* ----------------------------- MODALES ----------------------------- */
.modal-content {
  background-color: var(--color-white);
  padding: 20px;
  border-radius: 10px;
  width: 600px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #7b5a50;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: bold;
  font-size: 14px;
}

.form-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.cliente-select-container {
  display: flex;
  gap: 8px;
}

.cliente-select-container select {
  flex: 1;
}

.btn-agregar-cliente {
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-agregar-cliente:hover {
  background-color: #218838;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.cancel-button {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-button {
  padding: 8px 16px;
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.insumo-container {
  display: flex;
  align-items: center;
  gap: 20px;
  /* Espacio uniforme entre todos los elementos */
  flex-wrap: wrap;
  /* Para que se ajuste en pantallas pequeñas */
}

.insumo-container > span {
  white-space: nowrap;
  /* Evita que se rompan los textos */
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 1024px) {
  .header-section {
    flex-wrap: wrap;
    gap: 15px;
  }

  .filtros-derecha {
    width: 100%;
    justify-content: flex-start;
    margin-top: 15px;
  }
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    width: 100%;
  }

  .filtros-derecha {
    flex-direction: column;
    width: 100%;
    gap: 10px;
  }

  .filtro-group {
    width: 100%;
  }

  .filtro-input,
  .filtro-select {
    width: 100%;
  }

  .botones-acciones {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .pedido-header {
    flex-direction: column;
  }

  .pedido-acciones {
    align-self: flex-end;
    margin-top: 10px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .botones-acciones {
    flex-direction: column;
  }

  .btn-nuevo-pedido {
    width: 100%;
    justify-content: center;
  }
}
</style>
