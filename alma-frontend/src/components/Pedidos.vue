<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header :userEmail="userEmail" title="Gestión de Pedidos" @openPasswordModal="showPasswordModal = true"
        @logout="logout" />
      <main class="main-content">

        <section class="content pedidos-content">
          <h3 class="card-title1">Gestión de Pedidos</h3>
          <div class="botones-acciones">
            <button class="btn-nuevo-pedido" @click="abrirModalCrear">
              <i class="bi bi-plus-lg"></i> Nuevo Pedido
            </button>
          </div>
          <!-- Filtros de pedidos -->
          <div class="filtros-pedidos">
            <div class="filtro-group">
              <label for="fecha-filtro">Filtrar por fecha:</label>
              <input type="date" id="fecha-filtro" v-model="fechaFiltro" @change="filtrarPorFecha" />
            </div>

            <div class="filtro-group">
              <label for="estado-filtro">Filtrar por estado:</label>
              <select id="estado-filtro" v-model="estadoFiltro" @change="filtrarPorEstado">
                <option value="">Todos los estados</option>
                <option v-for="estado in estadosPedido" :key="estado" :value="estado">
                  {{ estado }}
                </option>
              </select>
            </div>
          </div>
        </section>

        <!-- Card principal de pedidos -->
        <div class="card pedidos-card">

          <div v-if="loadingPedidos" class="loading-state">
            <i class="fas fa-spinner fa-spin"></i> Cargando pedidos...
          </div>

          <div v-else-if="pedidosFiltrados.length === 0" class="empty-state">
            No hay pedidos que coincidan con los filtros seleccionados
          </div>

          <div v-else class="pedidos-list">
            <div v-for="pedido in pedidosFiltrados" :key="pedido.id" class="pedido-item">
              <div class="pedido-header">
                <div class="pedido-info">
                  <span class="pedido-id">#{{ pedido.id }}</span>
                  <span class="cliente-nombre">{{
                    pedido.cliente.nombre
                  }}</span>
                  <span class="pedido-fecha">Entrega: {{ formatDate(pedido.fecha_entrega) }}</span>
                  <span class="pedido-fecha">Fabricación:
                    {{ formatDate(pedido.fecha_fabricacion) }}</span>
                </div>
                <div class="pedido-acciones">
                  <span class="estado-badge" :class="pedido.estado">{{
                    pedido.estado
                  }}</span>
                  <button class="btn-accion" @click="abrirModalEditar(pedido)" title="Editar pedido">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn-accion" @click="eliminarPedido(pedido.id)" title="Eliminar pedido">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>

              <div class="pedido-detalles">
                <div v-for="detalle in pedido.detalles" :key="detalle.id" class="detalle-item">
                  <span>{{ detalle.receta.nombre }} (x{{ detalle.cantidad }})</span>
                  <span>{{
                    formatDecimal(detalle.precio * detalle.cantidad)
                  }}</span>
                </div>

                <div v-if="
                  pedido.ingredientes_extra &&
                  pedido.ingredientes_extra.length > 0
                " class="ingredientes-extra">
                  <p><strong>Ingredientes extra:</strong></p>
                  <ul>
                    <li v-for="extra in pedido.ingredientes_extra" :key="extra.id">
                      {{ extra.insumo.nombre }}:
                      {{ formatDecimal(extra.cantidad) }}
                      {{ extra.insumo.unidad_medida.abreviatura }}
                    </li>
                  </ul>
                </div>

                <div class="pedido-total">
                  <strong>Total: {{ formatDecimal(pedido.total) }}</strong>
                </div>
              </div>

              <div class="estado-actions">
                <button v-if="pedido.estado === 'pendiente'"
                  @click="actualizarEstadoPedido(pedido.id, 'en preparación')" class="btn-estado">
                  Marcar como en preparación
                </button>
                <button v-if="pedido.estado === 'en preparación'"
                  @click="actualizarEstadoPedido(pedido.id, 'entregado')" class="btn-estado">
                  Marcar como entregado
                </button>
              </div>
            </div>
          </div>
        </div>

      </main>
    </div>

    <!-- Modal para crear/editar pedido -->
    <div v-if="showPedidoModal" class="modal-overlay">
      <div class="modal-content modal-grande">
        <h3>{{ esEdicion ? "Editar Pedido" : "Crear Nuevo Pedido" }}</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Cliente:</label>
            <div class="cliente-select-container">
              <select v-model="pedidoForm.cliente" required>
                <option value="">Seleccione un cliente</option>
                <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                  {{ cliente.nombre }}
                </option>
              </select>
              <button type="button" class="btn-agregar-cliente" @click="mostrarModalCliente"
                title="Agregar nuevo cliente">
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Fecha de entrega:</label>
            <input type="date" v-model="pedidoForm.fecha_entrega" required />
          </div>

          <div class="form-group">
            <label>Fecha de fabricación:</label>
            <input type="date" v-model="pedidoForm.fecha_fabricacion" required />
          </div>

          <div class="form-group">
            <label>Estado:</label>
            <select v-model="pedidoForm.estado" required>
              <option v-for="estado in estadosPedido" :key="estado" :value="estado">
                {{ estado }}
              </option>
            </select>
          </div>
        </div>

        <div class="seccion-detalles">
          <h4>Detalles del Pedido</h4>

          <div class="nuevo-detalle">
            <select v-model="nuevaReceta" class="select-receta">
              <option value="">Seleccione una receta</option>
              <option v-for="receta in recetas" :key="receta.id" :value="receta">
                {{ receta.nombre }} - {{ formatDecimal(receta.precio) }}
              </option>
            </select>
            <input type="number" v-model="nuevaCantidad" min="1" placeholder="Cantidad" class="input-cantidad" />
            <button @click="agregarDetalle" class="btn-agregar" :disabled="!nuevaReceta || !nuevaCantidad">
              <i class="fas fa-plus"></i> Agregar
            </button>
          </div>

          <div class="lista-detalles">
            <div v-for="(detalle, index) in pedidoForm.detalles" :key="index" class="detalle-item-modal">
              <span>{{ detalle.receta.nombre }} x{{ detalle.cantidad }}</span>
              <span>{{
                formatDecimal(detalle.precio * detalle.cantidad)
              }}</span>
              <button @click="eliminarDetalle(index)" class="btn-eliminar-detalle">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="seccion-ingredientes-extra">
          <h4>Ingredientes Extra</h4>

          <div class="nuevo-ingrediente">
            <select v-model="nuevoIngrediente.insumo" class="select-insumo">
              <option value="">Seleccione un ingrediente</option>
              <option v-for="insumo in insumos" :key="insumo.id" :value="insumo">
                {{ insumo.nombre }} ({{ insumo.unidad_medida.abreviatura }})
              </option>
            </select>
            <input type="number" v-model="nuevoIngrediente.cantidad" min="0.1" step="0.1" placeholder="Cantidad"
              class="input-cantidad" />

            <!-- Selector de unidad de medida -->
            <select v-model="nuevoIngrediente.unidad_medida" class="select-unidad" v-if="nuevoIngrediente.insumo">
              <option value="">Seleccione unidad</option>
              <option v-for="unidad in unidadesCompatibles" :key="unidad.id" :value="unidad">
                {{ unidad.abreviatura }}
              </option>
            </select>

            <button @click="agregarIngredienteExtra" class="btn-agregar" :disabled="!nuevoIngrediente.insumo ||
              !nuevoIngrediente.cantidad ||
              !nuevoIngrediente.unidad_medida
              ">
              <i class="fas fa-plus"></i> Agregar
            </button>
          </div>

          <div class="lista-ingredientes">
            <div v-for="(ingrediente, index) in pedidoForm.ingredientes_extra" :key="index" class="ingrediente-item">
              <span>
                {{ obtenerNombreInsumo(ingrediente.insumo) }}:
                {{ formatDecimal(ingrediente.cantidad) }}
                {{ ingrediente.unidad_medida_nombre }}
                <small v-if="
                  ingrediente.cantidad_convertida &&
                  ingrediente.cantidad_convertida !== ingrediente.cantidad
                ">
                  (≈ {{ formatDecimal(ingrediente.cantidad_convertida) }}
                  {{ ingrediente.unidad_base }})
                </small>
              </span>
              <button @click="eliminarIngredienteExtra(index)" class="btn-eliminar-detalle">
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="total-pedido">
          <strong>Total: {{ formatDecimal(calcularTotal) }}</strong>
        </div>

        <div class="modal-buttons">
          <button @click="cerrarModal" class="cancel-button">Cancelar</button>
          <button @click="guardarPedido" class="confirm-button" :disabled="!pedidoValido">
            {{ esEdicion ? "Actualizar" : "Crear" }}
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
  <!-- Modal para agregar nuevo cliente -->
  <div v-if="showClienteModal" class="modal-overlay">
    <div class="modal-content">
      <h3>Agregar Nuevo Cliente</h3>

      <div class="form-group">
        <label>Nombre:</label>
        <input type="text" v-model="nuevoCliente.nombre" required />
      </div>

      <div class="form-group">
        <label>Teléfono:</label>
        <input type="text" v-model="nuevoCliente.telefono" />
      </div>

      <div class="form-group">
        <label>Dirección:</label>
        <input type="text" v-model="nuevoCliente.direccion" required />
      </div>

      <div class="modal-buttons">
        <button @click="cerrarModalCliente" class="cancel-button">
          Cancelar
        </button>
        <button @click="guardarCliente" class="confirm-button">Guardar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatDecimal } from "../helpers/formatters";
