<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header />

      <main class="main-content">
        <section class="pedidos-content">
          <h3 class="card-title1">Gestión de Pedidos</h3>

          <!-- Filtros de pedidos -->
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
            <i class="fas fa-search"></i>
            <p>No hay pedidos que coincidan con los filtros seleccionados</p>
          </div>

          <div v-else class="pedidos-list">
            <div
              v-for="pedido in pedidosFiltrados"
              :key="pedido.id"
              class="pedido-item"
              :class="{ 'pedido-entregado': pedido.estado === 'entregado' }"
            >
              <!-- En la sección del pedido-item, modificar el pedido-header -->
              <div
                class="pedido-header"
                @click="togglePedido(pedido.id)"
                :class="{ 'cursor-pointer': true }"
              >
                <div class="pedido-info">
                  <div class="pedido-titulo">
                    <span class="cliente-nombre">
                      {{ pedido.cliente.nombre }}
                    </span>
                    <span
                      class="pedido-estado-badge"
                      :class="pedido.estado.toLowerCase()"
                    >
                      {{ pedido.estado }}
                    </span>
                    <span class="pedido-total">
                      ${{ calcularTotalPedido(pedido) }}
                    </span>
                  </div>
                  <div class="pedido-datos">
                    <div class="dato-grupo">
                      <i class="fas fa-calendar-alt"></i>
                      <span class="pedido-fecha">
                        Pedido: {{ formatFecha(pedido.fecha_pedido) }}
                      </span>
                    </div>
                    <div class="dato-grupo">
                      <i class="fas fa-truck"></i>
                      <span class="pedido-fecha">
                        Entrega: {{ formatFecha(pedido.fecha_entrega) }}
                      </span>
                    </div>
                    <div class="dato-grupo">
                      <i class="fas fa-list"></i>
                      <span class="pedido-recetas-count">
                        {{ pedido.detalles.length }} recetas
                      </span>
                    </div>
                  </div>
                </div>
                <div class="pedido-acciones" @click.stop>
                  <!-- Los botones de acción mantienen el @click.stop para evitar que el evento se propague -->
                  <button
                    class="btn-accion btn-editar"
                    @click="editarPedido(pedido)"
                    title="Editar pedido"
                    :disabled="pedido.estado === 'entregado'"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                  <button
                    class="btn-accion btn-eliminar"
                    @click="confirmarEliminarPedido(pedido)"
                    title="Eliminar pedido"
                    :disabled="pedido.estado === 'entregado'"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                  <button
                    class="btn-accion btn-desplegable"
                    @click="togglePedido(pedido.id)"
                    :title="
                      pedidoDesplegado[pedido.id]
                        ? 'Ocultar detalles'
                        : 'Mostrar detalles'
                    "
                  >
                    <i
                      class="fas"
                      :class="
                        pedidoDesplegado[pedido.id]
                          ? 'fa-chevron-up'
                          : 'fa-chevron-down'
                      "
                    ></i>
                  </button>
                </div>
              </div>
              <!-- Desplegable de detalles del pedido -->
              <div
                v-if="pedidoDesplegado[pedido.id]"
                class="pedido-detalles-desplegable"
                :class="{ active: pedidoDesplegado[pedido.id] }"
              >
                <div class="detalles-content">
                  <!-- Botón para agregar receta -->
                  <div
                    class="agregar-receta-container"
                    v-if="pedido.estado !== 'entregado'"
                  >
                    <button
                      class="btn-agregar-receta"
                      @click="showAgregarRecetaModal(pedido)"
                    >
                      <i class="fas fa-plus-circle"></i> Agregar Receta
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
                      <div
                        class="receta-header"
                        @click="toggleReceta(detalle.id)"
                      >
                        <div class="receta-info">
                          <div class="receta-titulo">
                            <span class="receta-nombre">
                              {{ detalle.receta.nombre }} x{{
                                detalle.cantidad
                              }}
                            </span>
                            <span class="receta-precio">
                              ${{ calcularPrecioReceta(detalle) }}
                            </span>
                          </div>
                        </div>
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
                            <i class="fas fa-plus"></i> Agregar Ingrediente
                            Extra
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Botón Nuevo Pedido flotante -->
        <button class="btn-nuevo-pedido-flotante" @click="showNuevoPedidoModal">
          <i class="fas fa-plus"></i>
          <span>Nuevo Pedido</span>
        </button>
      </main>
    </div>

    <!-- MODALES -->

    <!-- Modal para Nuevo/Editar Pedido -->
    <BaseModal
      v-model:show="showModalPedido"
      :title="esEdicionPedido ? 'Editar Pedido' : 'Nuevo Pedido'"
      size="medium"
      @close="closeModal"
    >
      <div class="form-grid">
        <div class="form-group">
          <label>Cliente:</label>
          <div class="select-with-button">
            <select v-model="formPedido.cliente_id" required class="form-input">
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

      <template #footer>
        <ModalButtons
          :confirm-text="esEdicionPedido ? 'Actualizar' : 'Crear'"
          @cancel="closeModal"
          @confirm="guardarPedido"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nuevo Cliente -->
    <BaseModal
      v-model:show="showNuevoClienteModal"
      title="Nuevo Cliente"
      size="medium"
      @close="showNuevoClienteModal = false"
    >
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

        <div class="form-group full-width">
          <label>Dirección:</label>
          <textarea
            v-model="formCliente.direccion"
            class="form-input"
            rows="3"
            placeholder="Dirección"
          ></textarea>
        </div>
      </div>

      <template #footer>
        <ModalButtons
          confirm-text="Guardar"
          @cancel="showNuevoClienteModal = false"
          @confirm="guardarCliente"
        />
      </template>
    </BaseModal>

    <!-- Modal Agregar/Editar Receta al Pedido -->
    <BaseModal
      v-model:show="showModalReceta"
      :title="esEdicionReceta ? 'Editar Receta' : 'Agregar Receta al Pedido'"
      size="medium"
      @close="closeModal"
    >
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

      <template #footer>
        <ModalButtons
          :confirm-text="esEdicionReceta ? 'Actualizar' : 'Agregar'"
          @cancel="closeModal"
          @confirm="guardarDetalle"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nueva Receta -->
    <BaseModal
      v-model:show="showNuevaRecetaModal"
      title="Nueva Receta"
      size="large"
      @close="showNuevaRecetaModal = false"
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
          <label>Costo unitario:</label>
          <input
            v-model="formReceta.costo_unitario"
            type="number"
            step="0.01"
            min="0.01"
            required
            class="form-input"
            placeholder="Costo unitario (por porción o unidad)"
          />
        </div>

        <div class="form-group">
          <label>Costo total:</label>
          <input
            v-model="formReceta.costo_total"
            type="number"
            step="0.01"
            min="0.01"
            required
            class="form-input"
            placeholder="Costo total"
          />
        </div>

        <div class="form-group">
          <label>Precio de venta:</label>
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
          confirm-text="Guardar"
          @cancel="showNuevaRecetaModal = false"
          @confirm="guardarNuevaReceta"
        />
      </template>
    </BaseModal>

    <!-- Modal para Agregar/Editar Ingrediente Extra -->
    <BaseModal
      v-model:show="showModalIngrediente"
      :title="
        esEdicionIngrediente
          ? 'Editar Ingrediente Extra'
          : 'Agregar Ingrediente Extra'
      "
      size="medium"
      @close="closeModal"
    >
      <div class="form-grid">
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

      <template #footer>
        <ModalButtons
          :confirm-text="esEdicionIngrediente ? 'Actualizar' : 'Agregar'"
          @cancel="closeModal"
          @confirm="guardarIngredienteExtra"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nuevo Insumo -->
    <BaseModal
      v-model:show="showNuevoInsumoModal"
      title="Nuevo Insumo"
      size="large"
      @close="showNuevoInsumoModal = false"
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
              class="btn-agregar-nuevo"
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
          <div class="select-with-button">
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
              class="btn-agregar-nuevo"
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
          confirm-text="Guardar"
          @cancel="showNuevoInsumoModal = false"
          @confirm="guardarNuevoInsumo"
        />
      </template>
    </BaseModal>

    <!-- Modal para Nueva Unidad de Medida -->
    <BaseModal
      v-model:show="showNuevaUnidadModal"
      title="Nueva Unidad de Medida"
      size="small"
      @close="showNuevaUnidadModal = false"
    >
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

      <template #footer>
        <ModalButtons
          confirm-text="Guardar"
          @cancel="showNuevaUnidadModal = false"
          @confirm="guardarNuevaUnidadMedida"
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
          ></textarea>
        </div>
      </div>

      <template #footer>
        <ModalButtons
          confirm-text="Guardar"
          @cancel="showNuevaCategoriaModal = false"
          @confirm="guardarNuevaCategoria"
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
          @confirm="guardarNuevoProveedor"
        />
      </template>
    </BaseModal>

    <!-- Modal de confirmación para eliminar pedido -->
    <ConfirmModal
      :show="showConfirmModalPedido"
      title="Confirmar Eliminación"
      :message="`¿Está seguro de que desea eliminar el pedido de '${pedidoAEliminar?.cliente?.nombre}'?`"
      confirm-text="Eliminar"
      @update:show="showConfirmModalPedido = $event"
      @cancel="showConfirmModalPedido = false"
      @confirm="eliminarPedido"
    />

    <!-- Modal de confirmación para eliminar ingrediente extra -->
    <ConfirmModal
      :show="showConfirmModalIngrediente"
      title="Confirmar Eliminación"
      message="¿Está seguro de que desea eliminar este ingrediente extra?"
      confirm-text="Eliminar"
      @update:show="showConfirmModalIngrediente = $event"
      @cancel="showConfirmModalIngrediente = false"
      @confirm="eliminarIngredienteExtra"
    />

    <!-- Modal de confirmación para eliminar receta -->
    <ConfirmModal
      :show="showConfirmModalReceta"
      title="Confirmar Eliminación"
      message="¿Está seguro de que desea eliminar esta receta del pedido?"
      confirm-text="Eliminar"
      @update:show="showConfirmModalReceta = $event"
      @cancel="showConfirmModalReceta = false"
      @confirm="eliminarReceta"
    />
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted, watch, inject } from "vue";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import BaseModal from "./Modals/BaseModal.vue";
import ModalButtons from "./Modals/ModalButtons.vue";
import ConfirmModal from "./Modals/ConfirmModal.vue";
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
const pedidoDesplegado = ref({});

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
  precio_venta: 0,
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
  } else {
    // Si no hay estado seleccionado, excluir los entregados
    filtered = filtered.filter((pedido) => pedido.estado !== "entregado");
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

  // Ordenar por fecha de pedido (más reciente primero)
  return filtered.sort((a, b) => {
    // Convertir fechas a timestamps para comparar
    const fechaA = new Date(a.fecha_pedido).getTime();
    const fechaB = new Date(b.fecha_pedido).getTime();

    // Orden descendente (más reciente primero)
    return fechaB - fechaA;
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

// Nuevo método para toggle del desplegable de pedidos
const togglePedido = (pedidoId) => {
  pedidoDesplegado.value = {
    ...pedidoDesplegado.value,
    [pedidoId]: !pedidoDesplegado.value[pedidoId],
  };
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

// Función de conversión de unidades
const convertirUnidad = (cantidad, unidadOrigen, unidadDestino) => {
  // Tabla de conversiones básicas
  const conversiones = {
    // Peso
    kg: { g: 1000, mg: 1000000, kg: 1 },
    g: { kg: 0.001, mg: 1000, g: 1 },
    mg: { kg: 0.000001, g: 0.001, mg: 1 },

    // Volumen
    l: { ml: 1000, cl: 100, l: 1 },
    ml: { l: 0.001, cl: 0.1, ml: 1 },
    cl: { l: 0.01, ml: 10, cl: 1 },

    // Unidades (si no hay conversión, asumimos 1:1)
    unidad: { unidad: 1, u: 1, pz: 1 },
    u: { unidad: 1, u: 1, pz: 1 },
    pz: { unidad: 1, u: 1, pz: 1 },
  };

  // Si las unidades son iguales, no hay conversión
  if (unidadOrigen === unidadDestino) return cantidad;

  // Buscar conversión
  if (conversiones[unidadOrigen] && conversiones[unidadOrigen][unidadDestino]) {
    return cantidad * conversiones[unidadOrigen][unidadDestino];
  }

  // Si no encuentra conversión, devolver la cantidad original (asumir misma unidad)
  console.warn(
    `No se encontró conversión de ${unidadOrigen} a ${unidadDestino}`
  );
  return cantidad;
};

// Función corregida para calcular total del pedido
const calcularTotalPedido = (pedido) => {
  let total = 0;

  if (pedido.detalles) {
    pedido.detalles.forEach((detalle) => {
      // Calcular subtotal de la receta
      const precioReceta = parseFloat(detalle.receta?.precio_venta) || 0;
      const cantidadReceta = parseFloat(detalle.cantidad) || 0;
      const subtotalReceta = precioReceta * cantidadReceta;
      total += subtotalReceta;

      // Calcular subtotal de ingredientes extras
      if (
        detalle.ingredientes_extra &&
        Array.isArray(detalle.ingredientes_extra)
      ) {
        detalle.ingredientes_extra.forEach((ingrediente) => {
          const precioIngrediente =
            parseFloat(ingrediente.insumo?.precio_unitario) || 0;
          const cantidadIngrediente = parseFloat(ingrediente.cantidad) || 0;

          // Obtener unidades
          const unidadInsumo =
            ingrediente.insumo?.unidad_medida?.abreviatura || "unidad";
          const unidadIngrediente =
            ingrediente.unidad_medida?.abreviatura || "unidad";

          // Convertir a la unidad del insumo para calcular el precio correctamente
          const cantidadConvertida = convertirUnidad(
            cantidadIngrediente,
            unidadIngrediente.toLowerCase(),
            unidadInsumo.toLowerCase()
          );

          const subtotalIngrediente = precioIngrediente * cantidadConvertida;
          total += subtotalIngrediente;
        });
      }
    });
  }

  return total.toFixed(2);
};

// También corrige calcularPrecioReceta por consistencia
const calcularPrecioReceta = (detalle) => {
  const precioReceta = parseFloat(detalle.receta?.precio_venta) || 0;
  const cantidad = parseFloat(detalle.cantidad) || 0;
  return (precioReceta * cantidad).toFixed(2);
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
    if (!formReceta.value.precio_venta || formReceta.value.precio_venta <= 0) {
      notificationSystem.show({
        type: "error",
        title: "Error de validación",
        message: "El precio de venta debe ser mayor a 0",
        timeout: 4000,
      });
      return;
    }

    // Preparar datos para enviar
    const datosReceta = {
      nombre: formReceta.value.nombre,
      rinde: formReceta.value.rinde,
      unidad_rinde: formReceta.value.unidad_rinde,
      costo_unitario: parseFloat(formReceta.value.costo_unitario) || 0,
      costo_total: parseFloat(formReceta.value.costo_total) || 0,
      precio_venta: parseFloat(formReceta.value.precio_venta) || 0,
    };

    const response = await axios.post("/api/recetas/", datosReceta);

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
    console.error("Respuesta del servidor:", error.response?.data);

    let mensajeError = "Error al crear la receta";
    if (error.response?.data) {
      if (typeof error.response.data === "object") {
        mensajeError += ": " + JSON.stringify(error.response.data);
      } else {
        mensajeError += ": " + error.response.data;
      }
    }

    notificationSystem.show({
      type: "error",
      title: "Error",
      message: mensajeError,
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
  showNuevoClienteModal.value = false;
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
    precio_venta: 0,
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

/* ----------------------------- CONTENIDO PRINCIPAL ----------------------------- */
.pedidos-content {
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

.filtro-input,
.filtro-select {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 14px;
  height: 46px;
  transition: all 0.3s ease;
  background: white;
  min-width: 200px;
}

.filtro-input:focus,
.filtro-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(123, 90, 80, 0.1);
  transform: translateY(-1px);
}

/* ----------------------------- BOTONES GENERALES ----------------------------- */
.btn-agregar-receta,
.btn-agregar-ingrediente {
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

.btn-nuevo-pedido:hover,
.btn-agregar-receta:hover,
.btn-agregar-ingrediente:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
}

.btn-agregar-ingrediente {
  padding: 8px 16px;
  font-size: 0.8rem;
}

/* ----------------------------- CARD DE PEDIDOS ----------------------------- */
.pedidos-card {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(123, 90, 80, 0.1);
  padding: 25px;
  margin: 0 auto;
  border: 1px solid rgba(123, 90, 80, 0.1);
}

.pedidos-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pedido-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: hidden;
}

.pedido-item::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, var(--color-primary), #f1d0cb);
  opacity: 0.8;
}

.pedido-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(123, 90, 80, 0.15);
  border-color: var(--color-primary);
}

.pedido-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0;
  gap: 20px;
}

.pedido-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.pedido-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.cliente-nombre {
  font-weight: 700;
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0;
}

.pedido-estado-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.pedido-estado-badge.pendiente {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  color: #856404;
}

.pedido-estado-badge.en-preparacion {
  background: linear-gradient(135deg, #d1ecf1, #a6e3e9);
  color: #0c5460;
}

.pedido-estado-badge.entregado {
  background: linear-gradient(135deg, #d4edda, #a8e6a3);
  color: #155724;
}

.pedido-estado-badge.cancelado {
  background: linear-gradient(135deg, #f8d7da, #f5b7b1);
  color: #721c24;
}

.pedido-total {
  font-weight: 700;
  color: var(--color-success);
  font-size: 1.1rem;
  background: rgba(40, 167, 69, 0.1);
  padding: 6px 12px;
  border-radius: 8px;
}

.pedido-datos {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.dato-grupo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
}

.dato-grupo i {
  color: var(--color-primary);
  width: 16px;
  text-align: center;
}

/* ----------------------------- BOTÓN FLOTANTE NUEVA RECETA ----------------------------- */
.btn-nuevo-pedido-flotante {
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

.btn-nuevo-pedido-flotante:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(123, 90, 80, 0.4);
  background: linear-gradient(135deg, #9c7a6d, var(--color-primary));
}

/* ----------------------------- BOTONES DE ACCIÓN ----------------------------- */
.pedido-acciones {
  display: flex;
  align-items: center;
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
}

.btn-accion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.btn-accion:disabled:hover {
  transform: none !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
}

.btn-editar {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.btn-editar:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9, #21618c);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-eliminar {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.btn-eliminar:hover:not(:disabled) {
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
.pedido-detalles-desplegable {
  max-height: 0;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  margin-top: 0;
}

.pedido-detalles-desplegable.active {
  max-height: 1000px;
  margin-top: 20px;
}

.detalles-content {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #dee2e6;
}

.agregar-receta-container {
  margin-bottom: 20px;
  text-align: right;
}

/* ----------------------------- RECETAS E INGREDIENTES ----------------------------- */
.recetas-container {
  margin-top: 15px;
}

.receta-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 10px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.receta-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.receta-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  cursor: pointer;
  transition: background-color 0.2s;
}

.receta-header:hover {
  background: #e9ecef;
}

.receta-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}

.receta-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.receta-nombre {
  font-weight: 600;
  color: #2c3e50;
}

.receta-precio {
  font-weight: 700;
  color: var(--color-success);
  background: rgba(40, 167, 69, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

.receta-header-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-accion-small {
  border: none;
  cursor: pointer;
  font-size: 12px;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.3s ease;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-accion-small:hover {
  transform: translateY(-1px);
}

.receta-detalles {
  padding: 15px;
  background: white;
  border-top: 1px solid #e9ecef;
}

.observaciones {
  margin-bottom: 15px;
  font-style: italic;
  color: #6c757d;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.ingredientes-extras {
  margin-bottom: 15px;
}

.ingredientes-extras h4 {
  margin-bottom: 10px;
  color: var(--color-primary);
  font-size: 1rem;
}

.ingrediente-extra {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed #dee2e6;
}

.ingrediente-acciones {
  display: flex;
  gap: 5px;
}

.receta-acciones {
  text-align: right;
  margin-top: 15px;
}

/* ----------------------------- ESTADOS ESPECIALES ----------------------------- */
.pedido-entregado {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  opacity: 0.8;
}

.pedido-entregado::before {
  background: linear-gradient(to bottom, #28a745, #20c997);
}

.pedido-entregado-mensaje {
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  color: #155724;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

/* ----------------------------- ESTADOS DE CARGA Y VACÍO ----------------------------- */
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

/* Añadir al final de la sección de estilos */
.cursor-pointer {
  cursor: pointer;
}

.pedido-header:hover {
  background-color: rgba(123, 90, 80, 0.03);
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

/* Indicador visual de que es clickeable */
.pedido-header::after {
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

.pedido-header:hover::after {
  box-shadow: inset 0 0 0 2px rgba(123, 90, 80, 0.1);
}

/* ----------------------------- RESPONSIVE ----------------------------- */
@media (max-width: 768px) {
  .pedidos-content {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .filtros-derecha {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .filtro-input,
  .filtro-select {
    min-width: 100%;
  }

  .botones-acciones {
    align-self: flex-start;
  }

  .pedido-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .pedido-acciones {
    align-self: flex-end;
  }

  .pedido-titulo {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .pedido-datos {
    flex-direction: column;
    gap: 10px;
  }

  .receta-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .receta-header-acciones {
    align-self: flex-end;
  }

  .ingrediente-extra {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .ingrediente-acciones {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .pedidos-card {
    padding: 15px;
  }

  .pedido-item {
    padding: 15px;
  }

  .cliente-nombre {
    font-size: 1.1rem;
  }

  .detalles-content {
    padding: 15px;
  }

  .receta-titulo {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
