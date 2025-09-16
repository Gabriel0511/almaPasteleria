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
        <section class="pedidos-content">
          <h3 class="card-title1">Gestión de Pedidos</h3>

          <div class="botones-acciones">
            <button class="btn-nuevo-pedido" @click="showNuevoPedidoModal">
              <i class="fas fa-plus"></i> Nuevo Pedido
            </button>
          </div>

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
              :class="{ 'pedido-entregado': pedido.estado === 'entregado' }"
            >
              <div class="pedido-header">
                <div class="pedido-info">
                  <span class="cliente-container">
                    <span class="cliente-nombre">
                      {{ pedido.cliente.nombre }}
                      <span
                        class="pedido-estado"
                        :class="pedido.estado.toLowerCase()"
                      >
                        ({{ pedido.estado }})
                      </span>
                    </span>
                    <span class="pedido-fechas">
                      Pedido: {{ formatFecha(pedido.fecha_pedido) }} | Entrega:
                      {{ formatFecha(pedido.fecha_entrega) }}
                    </span>
                    <span class="pedido-total">
                      Total: ${{ calcularTotalPedido(pedido) }}
                    </span>
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

              <!-- Botón para agregar receta -->
              <div
                class="agregar-receta-container"
                v-if="pedido.estado !== 'entregado'"
              >
                <button
                  class="btn-agregar-receta"
                  @click="showAgregarRecetaModal(pedido)"
                >
                  <i class="fas fa-plus"></i> Agregar Receta
                </button>
              </div>

              <!-- Mensaje para pedidos entregados -->
              <div
                class="pedido-entregado-mensaje"
                v-if="pedido.estado === 'entregado'"
              >
                <i class="fas fa-check-circle"></i> Pedido entregado - No se
                pueden realizar modificaciones
              </div>

              <!-- Detalles del pedido - Recetas -->
              <div class="recetas-container">
                <div
                  v-for="detalle in pedido.detalles"
                  :key="detalle.id"
                  class="receta-item"
                >
                  <div class="receta-header" @click="toggleReceta(detalle.id)">
                    <span class="receta-nombre">
                      {{ detalle.receta.nombre }} x{{ detalle.cantidad }}
                    </span>
                    <span class="receta-precio">
                      ${{ calcularPrecioReceta(detalle) }}
                    </span>

                    <div class="receta-header-acciones">
                      <template v-if="pedido.estado !== 'entregado'">
                        <button
                          class="btn-accion-small"
                          @click.stop="editarReceta(detalle, pedido)"
                          title="Editar receta"
                        >
                          <i class="fas fa-edit"></i>
                        </button>
                        <button
                          class="btn-accion-small btn-eliminar"
                          @click.stop="confirmarEliminarReceta(detalle)"
                          title="Eliminar receta"
                        >
                          <i class="fas fa-trash"></i>
                        </button>
                      </template>
                      <i
                        class="fas"
                        :class="
                          detalleExpandido[detalle.id]
                            ? 'fa-chevron-up'
                            : 'fa-chevron-down'
                        "
                      ></i>
                    </div>
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
                        <span>
                          {{ ingrediente.insumo.nombre }}:
                          {{ ingrediente.cantidad }}
                          {{ ingrediente.unidad_medida.abreviatura }}
                        </span>

                        <div
                          class="ingrediente-acciones"
                          v-if="pedido.estado !== 'entregado'"
                        >
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
                            class="btn-accion-small btn-eliminar"
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

                    <div
                      class="receta-acciones"
                      v-if="pedido.estado !== 'entregado'"
                    >
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

    <!-- MODALES -->

    <!-- Modal para Nuevo/Editar Pedido -->
    <div v-if="showModalPedido" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ esEdicionPedido ? "Editar Pedido" : "Nuevo Pedido" }}</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Cliente:</label>
            <div class="select-with-button">
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
                  {{ cliente.nombre }}
                </option>
              </select>
              <button
                type="button"
                class="btn-agregar-nuevo"
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
              :disabled="esEdicionPedido"
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
            {{ esEdicionPedido ? "Actualizar" : "Crear" }}
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
              placeholder="Nombre del cliente"
            />
          </div>

          <div class="form-group">
            <label>Teléfono:</label>
            <input
              v-model="formCliente.telefono"
              type="text"
              class="form-input"
              placeholder="Teléfono"
            />
          </div>

          <div class="form-group">
            <label>Dirección:</label>
            <textarea
              v-model="formCliente.direccion"
              class="form-input"
              rows="3"
              placeholder="Dirección"
            ></textarea>
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

    <!-- Modal Agregar/Editar Receta al Pedido -->
    <div v-if="showModalReceta" class="modal-overlay">
      <div class="modal-content">
        <h3>
          {{ esEdicionReceta ? "Editar Receta" : "Agregar Receta al Pedido" }}
        </h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Receta:</label>
            <div class="select-with-button">
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
              <button
                type="button"
                class="btn-agregar-nuevo"
                @click="showNuevaRecetaModal = true"
                title="Crear nueva receta"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
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

    <!-- Modal para Nueva Receta -->
    <div v-if="showNuevaRecetaModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nueva Receta</h3>

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
            <select
              v-model="formReceta.unidad_rinde"
              required
              class="form-input"
            >
              <option value="porciones">Porciones</option>
              <option value="unidades">Unidades</option>
            </select>
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="showNuevaRecetaModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="guardarNuevaReceta" class="confirm-button">
            Guardar
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
          <!-- Insumo con botón para agregar nuevo -->
          <div class="form-group">
            <label>Insumo:</label>
            <div class="select-with-button">
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
              <button
                type="button"
                class="btn-agregar-nuevo"
                @click="showNuevoInsumoModal = true"
                title="Crear nuevo insumo"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Cantidad:</label>
            <input
              v-model="formIngrediente.cantidad"
              type="number"
              step="0.001"
              min="0.001"
              required
              class="form-input"
            />
          </div>

          <!-- Unidad de medida con botón para agregar nueva -->
          <div class="form-group">
            <label>Unidad de Medida:</label>
            <div class="select-with-button">
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
              <button
                type="button"
                class="btn-agregar-nuevo"
                @click="showNuevaUnidadModal = true"
                title="Crear nueva unidad de medida"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>
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

    <!-- Modal para Nuevo Insumo -->
    <div v-if="showNuevoInsumoModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nuevo Insumo</h3>

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
          <button @click="showNuevoInsumoModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="guardarNuevoInsumo" class="confirm-button">
            Guardar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal para Nueva Unidad de Medida -->
    <div v-if="showNuevaUnidadModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Nueva Unidad de Medida</h3>

        <div class="form-grid">
          <div class="form-group">
            <label>Nombre:</label>
            <input
              v-model="formUnidadMedida.nombre"
              type="text"
              required
              class="form-input"
              placeholder="Nombre completo"
            />
          </div>

          <div class="form-group">
            <label>Abreviatura:</label>
            <input
              v-model="formUnidadMedida.abreviatura"
              type="text"
              required
              class="form-input"
              placeholder="Ej: kg, g, l, ml"
              maxlength="10"
            />
          </div>

          <div class="form-group">
            <label>Descripción:</label>
            <input
              v-model="formUnidadMedida.descripcion"
              type="text"
              class="form-input"
            />
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="showNuevaUnidadModal = false" class="cancel-button">
            Cancelar
          </button>
          <button @click="guardarNuevaUnidadMedida" class="confirm-button">
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
              placeholder="Nombre de la categoría"
            />
          </div>
          <div class="form-group">
            <label>Descripción:</label>
            <textarea
              v-model="formCategoria.descripcion"
              class="form-input"
              rows="3"
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
          <button @click="guardarNuevaCategoria" class="confirm-button">
            Guardar
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
        <div class="modal-buttons">
          <button
            @click="showNuevoProveedorModal = false"
            class="cancel-button"
          >
            Cancelar
          </button>
          <button @click="guardarNuevoProveedor" class="confirm-button">
            Guardar
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
import { ref, computed, onMounted, watch, inject } from "vue";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import axios from "axios";