import { onMounted, ref, computed, inject, watch } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";

const router = useRouter();
const notificationSystem = inject("notifications");

const handleNavigation = (route) => {
  router.push(route);
};

// ----------------------
// 🔹 Estado del Menú y Usuario
// ----------------------
const showPasswordModal = ref(false);
const userEmail = ref("Usuario");
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

// ----------------------
// 🔹 Gestión de Pedidos
// ----------------------
const pedidos = ref([]);
const loadingPedidos = ref(true);
const fechaFiltro = ref("");
const estadoFiltro = ref("");
const estadosPedido = ["pendiente", "en preparación", "entregado", "cancelado"];

// Computed para filtrar pedidos
const pedidosFiltrados = computed(() => {
  let filtered = [...pedidos.value];

  // Filtrar por fecha si hay selección
  if (fechaFiltro.value) {
    filtered = filtered.filter(
      (pedido) =>
        pedido.fecha_entrega === fechaFiltro.value ||
        pedido.fecha_fabricacion === fechaFiltro.value
    );
  }

  // Filtrar por estado si hay selección
  if (estadoFiltro.value) {
    filtered = filtered.filter(
      (pedido) => pedido.estado === estadoFiltro.value
    );
  }

  return filtered.sort(
    (a, b) => new Date(b.fecha_pedido) - new Date(a.fecha_pedido)
  );
});

