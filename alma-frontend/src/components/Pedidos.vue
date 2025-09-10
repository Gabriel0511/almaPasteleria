<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header
        :userEmail="userEmail"
        title="Gestión de Pedidos"
        @openPasswordModal="showPasswordModal = true"
        @logout="logout"
      />
      <main class="main-content">
        <section class="content pedidos-content">
          <h3 class="card-title1">Gestión de Pedidos</h3>
          <div class="botones-acciones">
            <button class="btn-nuevo-pedido" @click="showNuevoPedidoModal">
              <i class="fas fa-plus"></i> Nuevo Pedido
            </button>
          </div>

          <!-- Filtros de pedidos alineados a la derecha -->
          <div class="filtros-derecha">
            <div class="filtro-group">
              <input
                type="text"
                v-model="searchTerm"
                placeholder="Buscar cliente..."
                class="filtro-input"
              />
            </div>

            <div class="filtro-group">
              <select v-model="estadoSeleccionado" class="filtro-select">
                <option value="">Todos los estados</option>
                <option
                  v-for="estado in estadosPedido"
                  :key="estado"
                  :value="estado"
                >
                  {{ estado }}
                </option>
              </select>
            </div>

            <div class="filtro-group">
              <input
                type="date"
                v-model="fechaSeleccionada"
                class="filtro-input"
              />
            </div>
          </div>
        </section>

        <!-- Card principal de pedidos -->
        <div class="card pedidos-card">
          <div v-if="loading" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i> Cargando pedidos...
          </div>

          <div v-else-if="pedidosFiltrados.length === 0" class="empty-state">
            No hay pedidos que coincidan con los filtros seleccionados
          </div>

          <div v-else class="pedidos-list">
            <div
              v-for="pedido in pedidosFiltrados"
              :key="pedido.id"
              class="pedido-item"
            >
              <div class="pedido-header">
                <div class="pedido-info">
                  <span class="cliente-container">
                    <span class="cliente-nombre"
                      >{{ pedido.cliente.nombre }}
                      <span
                        class="pedido-estado"
                        :class="pedido.estado.toLowerCase()"
                        >({{ pedido.estado }})</span
                      >
                    </span>
                    <span class="pedido-fechas">
                      Pedido: {{ formatFecha(pedido.fecha_pedido) }} | Entrega:
                      {{ formatFecha(pedido.fecha_entrega) }}
                    </span>
                    <span class="pedido-total"
                      >Total: ${{ calcularTotalPedido(pedido) }}</span
                    >
                  </span>
                </div>
                <div class="pedido-acciones">
                  <button
                    class="btn-accion"
                    @click="editarPedido(pedido)"
                    title="Editar pedido"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="btn-accion"
                    @click="confirmarEliminarPedido(pedido)"
                    title="Eliminar pedido"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <!-- Botón para agregar receta al pedido -->
              <div class="agregar-receta-container">
                <button
                  class="btn-agregar-receta"
                  @click="showAgregarRecetaModal(pedido)"
                >
                  <i class="fas fa-plus"></i> Agregar Receta
                </button>
              </div>

              <!-- Detalles del pedido - Recetas -->
              <div class="recetas-container">
                <div
                  v-for="detalle in pedido.detalles"
                  :key="detalle.id"
                  class="receta-item"
                >
                  <div class="receta-header" @click="toggleReceta(detalle.id)">
                    <span class="receta-nombre"
                      >{{ detalle.receta.nombre }} x{{ detalle.cantidad }}</span
                    >
                    <span class="receta-precio"
                      >${{ calcularPrecioReceta(detalle) }}</span
                    >
                    <i
                      class="fas"
                      :class="
                        detalleExpandido[detalle.id]
                          ? 'fa-chevron-up'
                          : 'fa-chevron-down'
                      "
                    ></i>
                  </div>

                  <div
                    v-if="detalleExpandido[detalle.id]"
                    class="receta-detalles"
                  >
                    <p class="observaciones" v-if="detalle.observaciones">
                      <strong>Observaciones:</strong>
                      {{ detalle.observaciones }}
                    </p>

                    <!-- Ingredientes extras -->
                    <div
                      class="ingredientes-extras"
                      v-if="
                        detalle.ingredientes_extra &&
                        detalle.ingredientes_extra.length > 0
                      "
                    >
                      <h4>Ingredientes Extra:</h4>
                      <div
                        v-for="ingrediente in detalle.ingredientes_extra"
                        :key="ingrediente.id"
                        class="ingrediente-extra"
                      >
                        <span
                          >{{ ingrediente.insumo.nombre }}:
                          {{ ingrediente.cantidad }}
                          {{ ingrediente.unidad_medida.abreviatura }}</span
                        >
                        <div class="ingrediente-acciones">
                          <button
                            class="btn-accion-small"
                            @click="
                              editarIngredienteExtra(ingrediente, detalle)
                            "
                            title="Editar ingrediente"
                          >
                            <i class="fas fa-edit"></i>
                          </button>
                          <button
                            class="btn-accion-small"
                            @click="
                              confirmarEliminarIngredienteExtra(ingrediente)
                            "
                            title="Eliminar ingrediente"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>

                    <div class="receta-acciones">
                      <button
                        class="btn-agregar-ingrediente"
                        @click="showNuevoIngredienteModal(detalle)"
                      >
                        <i class="fas fa-plus"></i> Agregar Ingrediente Extra
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Modal para Agregar/Editar Receta al Pedido -->
    <div v-if="showModalReceta" class="modal-overlay">
      <div class="modal-content">
        <h3>
          {{ esEdicionReceta ? "Editar Receta" : "Agregar Receta al Pedido" }}
        </h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Receta:</label>
            <select
              v-model="formDetalle.receta_id"
              required
              class="form-input"
              :disabled="esEdicionReceta"
            >
              <option value="">Seleccione una receta</option>
              <option
                v-for="receta in recetas"
                :key="receta.id"
                :value="receta.id"
              >
                {{ receta.nombre }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Cantidad:</label>
            <input
              v-model="formDetalle.cantidad"
              type="number"
              min="1"
              required
              class="form-input"
            />
          </div>

          <div class="form-group full-width">
            <label>Observaciones:</label>
            <textarea
              v-model="formDetalle.observaciones"
              class="form-input"
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="closeModal" class="cancel-button">Cancelar</button>
          <button @click="guardarDetalle" class="confirm-button">
            {{ esEdicionReceta ? "Actualizar" : "Agregar" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar receta -->
    <div v-if="showConfirmModalReceta" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirmar Eliminación</h3>
        <p>
          ¿Está seguro de que desea eliminar la receta "{{
            recetaAEliminar?.receta?.nombre
          }}" del pedido?
        </p>

        <div class="modal-buttons">
          <button @click="showConfirmModalReceta = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="eliminarReceta" class="confirm-button">
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Nuevo/Editar Pedido -->
    <div v-if="showModalPedido" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ esEdicionPedido ? "Editar Pedido" : "Nuevo Pedido" }}</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Cliente:</label>
            <div class="cliente-select-container">
              <select
                v-model="formPedido.cliente_id"
                required
                class="form-input"
              >
                <option value="">Seleccione un cliente</option>
                <option
                  v-for="cliente in clientes"
                  :key="cliente.id"
                  :value="cliente.id"
                >
                  {{ cliente.nombre }} - {{ cliente.telefono }}
                </option>
              </select>
              <button
                type="button"
                class="btn-agregar-cliente"
                @click="showNuevoClienteModal = true"
                title="Agregar nuevo cliente"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Fecha de Pedido:</label>
            <input
              v-model="formPedido.fecha_pedido"
              type="date"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Fecha de Entrega:</label>
            <input
              v-model="formPedido.fecha_entrega"
              type="date"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Estado:</label>
            <select v-model="formPedido.estado" required class="form-input">
              <option
                v-for="estado in estadosPedido"
                :key="estado"
                :value="estado"
              >
                {{ estado }}
              </option>
            </select>
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="closeModal" class="cancel-button">Cancelar</button>
          <button @click="guardarPedido" class="confirm-button">
            {{ esEdicionPedido ? "Actualizar" : "Guardar" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Nuevo Cliente -->
    <div v-if="showNuevoClienteModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nuevo Cliente</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre:</label>
            <input
              v-model="formCliente.nombre"
              type="text"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Teléfono:</label>
            <input
              v-model="formCliente.telefono"
              type="text"
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Dirección:</label>
            <input
              v-model="formCliente.direccion"
              type="text"
              class="form-input"
            />
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="showNuevoClienteModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="guardarCliente" class="confirm-button">
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Agregar/Editar Receta al Pedido -->
    <div v-if="showModalReceta" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ esEdicionReceta ? "Editar Receta" : "Agregar Receta" }}</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Receta:</label>
            <select v-model="formDetalle.receta_id" required class="form-input">
              <option value="">Seleccione una receta</option>
              <option
                v-for="receta in recetas"
                :key="receta.id"
                :value="receta.id"
              >
                {{ receta.nombre }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Cantidad:</label>
            <input
              v-model="formDetalle.cantidad"
              type="number"
              min="1"
              required
              class="form-input"
            />
          </div>

          <div class="form-group full-width">
            <label>Observaciones:</label>
            <textarea
              v-model="formDetalle.observaciones"
              class="form-input"
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="closeModal" class="cancel-button">Cancelar</button>
          <button @click="guardarDetalle" class="confirm-button">
            {{ esEdicionReceta ? "Actualizar" : "Agregar" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Agregar/Editar Ingrediente Extra -->
    <div v-if="showModalIngrediente" class="modal-overlay">
      <div class="modal-content">
        <h3>
          {{
            esEdicionIngrediente
              ? "Editar Ingrediente Extra"
              : "Agregar Ingrediente Extra"
          }}
        </h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Insumo:</label>
            <select
              v-model="formIngrediente.insumo_id"
              required
              class="form-input"
            >
              <option value="">Seleccione un insumo</option>
              <option
                v-for="insumo in insumos"
                :key="insumo.id"
                :value="insumo.id"
              >
                {{ insumo.nombre }} - ${{ insumo.precio_unitario }}/{{
                  insumo.unidad_medida.abreviatura
                }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Cantidad:</label>
            <input
              v-model="formIngrediente.cantidad"
              type="number"
              step="0.001"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label>Unidad de Medida:</label>
            <select
              v-model="formIngrediente.unidad_medida_id"
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
        </div>

        <div class="modal-buttons">
          <button @click="closeModal" class="cancel-button">Cancelar</button>
          <button @click="guardarIngredienteExtra" class="confirm-button">
            {{ esEdicionIngrediente ? "Actualizar" : "Agregar" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar pedido -->
    <div v-if="showConfirmModalPedido" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirmar Eliminación</h3>
        <p>
          ¿Está seguro de que desea eliminar el pedido de "{{
            pedidoAEliminar?.cliente?.nombre
          }}"?
        </p>

        <div class="modal-buttons">
          <button @click="showConfirmModalPedido = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="eliminarPedido" class="confirm-button">
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de confirmación para eliminar ingrediente extra -->
    <div v-if="showConfirmModalIngrediente" class="modal-overlay">
      <div class="modal-content">
        <h3>Confirmar Eliminación</h3>
        <p>¿Está seguro de que desea eliminar este ingrediente extra?</p>

        <div class="modal-buttons">
          <button
            @click="showConfirmModalIngrediente = false"
            class="cancel-button"
          >
            Cancelar
          </button>
          <button @click="eliminarIngredienteExtra" class="confirm-button">
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
const pedidos = ref([]);
const clientes = ref([]);
const recetas = ref([]);
const insumos = ref([]);
const unidadesMedida = ref([]);
const estadoSeleccionado = ref("");
const fechaSeleccionada = ref("");
const searchTerm = ref("");
const loading = ref(true);
const detalleExpandido = ref({});

// Modales
const showModalPedido = ref(false);
const showNuevoClienteModal = ref(false);
const showModalReceta = ref(false);
const showModalIngrediente = ref(false);
const showConfirmModalPedido = ref(false);
const showConfirmModalIngrediente = ref(false);
const showConfirmModalReceta = ref(false);

// Formularios
const formPedido = ref({
  id: null,
  cliente_id: "",
  fecha_pedido: new Date().toISOString().split("T")[0],
  fecha_entrega: "",
  estado: "pendiente",
});

const formCliente = ref({
  nombre: "",
  telefono: "",
  direccion: "",
});

const formDetalle = ref({
  id: null,
  pedido_id: null,
  receta_id: "",
  cantidad: 1,
  observaciones: "",
});

const formIngrediente = ref({
  id: null,
  detalle_id: null,
  insumo_id: "",
  cantidad: 0,
  unidad_medida_id: "",
});

const esEdicionPedido = ref(false);
const esEdicionReceta = ref(false);
const esEdicionIngrediente = ref(false);
const pedidoAEliminar = ref(null);
const ingredienteAEliminar = ref(null);
const recetaAEliminar = ref(null);
const detalleActual = ref(null);
const pedidoActual = ref(null);

// Estados de pedido
const estadosPedido = ref([
  "pendiente",
  "en preparación",
  "entregado",
  "cancelado",
]);

// Computed properties
const pedidosFiltrados = computed(() => {
  let filtered = pedidos.value;

  // Filtrar por estado
  if (estadoSeleccionado.value) {
    filtered = filtered.filter(
      (pedido) => pedido.estado === estadoSeleccionado.value
    );
  }

  // Filtrar por fecha
  if (fechaSeleccionada.value) {
    filtered = filtered.filter(
      (pedido) => pedido.fecha_entrega === fechaSeleccionada.value
    );
  }

  // Filtrar por término de búsqueda
  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase();
    filtered = filtered.filter(
      (pedido) =>
        pedido.cliente.nombre.toLowerCase().includes(term) ||
        pedido.cliente.telefono.toLowerCase().includes(term)
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

const formatFecha = (fecha) => {
  if (!fecha) return "";
  return new Date(fecha).toLocaleDateString("es-ES");
};

const calcularPrecioReceta = (detalle) => {
  const precioReceta = detalle.receta.precio_venta || 0;
  return (precioReceta * detalle.cantidad).toFixed(2);
};

const calcularTotalPedido = (pedido) => {
  let total = 0;
  if (pedido.detalles) {
    pedido.detalles.forEach((detalle) => {
      const precioReceta = detalle.receta.precio_venta || 0;
      total += precioReceta * detalle.cantidad;

      // Sumar ingredientes extras si existen
      if (detalle.ingredientes_extra) {
        detalle.ingredientes_extra.forEach((ingrediente) => {
          const precioIngrediente = ingrediente.insumo.precio_unitario || 0;
          total += precioIngrediente * ingrediente.cantidad;
        });
      }
    });
  }
  return total.toFixed(2);
};

const toggleReceta = (detalleId) => {
  detalleExpandido.value[detalleId] = !detalleExpandido.value[detalleId];
};

const showNuevoPedidoModal = () => {
  esEdicionPedido.value = false;
  resetFormPedido();
  showModalPedido.value = true;
};

const editarPedido = (pedido) => {
  esEdicionPedido.value = true;
  formPedido.value = {
    id: pedido.id,
    cliente_id: pedido.cliente.id,
    fecha_pedido: pedido.fecha_pedido,
    fecha_entrega: pedido.fecha_entrega,
    estado: pedido.estado,
  };
  showModalPedido.value = true;
};

const confirmarEliminarPedido = (pedido) => {
  pedidoAEliminar.value = pedido;
  showConfirmModalPedido.value = true;
};

const eliminarPedido = async () => {
  try {
    await axios.delete(`/api/pedidos/${pedidoAEliminar.value.id}/`);

    // Actualizar la lista local
    const index = pedidos.value.findIndex(
      (item) => item.id === pedidoAEliminar.value.id
    );
    if (index !== -1) {
      pedidos.value.splice(index, 1);
    }

    showConfirmModalPedido.value = false;
    alert("Pedido eliminado correctamente");
  } catch (error) {
    console.error("Error al eliminar pedido:", error);
    alert("Error al eliminar el pedido");
  }
};

const guardarPedido = async () => {
  try {
    if (!formPedido.value.cliente_id) {
      alert("El cliente es requerido");
      return;
    }
    if (!formPedido.value.fecha_entrega) {
      alert("La fecha de entrega es requerida");
      return;
    }

    let response;
    if (esEdicionPedido.value) {
      response = await axios.put(
        `/api/pedidos/${formPedido.value.id}/`,
        formPedido.value
      );
    } else {
      response = await axios.post("/api/pedidos/", formPedido.value);
    }

    await fetchPedidos();
    closeModal();
    alert(
      esEdicionPedido.value
        ? "Pedido actualizado correctamente"
        : "Pedido creado correctamente"
    );
  } catch (error) {
    console.error("Error al guardar pedido:", error);
    alert("Error al guardar el pedido");
  }
};

const guardarCliente = async () => {
  try {
    const response = await axios.post("/api/clientes/", formCliente.value);
    await fetchClientes();
    showNuevoClienteModal.value = false;
    resetFormCliente();
    alert("Cliente creado correctamente");
  } catch (error) {
    console.error("Error al guardar cliente:", error);
    alert("Error al guardar el cliente");
  }
};

const showNuevoIngredienteModal = (detalle) => {
  esEdicionIngrediente.value = false;
  detalleActual.value = detalle;
  resetFormIngrediente();
  formIngrediente.value.detalle_id = detalle.id;
  showModalIngrediente.value = true;
};

const editarIngredienteExtra = (ingrediente, detalle) => {
  esEdicionIngrediente.value = true;
  detalleActual.value = detalle;
  formIngrediente.value = {
    id: ingrediente.id,
    detalle_id: detalle.id,
    insumo_id: ingrediente.insumo.id,
    cantidad: ingrediente.cantidad,
    unidad_medida_id: ingrediente.unidad_medida.id,
  };
  showModalIngrediente.value = true;
};

const confirmarEliminarIngredienteExtra = (ingrediente) => {
  ingredienteAEliminar.value = ingrediente;
  showConfirmModalIngrediente.value = true;
};

const eliminarIngredienteExtra = async () => {
  try {
    await axios.delete(
      `/api/ingredientes-extra/${ingredienteAEliminar.value.id}/`
    );

    // Actualizar la lista local
    const pedidoIndex = pedidos.value.findIndex((pedido) =>
      pedido.detalles.some((detalle) =>
        detalle.ingredientes_extra.some(
          (ing) => ing.id === ingredienteAEliminar.value.id
        )
      )
    );

    if (pedidoIndex !== -1) {
      const pedido = pedidos.value[pedidoIndex];
      for (let detalle of pedido.detalles) {
        const ingIndex = detalle.ingredientes_extra.findIndex(
          (ing) => ing.id === ingredienteAEliminar.value.id
        );
        if (ingIndex !== -1) {
          detalle.ingredientes_extra.splice(ingIndex, 1);
          break;
        }
      }
    }

    showConfirmModalIngrediente.value = false;
    alert("Ingrediente extra eliminado correctamente");
  } catch (error) {
    console.error("Error al eliminar ingrediente extra:", error);
    alert("Error al eliminar el ingrediente extra");
  }
};

const guardarIngredienteExtra = async () => {
  try {
    if (!formIngrediente.value.insumo_id) {
      alert("El insumo es requerido");
      return;
    }
    if (
      !formIngrediente.value.cantidad ||
      formIngrediente.value.cantidad <= 0
    ) {
      alert("La cantidad debe ser mayor a 0");
      return;
    }
    if (!formIngrediente.value.unidad_medida_id) {
      alert("La unidad de medida es requerida");
      return;
    }

    // Preparar datos para enviar al backend según el serializer
    const datosParaEnviar = {
      insumo_id: formIngrediente.value.insumo_id,
      cantidad: formIngrediente.value.cantidad,
      unidad_medida_id: formIngrediente.value.unidad_medida_id,
      detalle_id: formIngrediente.value.detalle_id,
    };

    let response;
    if (esEdicionIngrediente.value) {
      response = await axios.put(
        `/api/ingredientes-extra/${formIngrediente.value.id}/`,
        datosParaEnviar
      );
    } else {
      response = await axios.post("/api/ingredientes-extra/", datosParaEnviar);
    }

    // Actualizar el pedido localmente
    await fetchPedidos();
    closeModal();
    alert(
      esEdicionIngrediente.value
        ? "Ingrediente extra actualizado correctamente"
        : "Ingrediente extra agregado correctamente"
    );
  } catch (error) {
    console.error("Error al guardar ingrediente extra:", error);
    console.error("Datos enviados:", error.config?.data);
    console.error("Respuesta del servidor:", error.response?.data);

    let mensajeError = "Error al guardar el ingrediente extra";
    if (error.response?.data) {
      if (typeof error.response.data === "object") {
        mensajeError += ": " + JSON.stringify(error.response.data);
      } else {
        mensajeError += ": " + error.response.data;
      }
    }
    alert(mensajeError);
  }
};

const closeModal = () => {
  showModalPedido.value = false;
  showNuevoClienteModal.value = false;
  showModalReceta.value = false;
  showModalIngrediente.value = false;
  resetForms();
};

const resetFormPedido = () => {
  formPedido.value = {
    id: null,
    cliente_id: "",
    fecha_pedido: new Date().toISOString().split("T")[0],
    fecha_entrega: "",
    estado: "pendiente",
  };
};

const resetFormCliente = () => {
  formCliente.value = {
    nombre: "",
    telefono: "",
    direccion: "",
  };
};

const resetFormDetalle = () => {
  formDetalle.value = {
    id: null,
    pedido_id: null,
    receta_id: "",
    cantidad: 1,
    observaciones: "",
  };
};

const resetFormIngrediente = () => {
  formIngrediente.value = {
    id: null,
    detalle_id: null,
    insumo_id: "",
    cantidad: 0,
    unidad_medida_id: "",
  };
};

// Nuevos métodos para gestionar recetas
const showAgregarRecetaModal = (pedido) => {
  esEdicionReceta.value = false;
  pedidoActual.value = pedido;
  resetFormDetalle();
  formDetalle.value.pedido_id = pedido.id;
  showModalReceta.value = true;
};

const editarReceta = (detalle, pedido) => {
  esEdicionReceta.value = true;
  pedidoActual.value = pedido;
  formDetalle.value = {
    id: detalle.id,
    pedido_id: pedido.id,
    receta_id: detalle.receta.id,
    cantidad: detalle.cantidad,
    observaciones: detalle.observaciones || "",
  };
  showModalReceta.value = true;
};

const confirmarEliminarReceta = (detalle) => {
  recetaAEliminar.value = detalle;
  showConfirmModalReceta.value = true;
};

const eliminarReceta = async () => {
  try {
    await axios.delete(`/api/detalles-pedido/${recetaAEliminar.value.id}/`);

    // Actualizar la lista local
    const pedidoIndex = pedidos.value.findIndex((pedido) =>
      pedido.detalles.some((detalle) => detalle.id === recetaAEliminar.value.id)
    );

    if (pedidoIndex !== -1) {
      const pedido = pedidos.value[pedidoIndex];
      const detalleIndex = pedido.detalles.findIndex(
        (detalle) => detalle.id === recetaAEliminar.value.id
      );
      if (detalleIndex !== -1) {
        pedido.detalles.splice(detalleIndex, 1);
      }
    }

    showConfirmModalReceta.value = false;
    alert("Receta eliminada correctamente del pedido");
  } catch (error) {
    console.error("Error al eliminar receta:", error);
    alert("Error al eliminar la receta del pedido");
  }
};

const guardarDetalle = async () => {
  try {
    if (!formDetalle.value.receta_id) {
      alert("La receta es requerida");
      return;
    }
    if (!formDetalle.value.cantidad || formDetalle.value.cantidad <= 0) {
      alert("La cantidad debe ser mayor a 0");
      return;
    }

    // Preparar datos para enviar al backend
    const datosParaEnviar = {
      pedido: formDetalle.value.pedido_id,
      receta_id: formDetalle.value.receta_id,
      cantidad: formDetalle.value.cantidad,
      observaciones: formDetalle.value.observaciones || "",
    };

    let response;
    if (esEdicionReceta.value) {
      response = await axios.put(
        `/api/detalles-pedido/${formDetalle.value.id}/`,
        datosParaEnviar
      );
    } else {
      response = await axios.post("/api/detalles-pedido/", datosParaEnviar);
    }

    // Actualizar el pedido localmente
    await fetchPedidos();
    closeModal();
    alert(
      esEdicionReceta.value
        ? "Receta actualizada correctamente"
        : "Receta agregada correctamente al pedido"
    );
  } catch (error) {
    console.error("Error al guardar detalle:", error);
    console.error("Datos enviados:", error.config?.data);
    console.error("Respuesta del servidor:", error.response?.data);

    let mensajeError = "Error al guardar la receta en el pedido";
    if (error.response?.data) {
      if (typeof error.response.data === "object") {
        mensajeError += ": " + JSON.stringify(error.response.data);
      } else {
        mensajeError += ": " + error.response.data;
      }
    }
    alert(mensajeError);
  }
};

const resetForms = () => {
  resetFormPedido();
  resetFormCliente();
  resetFormDetalle();
  resetFormIngrediente();
  esEdicionPedido.value = false;
  esEdicionReceta.value = false;
  esEdicionIngrediente.value = false;
  detalleActual.value = null;
  pedidoActual.value = null;
};

// Funciones para cargar datos
const fetchPedidos = async () => {
  try {
    loading.value = true;
    const response = await axios.get("/api/pedidos/");
    pedidos.value = response.data;
    loading.value = false;
  } catch (err) {
    console.error("Error en fetchPedidos:", err);
    loading.value = false;
    if (err.response?.status === 401) {
      logout();
    }
  }
};

const fetchClientes = async () => {
  try {
    const response = await axios.get("/api/clientes/");
    clientes.value = response.data;
  } catch (err) {
    console.error("Error en fetchClientes:", err);
  }
};

const fetchRecetas = async () => {
  try {
    const response = await axios.get("/api/recetas/");
    recetas.value = response.data;
  } catch (err) {
    console.error("Error en fetchRecetas:", err);
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

  // Cargar datos del usuario y pedidos
  Promise.all([
    axios.get("/api/auth/perfil/").then((res) => {
      userEmail.value = res.data.email || "Usuario";
    }),
    fetchPedidos(),
    fetchClientes(),
    fetchRecetas(),
    fetchInsumos(),
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
.pedidos-content {
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

.filtro-input,
.filtro-select {
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

/* ----------------------------- CARD DE PEDIDOS ----------------------------- */
.pedidos-card {
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

.cliente-nombre {
  font-weight: bold;
  font-size: 16px;
  color: #333;
}

.pedido-estado {
  font-size: 14px;
  padding: 3px 8px;
  border-radius: 12px;
  font-weight: normal;
}

.pedido-estado.pendiente {
  background-color: #fff3cd;
  color: #856404;
}

.pedido-estado.enpreparación {
  background-color: #d1ecf1;
  color: #0c5460;
}

.pedido-estado.entregado {
  background-color: #d4edda;
  color: #155724;
}

.pedido-estado.cancelado {
  background-color: #f8d7da;
  color: #721c24;
}

.pedido-fechas {
  font-size: 14px;
  color: #666;
}

.pedido-total {
  font-size: 14px;
  color: #2e7d32;
  font-weight: bold;
}

.pedido-acciones {
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

/* ----------------------------- RECETAS E INGREDIENTES ----------------------------- */
.recetas-container {
  margin-top: 15px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.receta-item {
  margin-bottom: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.receta-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f5f5f5;
  cursor: pointer;
}

.receta-nombre {
  font-weight: bold;
}

.receta-precio {
  font-weight: bold;
  color: #2e7d32;
}

.receta-detalles {
  padding: 10px;
  background-color: #fff;
}

.observaciones {
  margin-bottom: 10px;
  font-style: italic;
  color: #666;
}

.ingredientes-extras {
  margin-top: 10px;
}

.ingredientes-extras h4 {
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.ingrediente-extra {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px dashed #eee;
}

.ingrediente-acciones {
  display: flex;
  gap: 5px;
}

.btn-accion-small {
  background: none;
  border: none;
  cursor: pointer;
  color: #7b5a50;
  font-size: 12px;
  padding: 2px 5px;
}

.btn-accion-small:hover {
  color: #5a3f36;
}

.receta-acciones {
  margin-top: 10px;
  text-align: right;
}

.btn-agregar-ingrediente {
  background-color: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-agregar-ingrediente:hover {
  background-color: #bbdefb;
}

/* Nuevos estilos para el botón de agregar receta */
.agregar-receta-container {
  margin: 15px 0;
  text-align: center;
}

.btn-agregar-receta {
  background-color: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
}

.btn-agregar-receta:hover {
  background-color: #bbdefb;
}

/* Estilos para los botones de acción en recetas */
.receta-acciones-superiores {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  justify-content: flex-end;
}

.btn-accion-small {
  background: none;
  border: 1px solid #ddd;
  cursor: pointer;
  color: #7b5a50;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-accion-small:hover {
  background-color: #f5f5f5;
}

.btn-eliminar {
  color: #dc3545;
  border-color: #f5c6cb;
}

.btn-eliminar:hover {
  background-color: #f8d7da;
}

/* Ajustes para el modal de recetas */
.modal-content {
  max-width: 500px;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group.full-width {
  width: 100%;
}

/* ----------------------------- MODALES ----------------------------- */
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

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #5a3f36;
  text-align: center;
}

.form-grid {
  display: flex;
  flex-direction: column;
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
  color: #333;
}

.form-input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.cliente-select-container {
  display: flex;
  gap: 5px;
}

.btn-agregar-cliente {
  background-color: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
  border-radius: 4px;
  cursor: pointer;
  padding: 0 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-agregar-cliente:hover {
  background-color: #bbdefb;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ccc;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-button:hover {
  background-color: #e0e0e0;
}

.confirm-button {
  background-color: #b8e6b8;
  color: #2b5d2b;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.confirm-button:hover {
  background-color: #a1dca1;
}

/* ----------------------------- ESTADOS ----------------------------- */
.loading-state,
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.loading-state i {
  margin-right: 10px;
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .filtros-derecha {
    flex-direction: column;
    align-items: stretch;
  }

  .pedido-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .pedido-acciones {
    align-self: flex-end;
  }
}
</style>