const router = useRouter();
const notificationSystem = inject("notifications");

// Variables de estado
const userEmail = ref("Usuario");
const showPasswordModal = ref(false);
const pedidos = ref([]);
const clientes = ref([]);
const recetas = ref([]);
const insumos = ref([]);
const categorias = ref([]);
const unidadesMedida = ref([]);
const proveedores = ref([]);
const estadoSeleccionado = ref("");
const fechaSeleccionada = ref("");
const searchTerm = ref("");
const loading = ref(true);
const detalleExpandido = ref({});

// Modales
const showModalPedido = ref(false);
const showNuevoClienteModal = ref(false);
const showModalReceta = ref(false);
const showNuevoInsumoModal = ref(false);
const showNuevaUnidadModal = ref(false);
const showNuevaRecetaModal = ref(false);
const showNuevaCategoriaModal = ref(false);
const showNuevaUnidadDeMedidaModal = ref(false);
const showNuevoProveedorModal = ref(false);
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

const formReceta = ref({
  nombre: "",
  rinde: 1,
  unidad_rinde: "porciones",
  costo_unitario: 0,
  costo_total: 0,
});

const formInsumo = ref({
  id: null,
  nombre: "",
  categoria_id: "",
  unidad_medida_id: "",
  stock_minimo: 0,
  precio_unitario: null,
  proveedor_id: null,
});