// ----------------------
// 🔹 Modal de Pedido
// ----------------------
const showPedidoModal = ref(false);
const esEdicion = ref(false);
const pedidoEditandoId = ref(null);

// Datos para el formulario de pedido
const pedidoForm = ref({
  cliente: "",
  fecha_entrega: "",
  fecha_fabricacion: "",
  estado: "pendiente",
  detalles: [],
  ingredientes_extra: [],
});

const nuevaReceta = ref(null);
const nuevaCantidad = ref(1);
const unidadesDisponibles = ref([]);
const nuevoIngrediente = ref({
  insumo: "",
  cantidad: 0.1,
  unidad_medida: "",
});

// Listas de opciones
const clientes = ref([]);
const recetas = ref([]);
const insumos = ref([]);

// Computed properties
const pedidoValido = computed(() => {
  return (
    pedidoForm.value.cliente &&
    pedidoForm.value.fecha_entrega &&
    pedidoForm.value.fecha_fabricacion &&
    pedidoForm.value.detalles.length > 0
  );
});

const calcularTotal = computed(() => {
  let total = 0;

  // Sumar total de detalles
  pedidoForm.value.detalles.forEach((detalle) => {
    total += (detalle.precio || detalle.receta.precio) * detalle.cantidad;
  });

  // Sumar costo aproximado de ingredientes extra (opcional)
  pedidoForm.value.ingredientes_extra.forEach((ingrediente) => {
    const insumo = insumos.value.find((i) => i.id === ingrediente.insumo);
    if (insumo && insumo.precio_por_unidad) {
      total += insumo.precio_por_unidad * ingrediente.cantidad;
    }
  });

  return total;
});

// ----------------------
// 🔹 Modal de Clientes
// ----------------------
const showClienteModal = ref(false);
const nuevoCliente = ref({
  nombre: "",
  telefono: "",
  direccion: "",
});

// Función para mostrar el modal de cliente
const mostrarModalCliente = () => {
  showClienteModal.value = true;
};

// Función para cerrar el modal de cliente
const cerrarModalCliente = () => {
  showClienteModal.value = false;
  // Limpiar el formulario
  nuevoCliente.value = {
    nombre: "",
    telefono: "",
    direccion: "",
  };
};

// Función para guardar un nuevo cliente
const guardarCliente = async () => {
  try {
    // Validar campos obligatorios
    if (!nuevoCliente.value.nombre || !nuevoCliente.value.direccion) {
      notificationSystem.show({
        type: "warning",
        title: "Campos incompletos",
        message: "Nombre y dirección son campos obligatorios",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.post("/api/clientes/", nuevoCliente.value);

    notificationSystem.show({
      type: "success",
      title: "Cliente agregado",
      message: "El cliente se ha agregado correctamente",
      timeout: 4000,
    });

    // Agregar el nuevo cliente a la lista y seleccionarlo
    clientes.value.push(response.data.cliente);
    pedidoForm.value.cliente = response.data.cliente.id;

    // Cerrar el modal
    cerrarModalCliente();
  } catch (err) {
    console.error("Error al guardar cliente:", err);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "No se pudo guardar el cliente",
      timeout: 4000,
    });
  }
};
// ----------------------
// 🔹 Funciones de Pedidos
// ----------------------
const fetchPedidos = async () => {
  try {
    loadingPedidos.value = true;
    const response = await axios.get("/api/pedidos/");
    pedidos.value = response.data;
  } catch (err) {
    console.error("Error fetching pedidos:", err);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "No se pudieron cargar los pedidos",
      timeout: 4000,
    });
  } finally {
    loadingPedidos.value = false;
  }
};

