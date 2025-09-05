<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header
        :userEmail="userEmail"
        title="Panel Principal"
        @openPasswordModal="showPasswordModal = true"
        @logout="logout"
      />

      <main class="main-content">
        <h3 class="card-title">
          Stock
          <span v-if="insumosBajoStock > 0" class="badge">
            (Hay {{ insumosBajoStock }} insumos con bajo stock)
          </span>
        </h3>

        <!-- Botones de acción -->
        <div class="action-buttons">
          <button class="btn-primary" @click="showNuevoInsumoModal">
            Nuevo Insumo
          </button>
          <button class="btn-success" @click="showNuevaCompraModal">
            Nueva Compra
          </button>
        </div>

        <!-- Buscador + Filtro -->
        <div class="stock-header">
          <span>
            Buscar:
            <input
              v-model="searchTerm"
              type="text"
              placeholder="Buscar insumo..."
              class="form-input"
            />
          </span>
          <span>
            Categoría:
            <select v-model="categoriaSeleccionada">
              <option value="">Todas</option>
              <option v-for="cat in categoriasStock" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </span>
        </div>

        <section class="content">
          <div class="card stock">
            <div class="stock-header-container">
              <div class="stock-header">
                <span>Nombre</span>
                <span>Cantidad</span>
                <span>Acciones</span>
              </div>
            </div>

            <ul class="stock-list">
              <li
                v-for="item in stockFiltrado"
                :key="item.id"
                :class="{ 'low-stock': item.bajoStock }"
              >
                <span>{{ item.nombre }} ({{ item.categoria }})</span>
                <span
                  >{{ formatDecimal(item.cantidad) }} {{ item.unidad }}</span
                >
                <span class="action-buttons">
                  <button class="btn-edit" @click="editarInsumo(item)">
                    Editar
                  </button>
                  <button
                    class="btn-delete"
                    @click="confirmarEliminarInsumo(item)"
                  >
                    Eliminar
                  </button>
                </span>
              </li>
            </ul>
          </div>
        </section>
      </main>
    </div>

    <!-- Modal para Nuevo Insumo -->
    <div v-if="showModalInsumo" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ esEdicion ? "Editar Insumo" : "Nuevo Insumo" }}</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="guardarInsumo">
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
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn-secondary">
                Cancelar
              </button>
              <button type="submit" class="btn-primary">
                {{ esEdicion ? "Actualizar" : "Guardar" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal para Nueva Compra -->
    <div v-if="showModalCompra" class="modal-overlay">
      <div class="modal">
        <div class="modal-header">
          <h3>Nueva Compra</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="registrarCompra">
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
                  {{ insumo.nombre }}
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
                  class="btn-small"
                  @click="showNuevoProveedorModal = true"
                >
                  +
                </button>
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeModal" class="btn-secondary">
                Cancelar
              </button>
              <button type="submit" class="btn-success">
                Registrar Compra
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal para Nuevo Proveedor -->
    <div v-if="showNuevoProveedorModal" class="modal-overlay">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Nuevo Proveedor</h3>
          <button class="close-btn" @click="showNuevoProveedorModal = false">
            &times;
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="guardarProveedor">
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
            <div class="modal-actions">
              <button
                type="button"
                @click="showNuevoProveedorModal = false"
                class="btn-secondary"
              >
                Cancelar
              </button>
              <button type="submit" class="btn-primary">Guardar</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Confirmar Eliminación</h3>
          <button class="close-btn" @click="showConfirmModal = false">
            &times;
          </button>
        </div>
        <div class="modal-body">
          <p>
            ¿Está seguro de que desea eliminar el insumo "{{
              insumoAEliminar?.nombre
            }}"?
          </p>
          <div class="modal-actions">
            <button
              type="button"
              @click="showConfirmModal = false"
              class="btn-secondary"
            >
              Cancelar
            </button>
            <button type="button" @click="eliminarInsumo" class="btn-delete">
              Eliminar
            </button>
          </div>
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

// Modales
const showModalInsumo = ref(false);
const showModalCompra = ref(false);
const showNuevoProveedorModal = ref(false);
const showConfirmModal = ref(false);

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
        item.nombre.toLowerCase().includes(term) ||
        item.categoria.toLowerCase().includes(term)
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
  // Convertir coma a punto para poder parsear correctamente
  const numericValue =
    typeof value === "string" ? parseFloat(value.replace(",", ".")) : value;

  return Number(numericValue).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
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
    stock_minimo: parsearNumero(insumo.stock_minimo), // Parsear aquí
    precio_unitario: parsearNumero(insumo.precio_unitario), // Parsear aquí
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

    // 🚩 Solo agregar stock_actual = 0 cuando sea un insumo nuevo
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
    console.error("Error completo al guardar insumo:", error);
    alert("Error al guardar el insumo");
  }
};

const registrarCompra = async () => {
  try {
    console.log("Datos de compra:", formCompra.value);

    const insumo = insumos.value.find(
      (i) => i.id === parseInt(formCompra.value.insumo_id)
    );
    console.log("Insumo encontrado:", insumo);

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
    ); // Cambia la URL
    await fetchProveedores();
    showNuevoProveedorModal.value = false;
    resetFormProveedor();
    alert("Proveedor creado correctamente");
  } catch (error) {
    console.error("Error al guardar proveedor:", error);
    alert("Error al guardar el proveedor");
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
    const response = await axios.get("/api/insumos/");
    stock.value = response.data.insumos
      .map((insumo) => ({
        id: insumo.id,
        nombre: insumo.nombre,
        cantidad: parsearNumero(insumo.stock_actual), // Usar parsearNumero aquí
        unidad: insumo.unidad_medida.abreviatura,
        bajoStock: insumo.necesita_reposicion,
        categoria: insumo.categoria?.nombre || "Sin categoría",
        stock_minimo: parsearNumero(insumo.stock_minimo), // Usar parsearNumero aquí
        precio_unitario: parsearNumero(insumo.precio_unitario), // Usar parsearNumero aquí
        proveedor_id: insumo.proveedor?.id || null,
      }))
      .sort((a, b) => {
        if (a.bajoStock && !b.bajoStock) return -1;
        if (!a.bajoStock && b.bajoStock) return 1;
        return 0;
      });
  } catch (err) {
    console.error("Error en fetchStock:", err);
    if (err.response?.status === 401) {
      logout();
    }
  }
};

const fetchInsumos = async () => {
  try {
    const response = await axios.get("/api/insumos/");
    insumos.value = response.data.insumos; // Asegúrate de acceder a la propiedad correcta
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
    if (error.response?.status === 401) {
      logout();
    }
  });
});
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.stock-header span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stock-header-container .stock-header {
  display: grid;
  grid-template-columns: 1fr 1fr 120px;
  padding: 10px 15px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
}

.stock-list li {
  display: grid;
  grid-template-columns: 1fr 1fr 120px;
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
}

.stock-list li.low-stock {
  background-color: #fff0f0;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.btn-primary,
.btn-success,
.btn-secondary,
.btn-edit,
.btn-delete {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background-color: #4a6cf7;
  color: white;
}

.btn-success {
  background-color: #22c55e;
  color: white;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-edit {
  background-color: #eab308;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

.btn-delete {
  background-color: #ef4444;
  color: white;
  padding: 4px 8px;
  font-size: 12px;
}

.btn-small {
  padding: 4px 8px;
  background-color: #4a6cf7;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-sm {
  width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.select-with-button {
  display: flex;
  gap: 10px;
}

.select-with-button select {
  flex: 1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.badge {
  background-color: #ef4444;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 14px;
  margin-left: 10px;
}
</style>