const formUnidadMedida = ref({
  nombre: "",
  abreviatura: "",
  descripcion: "",
});

const formCategoria = ref({
  nombre: "",
  descripcion: "",
});

const formProveedor = ref({
  nombre: "",
  contacto: "",
  telefono: "",
  email: "",
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
    filtered = filtered.filter((pedido) => {
      const nombreCliente = pedido.cliente?.nombre?.toLowerCase() || "";
      const telefonoCliente = pedido.cliente?.telefono?.toLowerCase() || "";
      return nombreCliente.includes(term) || telefonoCliente.includes(term);
    });
  }

  // Ordenar: pedidos entregados al final
  return filtered.sort((a, b) => {
    if (a.estado === "entregado" && b.estado !== "entregado") return 1;
    if (a.estado !== "entregado" && b.estado === "entregado") return -1;
    return 0;
  });
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

  // Crear fecha en la zona horaria local
  const fechaLocal = new Date(fecha);

  // Ajustar para compensar el offset de zona horaria
  const fechaAjustada = new Date(
    fechaLocal.getTime() + fechaLocal.getTimezoneOffset() * 60000
  );

  return fechaAjustada.toLocaleDateString("es-AR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
};

// Función para enviar fechas al backend correctamente
const formatFechaParaBackend = (fechaInput) => {
  if (!fechaInput) return "";

  // Crear fecha en la zona horaria local
  const fecha = new Date(fechaInput);

  // Ajustar para que se guarde como UTC pero representando la fecha local correcta
  const fechaAjustada = new Date(
    fecha.getTime() - fecha.getTimezoneOffset() * 60000
  );

  return fechaAjustada.toISOString().split("T")[0];
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
  if (pedido.estado === "entregado") {
    notificationSystem.show({
      type: "warning",
      title: "No se puede editar",
      message: "No se puede editar un pedido entregado",
      timeout: 4000,
    });
    return;
  }
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
  if (pedido.estado === "entregado") {
    notificationSystem.show({
      type: "warning",
      title: "No se puede eliminar",
      message: "No se puede eliminar un pedido entregado",
      timeout: 4000,
    });
    return;
  }
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

    notificationSystem.show({
      type: "success",
      title: "Pedido eliminado",
      message: "Pedido eliminado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al eliminar pedido:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al eliminar el pedido",
      timeout: 6000,
    });
  }
};

const guardarPedido = async () => {
  try {
    if (!formPedido.value.cliente_id) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El cliente es requerido",
        timeout: 4000,
      });
      return;
    }
    if (!formPedido.value.fecha_entrega) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La fecha de entrega es requerida",
        timeout: 4000,
      });
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

    notificationSystem.show({
      type: "success",
      title: esEdicionPedido.value ? "Pedido actualizado" : "Pedido creado",
      message: esEdicionPedido.value
        ? "Pedido actualizado correctamente"
        : "Pedido creado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar pedido:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al guardar el pedido",
      timeout: 6000,
    });
  }
};

const guardarCliente = async () => {
  try {
    const response = await axios.post("/api/clientes/", formCliente.value);
    await fetchClientes();
    showNuevoClienteModal.value = false;
    resetFormCliente();

    notificationSystem.show({
      type: "success",
      title: "Cliente creado",
      message: "Cliente creado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar cliente:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al guardar el cliente",
      timeout: 6000,
    });
  }
};