const fetchClientes = async () => {
  try {
    const response = await axios.get("/api/clientes/");
    clientes.value = response.data;
  } catch (err) {
    console.error("Error fetching clientes:", err);
  }
};

const fetchRecetas = async () => {
  try {
    const response = await axios.get("/api/recetas/");
    recetas.value = response.data;
  } catch (err) {
    console.error("Error fetching recetas:", err);
  }
};

const fetchInsumos = async () => {
  try {
    const response = await axios.get("/api/insumos/");
    insumos.value = response.data.insumos || response.data;
  } catch (err) {
    console.error("Error fetching insumos:", err);
  }
};

// Función para obtener unidades de medida disponibles
const fetchUnidadesMedida = async () => {
  try {
    const response = await axios.get("/api/unidades-medida/");
    unidadesDisponibles.value = response.data;
  } catch (err) {
    console.error("Error fetching unidades de medida:", err);
  }
};

// Computed para obtener unidades compatibles con el insumo seleccionado
const unidadesCompatibles = computed(() => {
  if (!nuevoIngrediente.value.insumo) return [];

  const insumoUnidad =
    nuevoIngrediente.value.insumo.unidad_medida.abreviatura.toLowerCase();

  // Definir grupos de unidades compatibles
  const gruposCompatibles = {
    peso: ["kg", "g", "mg"],
    volumen: ["l", "ml", "cl"],
    unidad: ["u", "pz", "unidad"],
  };

  // Encontrar el grupo del insumo
  const grupoInsumo = Object.keys(gruposCompatibles).find((grupo) =>
    gruposCompatibles[grupo].includes(insumoUnidad)
  );

  if (!grupoInsumo) return [nuevoIngrediente.value.insumo.unidad_medida];

  // Filtrar unidades que pertenezcan al mismo grupo
  return unidadesDisponibles.value.filter((unidad) =>
    gruposCompatibles[grupoInsumo].includes(unidad.abreviatura.toLowerCase())
  );
});

const filtrarPorFecha = () => {
  // El filtrado se realiza automáticamente a través del computed
};

const filtrarPorEstado = () => {
  // El filtrado se realiza automáticamente a través del computed
};

const actualizarEstadoPedido = async (pedidoId, nuevoEstado) => {
  try {
    await axios.patch(`/api/pedidos/${pedidoId}/actualizar-estado/`, {
      estado: nuevoEstado,
    });

    notificationSystem.show({
      type: "success",
      title: "Estado actualizado",
      message: "El estado del pedido se ha actualizado correctamente",
      timeout: 4000,
    });

    // Actualizar la lista de pedidos
    await fetchPedidos();
  } catch (err) {
    console.error("Error al actualizar estado:", err);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message:
        err.response?.data?.error || "Error al actualizar el estado del pedido",
      timeout: 4000,
    });
  }
};

const abrirModalCrear = async () => {
  // Cargar datos necesarios si no están cargados
  if (clientes.value.length === 0) await fetchClientes();
  if (recetas.value.length === 0) await fetchRecetas();
  if (insumos.value.length === 0) await fetchInsumos();
  if (unidadesDisponibles.value.length === 0) {
    await fetchUnidadesMedida();
    // Asegurar que las unidades tengan unidad_base
    unidadesDisponibles.value.forEach((unidad) => {
      if (!unidad.unidad_base) {
        // Asignar unidad_base basado en la abreviatura
        const grupos = {
          peso: ["kg", "g", "mg"],
          volumen: ["l", "ml", "cl"],
          unidad: ["u", "pz", "unidad"],
        };
        for (const [grupo, unidades] of Object.entries(grupos)) {
          if (unidades.includes(unidad.abreviatura.toLowerCase())) {
            unidad.unidad_base = grupo;
            break;
          }
        }
      }
    });
  }

  // Resetear formulario
  pedidoForm.value = {
    cliente: "",
    fecha_entrega: new Date().toISOString().split("T")[0],
    fecha_fabricacion: new Date().toISOString().split("T")[0],
    estado: "pendiente",
    detalles: [],
    ingredientes_extra: [],
  };

  nuevaReceta.value = null;
  nuevaCantidad.value = 1;
  nuevoIngrediente.value = {
    insumo: "",
    cantidad: 0.1,
    unidad_medida: "", // ← Asegurar que se resetee
  };

  esEdicion.value = false;
  pedidoEditandoId.value = null;
  showPedidoModal.value = true;
};

