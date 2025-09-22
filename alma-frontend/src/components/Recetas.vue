<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header />
      <main class="main-content">
        <section class="recetas-content">
          <h3 class="card-title1">Gestión de Recetas</h3>
          <div class="botones-acciones">
            <button class="btn-nuevo-pedido" @click="showNuevaRecetaModal">
              <i class="fas fa-plus"></i> Nueva Receta
            </button>
          </div>

          <!-- Filtros de recetas alineados a la derecha -->
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
            No hay recetas que coincidan con los filtros seleccionados
          </div>

          <div v-else class="recetas-list">
            <div
              v-for="receta in recetasFiltradas"
              :key="receta.id"
              class="receta-item"
            >
              <div class="receta-header">
                <div class="receta-info">
                  <span class="receta-container">
                    <span class="receta-nombre"
                      >{{ receta.nombre }}
                      <span class="receta-veces-hecha"
                        >(Preparada {{ receta.veces_hecha }} veces)</span
                      >
                    </span>
                    <span class="receta-rinde"
                      >Rinde: {{ receta.rinde }} {{ receta.unidad_rinde }}</span
                    >
                    <span class="receta-costo"
                      >Costo: ${{ formatDecimal(receta.costo_total) }}</span
                    >
                    <span class="receta-precio"
                      >Precio: ${{ formatDecimal(receta.precio_venta) }}</span
                    >
                  </span>
                </div>
                <div class="receta-acciones">
                  <button
                    class="btn-accion"
                    @click="incrementarReceta(receta)"
                    title="Preparar receta"
                  >
                    <i class="fas fa-plus-circle"></i>
                  </button>
                  <button
                    class="btn-accion"
                    @click="decrementarReceta(receta)"
                    title="Revertir preparación"
                  >
                    <i class="fas fa-minus-circle"></i>
                  </button>
                  <button
                    class="btn-accion"
                    @click="agregarInsumosAReceta(receta)"
                    title="Agregar/editar insumos"
                  >
                    <i class="fas fa-utensils"></i>
                  </button>
                  <button
                    class="btn-accion"
                    @click="editarReceta(receta)"
                    title="Editar receta"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="btn-accion"
                    @click="confirmarEliminarReceta(receta)"
                    title="Eliminar receta"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <div class="receta-insumos">
                <h4>Insumos ({{ receta.insumos.length }}):</h4>
                <div
                  v-for="insumo in receta.insumos"
                  :key="insumo.id"
                  class="insumo-item"
                >
                  <span class="insumo-nombre">{{ insumo.insumo.nombre }}</span>
                  <span class="insumo-cantidad"
                    >{{ formatDecimal(insumo.cantidad) }}
                    {{ insumo.unidad_medida.abreviatura }}</span
                  >
                  <span
                    class="insumo-costo"
                    v-if="insumo.insumo.precio_unitario"
                  >
                    Costo: ${{ formatDecimal(calcularCostoInsumo(insumo)) }}
                  </span>
                  <button
                    class="btn-eliminar-insumo-lista"
                    @click="eliminarInsumoDeReceta(receta, insumo)"
                    title="Eliminar insumo"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                <div v-if="receta.insumos.length === 0" class="sin-insumos">
                  <i class="fas fa-info-circle"></i>
                  Esta receta no tiene insumos asignados
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Modal para Nueva/Editar Receta (solo datos básicos) -->
    <div v-if="showModalReceta" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ esEdicion ? "Editar Receta" : "Nueva Receta" }}</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre:</label>
            <input
              v-model="formReceta.nombre"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Rinde:</label>
            <input
              v-model="formReceta.rinde"
              type="number"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Unidad de Rinde:</label>
            <select
              v-model="formReceta.unidad_rinde"
              required
              class="form-input"
            >
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
              required
              class="form-input"
            />
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="closeModal" class="cancel-button">Cancelar</button>
          <button @click="guardarRecetaBasica" class="confirm-button">
            {{ esEdicion ? "Actualizar" : "Guardar Receta" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Agregar/Eliminar Insumos a Receta -->
    <div v-if="showModalInsumos" class="modal-overlay">
      <div class="modal-content">
        <h3>Agregar Insumos a: {{ recetaSeleccionada?.nombre }}</h3>

        <div class="insumos-section">
          <h4>Agregar Nuevo Insumo:</h4>
          <div class="form-grid">
            <div class="form-group">
              <label>Insumo:</label>
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
            </div>

            <div class="form-group">
              <label>Cantidad:</label>
              <input
                v-model="nuevoInsumo.cantidad"
                type="number"
                step="0.001"
                required
                class="form-input"
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
          <h4>Insumos Actuales:</h4>
          <div
            v-for="insumo in recetaSeleccionada?.insumos || []"
            :key="insumo.id"
            class="insumo-existente-item"
          >
            <span class="insumo-info">
              {{ insumo.insumo.nombre }} - {{ formatDecimal(insumo.cantidad) }}
              {{ insumo.unidad_medida.abreviatura }}
            </span>
            <button
              class="btn-eliminar-insumo-existente"
              @click="eliminarInsumoDeReceta(recetaSeleccionada, insumo)"
              title="Eliminar insumo"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
          <div v-if="!recetaSeleccionada?.insumos?.length" class="sin-insumos">
            No hay insumos agregados
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="showModalInsumos = false" class="cancel-button">
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar receta -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirmar Eliminación</h3>
        <p>
          ¿Está seguro de que desea eliminar la receta "{{
            recetaAEliminar?.nombre
          }}"?
        </p>

        <div class="modal-buttons">
          <button @click="showConfirmModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="eliminarReceta" class="confirm-button">
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted, inject } from "vue";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import axios from "axios";