const guardarNuevaCategoria = async () => {
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

    // Actualizar la lista de categorías
    await fetchCategorias();

    // Seleccionar automáticamente la nueva categoría
    formInsumo.value.categoria_id = response.data.id;

    showNuevaCategoriaModal.value = false;
    formCategoria.value = { nombre: "", descripcion: "" };

    notificationSystem.show({
      type: "success",
      title: "Categoría creada",
      message: "Categoría creada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar categoría:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al crear la categoría",
      timeout: 6000,
    });
  }
};

const guardarNuevoProveedor = async () => {
  try {
    if (!formProveedor.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre del proveedor es requerido",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.post(
      "/api/proveedores/crear/",
      formProveedor.value
    );

    // Actualizar la lista de proveedores
    await fetchProveedores();

    // Seleccionar automáticamente el nuevo proveedor
    formInsumo.value.proveedor_id = response.data.id;

    showNuevoProveedorModal.value = false;
    formProveedor.value = { nombre: "", contacto: "", telefono: "", email: "" };

    notificationSystem.show({
      type: "success",
      title: "Proveedor creado",
      message: "Proveedor creado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar proveedor:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al crear el proveedor",
      timeout: 6000,
    });
  }
};

const guardarNuevoInsumo = async () => {
  try {
    if (!formInsumo.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre del insumo es requerido",
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

    // Preparar datos para enviar (sin el formateo complicado)
    const datosParaEnviar = {
      nombre: formInsumo.value.nombre,
      categoria_id: formInsumo.value.categoria_id || null,
      unidad_medida_id: formInsumo.value.unidad_medida_id,
      stock_minimo: parseFloat(formInsumo.value.stock_minimo),
      precio_unitario: formInsumo.value.precio_unitario
        ? parseFloat(formInsumo.value.precio_unitario)
        : null,
      proveedor_id: formInsumo.value.proveedor_id || null,
      stock_actual: 0, // Siempre empezar con stock 0 para nuevos insumos
      activo: true,
    };

    // Solo para crear nuevo insumo (sin lógica de edición)
    const response = await axios.post("/api/insumos/crear/", datosParaEnviar);

    // Actualizar la lista de insumos
    await fetchInsumos();

    // Seleccionar automáticamente el nuevo insumo en el formulario de ingrediente
    formIngrediente.value.insumo_id = response.data.id;

    showNuevoInsumoModal.value = false;
    resetFormInsumo();

    notificationSystem.show({
      type: "success",
      title: "Insumo creado",
      message: "Insumo creado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar insumo:", error);

    if (error.response?.status === 400 && error.response?.data?.error) {
      notificationSystem.show({
        type: "error",
        title: "Error al crear insumo",
        message: error.response.data.error,
        timeout: 6000,
      });
    } else {
      notificationSystem.show({
        type: "error",
        title: "Error",
        message: "Error al crear el insumo",
        timeout: 6000,
      });
    }
  }
};

const guardarNuevaUnidadMedida = async () => {
  try {
    if (!formUnidadMedida.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre de la unidad es requerido",
        timeout: 4000,
      });
      return;
    }
    if (!formUnidadMedida.value.abreviatura) {
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
      formUnidadMedida.value
    );

    // Actualizar la lista de unidades de medida
    await fetchUnidadesMedida();

    // Seleccionar automáticamente la nueva unidad
    formIngrediente.value.unidad_medida_id = response.data.id;

    showNuevaUnidadModal.value = false;
    resetFormUnidadMedida();

    notificationSystem.show({
      type: "success",
      title: "Unidad de medida creada",
      message: "Unidad de medida creada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar unidad de medida:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al crear la unidad de medida",
      timeout: 6000,
    });
  }
};