const abrirModalEditar = async (pedido) => {
  // Cargar datos necesarios si no están cargados
  if (clientes.value.length === 0) await fetchClientes();
  if (recetas.value.length === 0) await fetchRecetas();
  if (insumos.value.length === 0) await fetchInsumos();
  if (unidadesDisponibles.value.length === 0) await fetchUnidadesMedida();

  // Llenar formulario con datos del pedido - CORREGIDO
  pedidoForm.value = {
    cliente: pedido.cliente.id,
    fecha_entrega: pedido.fecha_entrega,
    fecha_fabricacion: pedido.fecha_fabricacion,
    estado: pedido.estado,
    detalles: pedido.detalles.map((detalle) => ({
      receta: { ...detalle.receta },
      cantidad: detalle.cantidad,
      precio: detalle.precio, // ← Añadir precio
      observaciones: detalle.observaciones || "",
    })),
    ingredientes_extra: [],
  };

  // Cargar ingredientes extra si existen - CORREGIDO
  if (pedido.detalles && pedido.detalles.length > 0) {
    // Recorrer todos los detalles, no solo el primero
    for (const detalle of pedido.detalles) {
      if (detalle.ingredientes_extra && detalle.ingredientes_extra.length > 0) {
        pedidoForm.value.ingredientes_extra = [
          ...pedidoForm.value.ingredientes_extra,
          ...detalle.ingredientes_extra.map((ing) => ({
            insumo: ing.insumo.id,
            cantidad: ing.cantidad,
            unidad_medida: ing.unidad_medida?.id || null,
            unidad_medida_nombre: ing.unidad_medida?.abreviatura || "",
            insumo_nombre: ing.insumo.nombre,
          })),
        ];
      }
    }
  }

  nuevaReceta.value = null;
  nuevaCantidad.value = 1;
  nuevoIngrediente.value = {
    insumo: "",
    cantidad: 0.1,
    unidad_medida: "",
  };

  esEdicion.value = true;
  pedidoEditandoId.value = pedido.id;
  showPedidoModal.value = true;
};

const cerrarModal = () => {
  showPedidoModal.value = false;
};

const agregarDetalle = () => {
  if (!nuevaReceta.value || !nuevaCantidad.value || nuevaCantidad.value < 1)
    return;

  // Verificar si la receta ya está en los detalles
  const detalleExistente = pedidoForm.value.detalles.find(
    (d) => d.receta.id === nuevaReceta.value.id
  );

  if (detalleExistente) {
    // Si ya existe, aumentar la cantidad
    detalleExistente.cantidad += parseInt(nuevaCantidad.value);
  } else {
    // Si no existe, agregar nuevo detalle
    pedidoForm.value.detalles.push({
      receta: { ...nuevaReceta.value },
      cantidad: parseInt(nuevaCantidad.value),
      precio: nuevaReceta.value.precio,
    });
  }

  // Resetear valores
  nuevaReceta.value = null;
  nuevaCantidad.value = 1;
};

const eliminarDetalle = (index) => {
  pedidoForm.value.detalles.splice(index, 1);
};

const agregarIngredienteExtra = () => {
  if (
    !nuevoIngrediente.value.insumo ||
    !nuevoIngrediente.value.cantidad ||
    !nuevoIngrediente.value.unidad_medida
  )
    return;

  // Validar compatibilidad de unidades
  const esCompatible = verificarCompatibilidadUnidades(
    nuevoIngrediente.value.insumo.id,
    nuevoIngrediente.value.unidad_medida.id
  );

  if (!esCompatible) {
    const insumo = nuevoIngrediente.value.insumo;
    const unidad = nuevoIngrediente.value.unidad_medida;

    notificationSystem.show({
      type: "error",
      title: "Unidades incompatibles",
      message: `No puedes usar ${unidad.abreviatura} con ${insumo.unidad_medida.abreviatura}. Las unidades deben ser del mismo tipo (peso, volumen, unidad).`,
      timeout: 5000,
    });
    return;
  }

  // Calcular conversión para mostrar (opcional)
  const cantidadConvertida = convertirUnidad(
    parseFloat(nuevoIngrediente.value.cantidad),
    nuevoIngrediente.value.unidad_medida.abreviatura,
    nuevoIngrediente.value.insumo.unidad_medida.abreviatura
  );

  pedidoForm.value.ingredientes_extra.push({
    insumo: nuevoIngrediente.value.insumo.id,
    cantidad: parseFloat(nuevoIngrediente.value.cantidad),
    unidad_medida: nuevoIngrediente.value.unidad_medida.id,
    unidad_medida_nombre: nuevoIngrediente.value.unidad_medida.abreviatura,
    insumo_nombre: nuevoIngrediente.value.insumo.nombre,
    // Información adicional para mostrar
    cantidad_convertida: cantidadConvertida,
    unidad_base: nuevoIngrediente.value.insumo.unidad_medida.abreviatura,
  });

  // Resetear valores
  nuevoIngrediente.value = {
    insumo: "",
    cantidad: 0.1,
    unidad_medida: "",
  };
};