const router = useRouter();
const notificationSystem = inject("notifications");

// Variables de estado
const recetas = ref([]);
const insumosDisponibles = ref([]);
const unidadesMedida = ref([]);
const searchTerm = ref("");
const loading = ref(true);

// Modales
const showModalReceta = ref(false);
const showModalInsumos = ref(false);
const showConfirmModal = ref(false);

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

  const numericValue =
    typeof value === "string" ? parseFloat(value.replace(",", ".")) : value;

  return Number(numericValue).toLocaleString("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const calcularCostoInsumo = (insumoReceta) => {
  if (!insumoReceta.insumo.precio_unitario) return 0;

  const precioUnitario = parseFloat(
    insumoReceta.insumo.precio_unitario.toString().replace(",", ".")
  );
  const cantidad = parseFloat(
    insumoReceta.cantidad.toString().replace(",", ".")
  );

  return precioUnitario * cantidad;
};

const resetFilters = () => {
  searchTerm.value = "";
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
    nuevoInsumo.value.unidad_medida_id = insumo.unidad_medida.id.toString();
    // También establecer una cantidad por defecto si es necesario
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

    // Recargar la receta para obtener los insumos actualizados
    await fetchRecetas();

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

const eliminarInsumoDeReceta = async (receta, insumo) => {
  try {
    await axios.delete(`/api/recetas/${receta.id}/insumos/${insumo.id}/`);

    // Recargar la receta para obtener los insumos actualizados
    await fetchRecetas();

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

const incrementarReceta = async (receta) => {
  try {
    const response = await axios.post(`/api/recetas/${receta.id}/incrementar/`);

    if (response.data.stock_actualizado) {
      notificationSystem.show({
        type: "success",
        title: "Receta preparada",
        message: response.data.mensaje,
        timeout: 4000,
      });

      // Actualizar el contador en la lista local
      const index = recetas.value.findIndex((r) => r.id === receta.id);
      if (index !== -1) {
        recetas.value[index].veces_hecha = response.data.nuevo_contador;
      }

      // Recargar insumos para actualizar stock
      await fetchInsumosDisponibles();
    }
  } catch (error) {
    console.error("Error al incrementar receta:", error);

    if (error.response?.status === 400 && error.response?.data?.insuficientes) {
      const insuficientes = error.response.data.insuficientes;
      let mensaje = `Stock insuficiente para preparar "${receta.nombre}":\n`;

      insuficientes.forEach((ins) => {
        mensaje += `- ${ins.nombre}: Necesita ${ins.necesario} ${ins.unidad}, tiene ${ins.disponible} ${ins.unidad}\n`;
      });

      notificationSystem.show({
        type: "error",
        title: "Stock insuficiente",
        message: mensaje,
        timeout: 8000,
      });
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al preparar la receta",
        timeout: 6000,
      });
    }
  }
};

const decrementarReceta = async (receta) => {
  try {
    if (receta.veces_hecha <= 0) {
      notificationSystem.show({
        type: "warning",
        title: "No se puede revertir",
        message: "Esta receta no ha sido preparada aún",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.post(`/api/recetas/${receta.id}/decrementar/`);

    if (response.data.stock_actualizado) {
      notificationSystem.show({
        type: "success",
        title: "Preparación revertida",
        message: response.data.mensaje,
        timeout: 4000,
      });

      // Actualizar el contador en la lista local
      const index = recetas.value.findIndex((r) => r.id === receta.id);
      if (index !== -1) {
        recetas.value[index].veces_hecha = response.data.nuevo_contador;
      }

      // Recargar insumos para actualizar stock
      await fetchInsumosDisponibles();
    }
  } catch (error) {
    console.error("Error al decrementar receta:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al revertir la preparación",
      timeout: 6000,
    });
  }
};

const closeModal = () => {
  showModalReceta.value = false;
  showModalInsumos.value = false;
  showConfirmModal.value = false;
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

// Funciones para cargar datos
const fetchRecetas = async () => {
  try {
    loading.value = true;
    const response = await axios.get("/api/recetas/");
    recetas.value = response.data;
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
.recetas-content {
  display: flex;
  padding: 0 20px;
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

.filtro-input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  height: 38px;
}

/* BOTONES */
.botones-acciones {
  display: flex;
  gap: 10px;
  margin-right: auto;
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
}

.btn-nuevo-pedido:hover {
  background-color: #a1dca1;
}

/* ----------------------------- CARD DE RECETAS ----------------------------- */
.recetas-card {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.recetas-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.receta-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
}

.receta-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.receta-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

.receta-nombre {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.receta-veces-hecha {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

.receta-rinde,
.receta-costo,
.receta-precio {
  font-size: 14px;
  color: #666;
}

.receta-precio {
  color: #2e7d32;
  font-weight: bold;
}

.receta-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
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

.receta-insumos {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ddd;
}

.receta-insumos h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.insumo-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 10px;
}

.insumo-item:last-child {
  border-bottom: none;
}

.insumo-nombre {
  font-size: 14px;
  flex: 1;
}

.insumo-cantidad {
  font-size: 14px;
  color: #666;
  min-width: 80px;
}

.insumo-costo {
  font-size: 14px;
  color: #2e7d32;
  min-width: 100px;
  text-align: right;
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
  width: 800px;
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

.insumos-section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 6px;
  background-color: #f9f9f9;
}

.insumos-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #7b5a50;
}

.insumo-form {
  margin-bottom: 15px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: white;
}

.btn-agregar-insumo {
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
}

.btn-agregar-insumo:hover {
  background-color: #a1dca1;
}

.btn-eliminar-insumo {
  background: none;
  border: none;
  cursor: pointer;
  color: #dc3545;
  font-size: 16px;
  align-self: flex-end;
  margin-top: 24px;
}

.btn-eliminar-insumo:hover {
  color: #bd2130;
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

.btn-accion {
  background: none;
  border: none;
  cursor: pointer;
  color: #7b5a50;
  font-size: 16px;
  margin: 0 2px;
}

.btn-eliminar-insumo-lista {
  background: none;
  border: none;
  cursor: pointer;
  color: #dc3545;
  font-size: 14px;
  padding: 2px 6px;
}

.btn-eliminar-insumo-existente {
  background: none;
  border: none;
  cursor: pointer;
  color: #dc3545;
  font-size: 14px;
  padding: 4px 8px;
}

.btn-agregar-insumo-modal {
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  margin-top: 24px;
}

.btn-agregar-insumo-modal:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.insumo-existente-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.insumo-info {
  flex: 1;
}

.sin-insumos {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 10px;
}

.insumos-existente-section {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 6px;
  background-color: #f9f9f9;
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .filtros-derecha {
    flex-direction: column;
    align-items: stretch;
  }

  .receta-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .receta-acciones {
    align-self: flex-end;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .insumo-item {
    flex-direction: column;
    gap: 5px;
  }

  .insumo-costo {
    text-align: left;
  }
}
</style>