const guardarNuevaReceta = async () => {
  try {
    if (!formReceta.value.nombre) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El nombre de la receta es requerido",
        timeout: 4000,
      });
      return;
    }
    if (!formReceta.value.rinde || formReceta.value.rinde <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El rinde debe ser mayor a 0",
        timeout: 4000,
      });
      return;
    }

    const response = await axios.post("/api/recetas/", formReceta.value);

    // Actualizar la lista de recetas
    await fetchRecetas();

    // Seleccionar automáticamente la nueva receta
    formDetalle.value.receta_id = response.data.id;

    showNuevaRecetaModal.value = false;
    resetFormReceta();

    notificationSystem.show({
      type: "success",
      title: "Receta creada",
      message: "Receta creada correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al guardar receta:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al crear la receta",
      timeout: 6000,
    });
  }
};

const showNuevoIngredienteModal = (detalle) => {
  const pedido = pedidos.value.find((p) =>
    p.detalles.some((d) => d.id === detalle.id)
  );
  if (pedido && pedido.estado === "entregado") {
    notificationSystem.show({
      type: "warning",
      title: "No se puede agregar",
      message: "No se pueden agregar ingredientes a un pedido entregado",
      timeout: 4000,
    });
    return;
  }
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

    notificationSystem.show({
      type: "success",
      title: "Ingrediente eliminado",
      message: "Ingrediente extra eliminado correctamente",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al eliminar ingrediente extra:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al eliminar el ingrediente extra",
      timeout: 6000,
    });
  }
};

const guardarIngredienteExtra = async () => {
  try {
    if (!formIngrediente.value.insumo_id) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El insumo es requerido",
        timeout: 4000,
      });
      return;
    }
    if (
      !formIngrediente.value.cantidad ||
      formIngrediente.value.cantidad <= 0
    ) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La cantidad debe ser mayor a 0",
        timeout: 4000,
      });
      return;
    }
    if (!formIngrediente.value.unidad_medida_id) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La unidad de medida es requerida",
        timeout: 4000,
      });
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

    notificationSystem.show({
      type: "success",
      title: esEdicionIngrediente.value
        ? "Ingrediente actualizado"
        : "Ingrediente agregado",
      message: esEdicionIngrediente.value
        ? "Ingrediente extra actualizado correctamente"
        : "Ingrediente extra agregado correctamente",
      timeout: 4000,
    });
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

    notificationSystem.show({
      type: "error",
      title: "Error al guardar ingrediente",
      message: mensajeError,
      timeout: 6000,
    });
  }
};

const closeModal = () => {
  showModalPedido.value = false;
  showNuevoClienteModal.value = false;
  showModalReceta.value = false;
  showModalIngrediente.value = false;
  showNuevaRecetaModal.value = false;
  showNuevoInsumoModal.value = false;
  showNuevaUnidadModal.value = false;
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

const resetFormReceta = () => {
  formReceta.value = {
    nombre: "",
    rinde: 1,
    unidad_rinde: "porciones",
    costo_unitario: 0,
    costo_total: 0,
  };
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

const resetFormUnidadMedida = () => {
  formUnidadMedida.value = {
    nombre: "",
    abreviatura: "",
  };
};

// Nuevos métodos para gestionar recetas
const showAgregarRecetaModal = (pedido) => {
  if (pedido.estado === "entregado") {
    notificationSystem.show({
      type: "warning",
      title: "No se puede agregar",
      message: "No se pueden agregar recetas a un pedido entregado",
      timeout: 4000,
    });
    return;
  }
  esEdicionReceta.value = false;
  pedidoActual.value = pedido;
  resetFormDetalle();
  formDetalle.value.pedido_id = pedido.id;
  showModalReceta.value = true;
};

const editarReceta = (detalle, pedido) => {
  if (pedido.estado === "entregado") {
    notificationSystem.show({
      type: "warning",
      title: "No se puede editar",
      message: "No se puede editar recetas de un pedido entregado",
      timeout: 4000,
    });
    return;
  }
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

    notificationSystem.show({
      type: "success",
      title: "Receta eliminada",
      message: "Receta eliminada correctamente del pedido",
      timeout: 4000,
    });
  } catch (error) {
    console.error("Error al eliminar receta:", error);

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: "Error al eliminar la receta del pedido",
      timeout: 6000,
    });
  }
};