// Función para verificar compatibilidad de unidades
const verificarCompatibilidadUnidades = (insumoId, unidadMedidaId) => {
  const insumo = insumos.value.find((i) => i.id === insumoId);
  const unidadSeleccionada = unidadesDisponibles.value.find(
    (u) => u.id === unidadMedidaId
  );

  if (!insumo || !unidadSeleccionada) return false;

  const unidadBaseInsumo = insumo.unidad_medida.abreviatura.toLowerCase();
  const unidadSeleccionadaAbr = unidadSeleccionada.abreviatura.toLowerCase();

  // Definir grupos de unidades compatibles
  const gruposCompatibles = {
    peso: ["kg", "g", "mg"],
    volumen: ["l", "ml", "cl"],
    unidad: ["u", "pz", "unidad"],
  };

  // Encontrar a qué grupo pertenece cada unidad
  const grupoInsumo = Object.keys(gruposCompatibles).find((grupo) =>
    gruposCompatibles[grupo].includes(unidadBaseInsumo)
  );

  const grupoSeleccionado = Object.keys(gruposCompatibles).find((grupo) =>
    gruposCompatibles[grupo].includes(unidadSeleccionadaAbr)
  );

  return grupoInsumo === grupoSeleccionado;
};
// Función para convertir unidades en el frontend (opcional, para mostrar)
const convertirUnidad = (cantidad, unidadOrigen, unidadDestino) => {
  const conversiones = {
    kg: { g: 1000, mg: 1000000 },
    g: { kg: 0.001, mg: 1000 },
    mg: { kg: 0.000001, g: 0.001 },
    l: { ml: 1000, cl: 100 },
    ml: { l: 0.001, cl: 0.1 },
    cl: { l: 0.01, ml: 10 },
  };

  if (unidadOrigen === unidadDestino) return cantidad;

  if (conversiones[unidadOrigen] && conversiones[unidadOrigen][unidadDestino]) {
    return cantidad * conversiones[unidadOrigen][unidadDestino];
  }

  return cantidad; // Si no hay conversión, devolver original
};

const eliminarIngredienteExtra = (index) => {
  pedidoForm.value.ingredientes_extra.splice(index, 1);
};

const obtenerNombreInsumo = (insumoId) => {
  const insumo = insumos.value.find((i) => i.id === insumoId);
  return insumo ? insumo.nombre : "Insumo desconocido";
};

const obtenerUnidadInsumo = (insumoId) => {
  const insumo = insumos.value.find((i) => i.id === insumoId);
  return insumo ? insumo.unidad_medida.abreviatura : "u";
};

const guardarPedido = async () => {
  try {
    // 1. Primero crear el pedido básico
    const datosPedido = {
      cliente_id: pedidoForm.value.cliente,
      fecha_pedido: new Date().toISOString().split("T")[0],
      fecha_entrega: pedidoForm.value.fecha_entrega,
      fecha_fabricacion: pedidoForm.value.fecha_fabricacion,
      estado: pedidoForm.value.estado,
    };

    console.log("Creando pedido básico:", datosPedido);

    let response;
    let pedidoId;

    if (esEdicion.value) {
      // Actualizar pedido existente
      response = await axios.put(
        `/api/pedidos/${pedidoEditandoId.value}/`,
        datosPedido
      );
      pedidoId = response.data.pedido.id;
    } else {
      // Crear nuevo pedido
      response = await axios.post("/api/pedidos/", datosPedido);
      pedidoId = response.data.id || response.data.pedido?.id;
    }

    console.log("Pedido creado/actualizado con ID:", pedidoId);

    // 2. Eliminar detalles existentes si es edición
    if (esEdicion.value) {
      try {
        await axios.delete(`/api/pedidos/${pedidoId}/detalles/`);
        console.log("Detalles anteriores eliminados");
      } catch (deleteError) {
        console.warn(
          "No se pudieron eliminar detalles anteriores:",
          deleteError
        );
      }
    }

    // 3. Agregar los nuevos detalles del pedido (recetas)
    for (const detalle of pedidoForm.value.detalles) {
      const detalleData = {
        pedido_id: pedidoId,
        receta_id: detalle.receta.id,
        cantidad: detalle.cantidad,
        observaciones: detalle.observaciones || "",
      };

      console.log("Agregando detalle:", detalleData);

      const detalleResponse = await axios.post(
        "/api/detalles-pedido/",
        detalleData
      );
      const detalleId =
        detalleResponse.data.id || detalleResponse.data.detalle?.id;

      console.log("Respuesta completa del detalle:", detalleResponse.data);
      console.log("Detalle creado con ID:", detalleId);

      // 4. Agregar ingredientes extra para este detalle (si existen)
      if (
        pedidoForm.value.ingredientes_extra &&
        pedidoForm.value.ingredientes_extra.length > 0
      ) {
        for (const [
          index,
          ingrediente,
        ] of pedidoForm.value.ingredientes_extra.entries()) {
          if (!detalleId) {
            console.error("Error: detalleId es null/undefined");
            continue;
          }

          const ingredienteData = {
            detalle_id: detalleId,
            insumo_id: ingrediente.insumo,
            cantidad: ingrediente.cantidad,
            unidad_medida_id: ingrediente.unidad_medida,
          };

          console.log(
            `Agregando ingrediente extra ${index + 1}:`,
            ingredienteData
          );

          try {
            const response = await axios.post(
              "/api/ingredientes-extra/",
              ingredienteData
            );
            console.log(
              "Ingrediente extra guardado exitosamente:",
              response.data
            );
          } catch (ingError) {
            console.error(
              "Error completo al guardar ingrediente extra:",
              ingError
            );
            console.error("Datos del error:", ingError.response?.data);
            console.error(
              "Configuración de la request:",
              ingError.config?.data
            );
          }
        }
      }
    }

    notificationSystem.show({
      type: "success",
      title: esEdicion.value ? "Pedido actualizado" : "Pedido creado",
      message: `El pedido se ha ${esEdicion.value ? "actualizado" : "creado"
        } correctamente`,
      timeout: 4000,
    });

    // Cerrar modal y actualizar lista
    cerrarModal();
    await fetchPedidos();
  } catch (err) {
    console.error("Error al guardar pedido:", err);
    if (err.response?.data) {
      console.error("Detalles del error:", err.response.data);

      let errorMessage = "Error al guardar el pedido";
      if (err.response.data.non_field_errors) {
        errorMessage = err.response.data.non_field_errors.join(", ");
      } else if (err.response.data.detail) {
        errorMessage = err.response.data.detail;
      }

      notificationSystem.show({
        type: "error",
        title: "Error",
        message: errorMessage,
        timeout: 6000,
      });
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error de conexión al guardar el pedido",
        timeout: 4000,
      });
    }
  }
};
const eliminarPedido = async (id) => {
  if (!confirm("¿Está seguro de que desea eliminar este pedido?")) {
    return;
  }

  try {
    await axios.delete(`/api/pedidos/${id}/`);

    notificationSystem.show({
      type: "success",
      title: "Pedido eliminado",
      message: "El pedido se ha eliminado correctamente",
      timeout: 4000,
    });

    // Actualizar la lista de pedidos
    await fetchPedidos();
  } catch (err) {
    console.error("Error al eliminar pedido:", err);
    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "No se pudo eliminar el pedido",
      timeout: 4000,
    });
  }
};

// ----------------------
// 🔹 Funciones de Usuario
// ----------------------
const openChangePassword = () => {
  showPasswordModal.value = true;
};

const changePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    notificationSystem.show({
      type: "warning",
      title: "Contraseñas no coinciden",
      message: "Las contraseñas ingresadas no son iguales",
      timeout: 4000,
    });
    return;
  }

  try {
    await axios.post("/api/auth/change-password/", {
      old_password: currentPassword.value,
      new_password1: newPassword.value,
      new_password2: confirmPassword.value,
    });

    notificationSystem.show({
      type: "success",
      title: "¡Contraseña cambiada!",
      message: "Tu contraseña ha sido actualizada exitosamente",
      timeout: 4000,
    });
    showPasswordModal.value = false;
    currentPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  } catch (error) {
    console.error("Error al cambiar contraseña:", error);

    let errorMessage = "Error al cambiar la contraseña";
    if (error.response?.data?.errors) {
      errorMessage = Object.values(error.response.data.errors)
        .flat()
        .join("\n");
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }

    alert(errorMessage);
  }
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

// ----------------------
// 🔹 Utilidades
// ----------------------
// Funciones de utilidad para conversiones
const mostrarConversion = (ingrediente) => {
  const insumo = insumos.value.find((i) => i.id === ingrediente.insumo);
  if (!insumo) return false;

  const unidadSeleccionada = unidadesDisponibles.value.find(
    (u) => u.id === ingrediente.unidad_medida
  );
  if (!unidadSeleccionada) return false;

  return unidadSeleccionada.abreviatura !== insumo.unidad_medida.abreviatura;
};

const calcularConversion = (ingrediente) => {
  const insumo = insumos.value.find((i) => i.id === ingrediente.insumo);
  const unidadSeleccionada = unidadesDisponibles.value.find(
    (u) => u.id === ingrediente.unidad_medida
  );

  if (!insumo || !unidadSeleccionada) return ingrediente.cantidad;

  // Aquí podrías implementar la lógica de conversión en el frontend
  // o simplemente mostrar la cantidad original ya que el backend hará la conversión real
  return ingrediente.cantidad;
};