const guardarDetalle = async () => {
  try {
    if (!formDetalle.value.receta_id) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La receta es requerida",
        timeout: 4000,
      });
      return;
    }
    if (!formDetalle.value.cantidad || formDetalle.value.cantidad <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "La cantidad debe ser mayor a 0",
        timeout: 4000,
      });
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

    notificationSystem.show({
      type: "success",
      title: esEdicionReceta.value ? "Receta actualizada" : "Receta agregada",
      message: esEdicionReceta.value
        ? "Receta actualizada correctamente"
        : "Receta agregada correctamente al pedido",
      timeout: 4000,
    });
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

    notificationSystem.show({
      type: "error",
      title: "Error al guardar receta",
      message: mensajeError,
      timeout: 6000,
    });
  }
};

const resetForms = () => {
  resetFormPedido();
  resetFormCliente();
  resetFormDetalle();
  resetFormIngrediente();
  resetFormReceta();
  resetFormInsumo();
  resetFormUnidadMedida();
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

const fetchCategorias = async () => {
  try {
    const response = await axios.get("/api/categorias/");
    categorias.value = response.data;
  } catch (err) {
    console.error("Error en fetchCategorias:", err);
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
    insumos.value = response.data.insumos || response.data;
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
    fetchCategorias(),
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

/* ----------------------------- LAYOUT GENERAL ----------------------------- */
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

/* ----------------------------- BOTONES GENERALES ----------------------------- */
.botones-acciones {
  display: flex;
  gap: 10px;
  margin-right: auto;
  margin-bottom: 25px;
}

.btn-nuevo-pedido,
.btn-agregar-receta,
.btn-agregar-ingrediente,
.btn-agregar-cliente,
.btn-agregar-nuevo {
  background-color: #e3f2fd;
  color: #1565c0;
  border: 1px solid #bbdefb;
  border-radius: 4px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: background-color 0.2s;
}

.btn-nuevo-pedido {
  background-color: #b8e6b8;
  color: #2b5d2b;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  padding: 8px 15px;
  height: 38px;
}
.btn-nuevo-pedido:hover {
  background-color: #a1dca1;
}

.btn-agregar-receta {
  padding: 8px 15px;
  border-radius: 6px;
  font-weight: bold;
}
.btn-agregar-receta:hover,
.btn-agregar-ingrediente:hover,
.btn-agregar-cliente:hover,
.btn-agregar-nuevo:hover {
  background-color: #bbdefb;
}

.btn-agregar-ingrediente {
  padding: 5px 10px;
  font-size: 12px;
}

.btn-agregar-cliente,
.btn-agregar-nuevo {
  padding: 0 10px;
  height: 38px;
}

/* Botón de acción genérico */
.btn-accion,
.btn-accion-small {
  background: none;
  border: 1px solid #ddd;
  cursor: pointer;
  color: #7b5a50;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}
.btn-accion:hover,
.btn-accion-small:hover {
  background-color: #f5f5f5;
}

/* Variante eliminar */
.btn-eliminar {
  color: #dc3545;
  border-color: #f5c6cb;
}
.btn-eliminar:hover {
  background-color: #f8d7da;
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
.pedido-estado.en-preparacion {
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

.receta-header-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
}

.receta-nombre,
.receta-precio {
  font-weight: bold;
}
.receta-precio {
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

.receta-acciones {
  margin-top: 10px;
  text-align: right;
}

.receta-acciones-superiores {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  justify-content: flex-end;
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
  width: 100%;
}

.cliente-select-container {
  display: flex;
  gap: 5px;
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

/* ----------------------------- ESTADOS Y VARIOS ----------------------------- */
.pedido-entregado {
  background-color: #f8f9fa;
  border-color: #d1ecf1;
  opacity: 0.8;
}
.pedido-entregado .pedido-header {
  opacity: 0.7;
}

.pedido-entregado-mensaje {
  background-color: #d4edda;
  color: #155724;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
  text-align: center;
  font-weight: bold;
}
.pedido-entregado-mensaje i {
  margin-right: 8px;
}

.pedido-entregado .btn-accion,
.pedido-entregado .btn-agregar-receta,
.pedido-entregado .btn-agregar-ingrediente {
  opacity: 0.5;
  cursor: not-allowed;
}
.pedido-entregado .btn-accion:hover,
.pedido-entregado .btn-agregar-receta:hover,
.pedido-entregado .btn-agregar-ingrediente:hover {
  background-color: transparent;
  transform: none;
}

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