const obtenerUnidadBase = (insumoId) => {
  const insumo = insumos.value.find((i) => i.id === insumoId);
  return insumo ? insumo.unidad_medida.abreviatura : "";
};
const formatDate = (dateString) => {
  if (!dateString) return "";
  const options = { day: "2-digit", month: "2-digit", year: "numeric" };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

// ----------------------
// 🔹 Montaje Inicial
// ----------------------
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  Promise.all([
    axios.get("/api/auth/perfil/").then((res) => {
      userEmail.value = res.data.email || "Usuario";
    }),
    fetchPedidos(),
    fetchClientes(), // Asegurarnos de cargar clientes
    fetchRecetas(),
    fetchInsumos(),
  ]).catch((error) => {
    console.error("Error cargando datos:", error);
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
  padding: 0 20px;
  display: flex;
}

.filtros-pedidos {
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

.filtro-group label {
  font-weight: bold;
  font-size: 14px;
}

.filtro-group input,
.filtro-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

/* BOTONEEES */

.botones-acciones {
  display: flex;
  gap: 10px;
  margin-right: auto;
  /* ← Esto los lleva a la izq */
  margin-bottom: 25px;
}

.botones-acciones button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

/* Colores pastel */
.btn-nuevo-pedido {
  background-color: #b8e6b8;
  /* verde clarito */
  color: #2b5d2b;
  padding: 4px 12px;
  /* menos alto */
  font-size: 0.875rem;
  /* texto más chico */
  height: 32px;
  /* altura fija */
  line-height: 1;
  /* centra el texto verticalmente */
  display: flex;
  align-items: center;
  /* icono y texto centrados */
  gap: 5px;
  border-radius: 6px;
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
}

.pedido-id {
  font-weight: bold;
  color: #7b5a50;
}

.cliente-nombre {
  font-weight: bold;
  font-size: 16px;
}

.pedido-fecha {
  font-size: 14px;
  color: #666;
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

.estado-badge.pendiente {
  background-color: #fff3cd;
  color: #856404;
}

.estado-badge.en.preparación {
  background-color: #d1ecf1;
  color: #0c5460;
}

.estado-badge.entregado {
  background-color: #d4edda;
  color: #155724;
}

.estado-badge.cancelado {
  background-color: #f8d7da;
  color: #721c24;
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

.pedido-detalles {
  margin-bottom: 15px;
}

.detalle-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px dashed #e0e0e0;
}

.ingredientes-extra {
  margin-top: 10px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.ingredientes-extra ul {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.ingredientes-extra li {
  margin-bottom: 3px;
}

.pedido-total {
  text-align: right;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 2px solid #ccc;
  font-size: 16px;
}

.estado-actions {
  display: flex;
  gap: 10px;
}

.btn-estado {
  background-color: #7b5a50;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-estado:hover {
  background-color: #5a3f36;
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

/* ----------------------------- MODAL DE PEDIDO ----------------------------- */
.modal-grande {
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
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

.form-group input,
.form-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.seccion-detalles,
.seccion-ingredientes-extra {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.seccion-detalles h4,
.seccion-ingredientes-extra h4 {
  margin-bottom: 15px;
  color: #7b5a50;
}

.nuevo-detalle,
.nuevo-ingrediente {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.select-receta,
.select-insumo {
  flex: 2;
  min-width: 200px;
}

.input-cantidad {
  width: 100px;
}

.btn-agregar {
  background-color: #7b5a50;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-agregar:hover:not(:disabled) {
  background-color: #5a3f36;
}

.btn-agregar:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.lista-detalles,
.lista-ingredientes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detalle-item-modal,
.ingrediente-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.btn-eliminar-detalle {
  background: none;
  border: none;
  cursor: pointer;
  color: #dc3545;
}

.btn-eliminar-detalle:hover {
  color: #bd2130;
}

.total-pedido {
  text-align: right;
  margin: 20px 0;
  padding-top: 15px;
  border-top: 2px solid #ccc;
  font-size: 18px;
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

.select-unidad {
  width: 120px;
  min-width: 120px;
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .filtros-pedidos {
    flex-direction: column;
    align-items: stretch;
  }

  .pedido-header {
    flex-direction: column;
  }

  .pedido-acciones {
    align-self: flex-end;
  }

  .estado-actions {
    flex-direction: column;
  }

  .btn-estado {
    width: 100%;
  }

  .modal-grande {
    width: 95%;
    margin: 10px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .nuevo-detalle,
  .nuevo-ingrediente {
    flex-direction: column;
    align-items: stretch;
  }

  .select-receta,
  .select-insumo,
  .input-cantidad {
    width: 100%;
    min-width: unset;
  }
}
</style>
