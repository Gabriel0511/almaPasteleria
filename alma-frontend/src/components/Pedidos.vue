<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content">
        <PageHeader
          title="Gestión de Pedidos"
          :show-total="true"
          :total="estadisticasPedidos.totalActivos"
          :stats="pedidosStats"
          :filters="pedidosFilters"
          :show-clear-button="true"
          :active-filter-type="estadoSeleccionado"
          @stat-click="handlePedidoStatClick"
          @filter-change="handlePedidoFilterChange"
          @clear-filters="limpiarFiltrosPedidos"
        />

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
              v-for="pedido in pedidosPaginados"
              :key="pedido.id"
              class="pedido-item"
              :class="[
                `pedido-${pedido.estado.toLowerCase().replace(' ', '-')}`,
                {
                  'pedido-atrasado': notificacionesPedidosAtrasados.some(
                    (n) => n.pedido.id === pedido.id
                  ),
                  'pedido-hoy': notificacionesPedidosParaHoy.some(
                    (n) => n.pedido.id === pedido.id
                  ),
                  expanded: pedidoDesplegado[pedido.id],
                },
              ]"
            >
              <!-- Contenedor principal compacto -->
              <div class="pedido-item-compact">
                <!-- Indicador de estado -->
                <div
                  class="estado-indicador"
                  :class="pedido.estado.toLowerCase().replace(' ', '-')"
                ></div>

                <!-- Información principal -->
                <div class="info-principal" @click="togglePedido(pedido.id)">
                  <div class="info-header">
                    <h4 class="cliente-nombre">{{ pedido.cliente.nombre }}</h4>
                    <div class="badges-container">
                      <span
                        class="badge-estado"
                        :class="pedido.estado.toLowerCase().replace(' ', '-')"
                      >
                        {{ getEstadoLabel(pedido.estado) }}
                      </span>
                      <span class="badge-total">
                        ${{ calcularTotalPedido(pedido) }}
                      </span>
                    </div>
                  </div>

                  <div class="info-detalles">
                    <div class="detalle-grupo">
                      <span class="detalle-item">
                        <i class="fas fa-calendar-alt"></i>Fecha creación de
                        pedido:
                        {{ formatFecha(pedido.fecha_pedido) }}
                      </span>
                      <span class="detalle-item">
                        <i class="fas fa-industry"></i>
                        Fecha de preparación:
                        {{
                          pedido.fecha_fabricacion
                            ? formatFecha(pedido.fecha_fabricacion)
                            : "Sin definir"
                        }}
                      </span>
                      <span class="detalle-item">
                        <i class="fas fa-truck"></i> Fecha de entrega:
                        {{ formatFecha(pedido.fecha_entrega) }}
                      </span>
                    </div>
                    <div class="detalle-grupo">
                      <span class="detalle-item">
                        <i class="fas fa-list"></i>
                        {{ pedido.detalles.length }} recetas
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Acciones -->
                <div class="acciones-container">
                  <!-- Botón para avanzar al siguiente estado -->
                  <button
                    v-if="
                      pedido.estado !== 'entregado' &&
                      pedido.estado !== 'cancelado'
                    "
                    class="btn-accion btn-siguiente-estado"
                    @click="avanzarEstadoPedido(pedido)"
                    :title="getSiguienteEstadoTitle(pedido.estado)"
                  >
                    <i :class="getSiguienteEstadoIcon(pedido.estado)"></i>
                  </button>

                  <!-- Botón para cancelar pedido -->
                  <button
                    v-if="
                      pedido.estado !== 'entregado' &&
                      pedido.estado !== 'cancelado'
                    "
                    class="btn-accion btn-cancelar"
                    @click="confirmarCancelarPedido(pedido)"
                    title="Cancelar pedido"
                  >
                    <i class="fas fa-ban"></i>
                  </button>

                  <button
                    class="btn-accion btn-editar"
                    @click="editarPedido(pedido)"
                    title="Editar pedido"
                    :disabled="
                      pedido.estado === 'entregado' ||
                      pedido.estado === 'cancelado'
                    "
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
                </div>
              </div>

              <!-- Desplegable de detalles del pedido -->
              <div
                v-if="pedidoDesplegado[pedido.id]"
                class="pedido-detalles-desplegable"
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
                          <div
                            class="receta-observaciones"
                            v-if="detalle.observaciones"
                          >
                            <small>{{ detalle.observaciones }}</small>
                          </div>
                        </div>
                        <div class="receta-header-acciones">
                          <template v-if="pedido.estado !== 'entregado'">
                            <button
                              class="btn-accion btn-accion-small"
                              @click.stop="editarReceta(detalle, pedido)"
                              title="Editar receta"
                            >
                              <i class="fas fa-edit"></i>
                            </button>
                            <button
                              class="btn-accion btn-accion-small btn-eliminar"
                              @click.stop="confirmarEliminarReceta(detalle)"
                              title="Eliminar receta"
                            >
                              <i class="fas fa-trash"></i>
                            </button>
                          </template>
                          <i
                            class="fas chevron-icon"
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
                            <span class="ingrediente-info">
                              {{ ingrediente.insumo.nombre }}:
                              {{ ingrediente.cantidad }}
                              {{ ingrediente.unidad_medida.abreviatura }}
                            </span>

                            <div
                              class="ingrediente-acciones"
                              v-if="pedido.estado !== 'entregado'"
                            >
                              <button
                                class="btn-accion btn-accion-small"
                                @click="
                                  editarIngredienteExtra(ingrediente, detalle)
                                "
                                title="Editar ingrediente"
                              >
                                <i class="fas fa-edit"></i>
                              </button>
                              <button
                                class="btn-accion btn-accion-small btn-eliminar"
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
          <div class="pagination-controls" v-if="totalPaginas > 1">
            <div class="pagination-info">
              Mostrando {{ inicioPagina }}-{{ finPagina }} de
              {{ pedidosFiltrados.length }} pedido(s)
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
              class="btn-agregar"
              @click="showNuevoClienteModal = true"
              title="Agregar nuevo cliente"
            >
              <i class="fas fa-plus"></i>
            </button>
          </div>
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
              :key="estado.value"
              :value="estado.value"
            >
              {{ estado.label }}
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
              class="btn-agregar"
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
              class="btn-agregar"
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
            step="1"
            min="0"
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
                v-for="unidad in unidadesMedida"
                :key="unidad.id"
                :value="unidad.id"
              >
                {{ unidad.nombre }} ({{ unidad.abreviatura }})
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Stock Mínimo:</label>
          <input
            v-model="formInsumo.stock_minimo"
            type="number"
            step="0"
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
          confirm-text="Guardar"
          @cancel="showNuevoInsumoModal = false"
          @confirm="guardarNuevoInsumo"
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

  <!-- Modal de confirmación para cancelar pedido -->
  <ConfirmModal
    :show="showConfirmModalCancelar"
    title="Confirmar Cancelación"
    :message="`¿Está seguro de que desea cancelar el pedido de '${pedidoACancelar?.cliente?.nombre}'? Esta acción no se puede deshacer.`"
    confirm-text="Cancelar Pedido"
    @update:show="showConfirmModalCancelar = $event"
    @cancel="showConfirmModalCancelar = false"
    @confirm="cancelarPedido"
  />
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref, computed, onMounted, inject } from "vue";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";
import BaseModal from "./Modals/BaseModal.vue";
import ModalButtons from "./Modals/ModalButtons.vue";
import ConfirmModal from "./Modals/ConfirmModal.vue";
import PageHeader from "./PageHeader.vue";
import axios from "axios";

const router = useRouter();
const notificationSystem = inject("notifications");

// Variables de estado
const sidebarRef = ref(null);
const pedidos = ref([]);
const clientes = ref([]);
const recetas = ref([]);
const insumos = ref([]);
const categorias = ref([]);
const unidadesMedida = ref([]);
const proveedores = ref([]);
const estadoSeleccionado = ref("");
const searchTerm = ref("");
const loading = ref(true);
const detalleExpandido = ref({});
const pedidoDesplegado = ref({});
const filtroAtrasados = ref(false);

// Modales
const showModalPedido = ref(false);
const showNuevoClienteModal = ref(false);
const showModalReceta = ref(false);
const showNuevoInsumoModal = ref(false);
const showNuevaRecetaModal = ref(false);
const showNuevaCategoriaModal = ref(false);
const showNuevoProveedorModal = ref(false);
const showModalIngrediente = ref(false);
const showConfirmModalPedido = ref(false);
const showConfirmModalIngrediente = ref(false);
const showConfirmModalReceta = ref(false);
const showConfirmModalCancelar = ref(false);
const pedidoACancelar = ref(null);

// Variables de paginación
const paginaActual = ref(1);
const itemsPorPagina = ref(10);

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

// Método para alternar el sidebar
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};

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
  { value: "pendiente", label: "Pendiente", color: "warning", order: 1 },
  { value: "en preparación", label: "En preparación", color: "info", order: 2 }, // ← con acento
  { value: "listo", label: "Listo para entregar", color: "success", order: 3 },
  { value: "entregado", label: "Entregado", color: "secondary", order: 4 },
  { value: "cancelado", label: "Cancelado", color: "danger", order: 5 },
]);

const getEstadoValues = computed(() => estadosPedido.value.map((e) => e.value));

const getEstadoLabel = (estadoValue) => {
  const estado = estadosPedido.value.find((e) => e.value === estadoValue);
  return estado ? estado.label : estadoValue;
};

// Computed properties
// Busca pedidosFiltrados (alrededor de la línea 300-350):
const pedidosFiltrados = computed(() => {
  let filtered = pedidos.value;

  // Filtrar por estado
  if (estadoSeleccionado.value) {
    filtered = filtered.filter(
      (pedido) => pedido.estado === estadoSeleccionado.value
    );
  } else {
    // Si no hay estado seleccionado, excluir los entregados y cancelados
    filtered = filtered.filter(
      (pedido) => pedido.estado !== "entregado" && pedido.estado !== "cancelado"
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

  // Filtrar por atrasados
  if (filtroAtrasados.value) {
    const hoy = new Date().toISOString().split("T")[0];
    filtered = filtered.filter((pedido) => {
      return (
        pedido.fecha_entrega < hoy &&
        pedido.estado !== "entregado" &&
        pedido.estado !== "cancelado"
      );
    });
  }

  // Ordenar por fecha de pedido (más reciente primero)
  return filtered.sort((a, b) => {
    const fechaA = new Date(a.fecha_pedido).getTime();
    const fechaB = new Date(b.fecha_pedido).getTime();
    return fechaB - fechaA;
  });
});

const pedidosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * itemsPorPagina.value;
  const fin = inicio + itemsPorPagina.value;
  return pedidosFiltrados.value.slice(inicio, fin);
});

const totalPaginas = computed(() => {
  return Math.ceil(pedidosFiltrados.value.length / itemsPorPagina.value);
});

const inicioPagina = computed(() => {
  return (paginaActual.value - 1) * itemsPorPagina.value + 1;
});

const finPagina = computed(() => {
  const fin = paginaActual.value * itemsPorPagina.value;
  return Math.min(fin, pedidosFiltrados.value.length);
});

const paginasVisibles = computed(() => {
  const paginas = [];
  const total = totalPaginas.value;
  const actual = paginaActual.value;
  const maxPaginasVisibles = 5;

  if (total <= maxPaginasVisibles) {
    for (let i = 1; i <= total; i++) {
      paginas.push(i);
    }
  } else {
    if (actual <= 3) {
      for (let i = 1; i <= 4; i++) paginas.push(i);
      paginas.push(total);
    } else if (actual >= total - 2) {
      paginas.push(1);
      for (let i = total - 3; i <= total; i++) paginas.push(i);
    } else {
      paginas.push(1);
      for (let i = actual - 1; i <= actual + 1; i++) paginas.push(i);
      paginas.push(total);
    }
  }

  return paginas;
});

const mostrarPuntosSuspensivos = computed(() => {
  return (
    totalPaginas.value > 5 &&
    !(paginaActual.value <= 3 || paginaActual.value >= totalPaginas.value - 2)
  );
});

const cambiarPagina = (pagina) => {
  if (pagina >= 1 && pagina <= totalPaginas.value) {
    // Cerrar todos los pedidos desplegados al cambiar de página
    cerrarTodosLosPedidos();
    paginaActual.value = pagina;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};

const resetearPaginacion = () => {
  cerrarTodosLosPedidos();
  paginaActual.value = 1;
};

const cerrarTodosLosPedidos = () => {
  pedidoDesplegado.value = {};
};

const notificacionesPedidosAtrasados = computed(() => {
  const hoy = new Date().toISOString().split("T")[0];

  return pedidos.value
    .filter((pedido) => {
      if (pedido.estado === "entregado" || pedido.estado === "cancelado") {
        return false;
      }
      return pedido.fecha_entrega < hoy;
    })
    .map((pedido) => ({
      id: `pedido-atrasado-${pedido.id}`,
      type: "critical",
      title: "Pedido Atrasado",
      message: `El pedido de ${
        pedido.cliente.nombre
      } está atrasado (Entrega: ${formatFecha(pedido.fecha_entrega)})`,
      timestamp: new Date(),
      read: false,
      pedido: pedido,
    }));
});

const notificacionesPedidosParaHoy = computed(() => {
  const hoy = new Date().toISOString().split("T")[0];

  return pedidos.value
    .filter((pedido) => {
      if (pedido.estado === "entregado" || pedido.estado === "cancelado") {
        return false;
      }
      return pedido.fecha_entrega === hoy;
    })
    .map((pedido) => ({
      id: `pedido-hoy-${pedido.id}`,
      type: "warning",
      title: "Entrega Hoy",
      message: `El pedido de ${pedido.cliente.nombre} debe entregarse hoy`,
      timestamp: new Date(),
      read: false,
      pedido: pedido,
    }));
});

const notificacionesPedidosParaManana = computed(() => {
  const manana = new Date();
  manana.setDate(manana.getDate() + 1);
  const mananaStr = manana.toISOString().split("T")[0];

  return pedidos.value
    .filter((pedido) => {
      if (pedido.estado === "entregado" || pedido.estado === "cancelado") {
        return false;
      }
      return pedido.fecha_entrega === mananaStr;
    })
    .map((pedido) => ({
      id: `pedido-manana-${pedido.id}`,
      type: "info",
      title: "Entrega Mañana",
      message: `El pedido de ${pedido.cliente.nombre} se entrega mañana`,
      timestamp: new Date(),
      read: false,
      pedido: pedido,
    }));
});

const logout = async () => {
  try {
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
      await axios.post("/api/auth/logout/", { refresh: refreshToken });
    }
  } catch (err) {
    // Solo registrar error en consola para debugging
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete axios.defaults.headers.common["Authorization"];
    router.push("/login");
  }
};

const togglePedido = (pedidoId) => {
  pedidoDesplegado.value = {
    ...pedidoDesplegado.value,
    [pedidoId]: !pedidoDesplegado.value[pedidoId],
  };
};

const formatFecha = (fecha) => {
  if (!fecha) return "";

  const fechaLocal = new Date(fecha);
  const fechaAjustada = new Date(
    fechaLocal.getTime() + fechaLocal.getTimezoneOffset() * 60000
  );

  return fechaAjustada.toLocaleDateString("es-AR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
};

// Función para convertir entre unidades de medida
const convertirUnidad = (cantidad, unidadOrigen, unidadDestino) => {
  if (unidadOrigen === unidadDestino) {
    return cantidad;
  }

  const conversiones = {
    kg: { g: 1000, mg: 1000000, lb: 2.20462, oz: 35.274 },
    g: { kg: 0.001, mg: 1000, lb: 0.00220462, oz: 0.035274 },
    mg: { kg: 0.000001, g: 0.001, lb: 0.00000220462, oz: 0.000035274 },
    lb: { kg: 0.453592, g: 453.592, mg: 453592, oz: 16 },
    oz: { kg: 0.0283495, g: 28.3495, mg: 28349.5, lb: 0.0625 },
    l: { ml: 1000, cl: 100, dl: 10, gal: 0.264172 },
    ml: { l: 0.001, cl: 0.1, dl: 0.01, gal: 0.000264172 },
    cl: { l: 0.01, ml: 10, dl: 0.1, gal: 0.00264172 },
    dl: { l: 0.1, ml: 100, cl: 10, gal: 0.0264172 },
    gal: { l: 3.78541, ml: 3785.41, cl: 378.541, dl: 37.8541 },
    unidad: { unidad: 1 },
    porcion: { porcion: 1 },
    paquete: { paquete: 1 },
    caja: { caja: 1 },
  };

  const normalizarUnidad = (unidad) => {
    const normalizadas = {
      kilogramo: "kg",
      kilogramos: "kg",
      kilo: "kg",
      gramo: "g",
      gramos: "g",
      miligramo: "mg",
      miligramos: "mg",
      libra: "lb",
      libras: "lb",
      onza: "oz",
      onzas: "oz",
      litro: "l",
      litros: "l",
      mililitro: "ml",
      mililitros: "ml",
      centilitro: "cl",
      centilitros: "cl",
      decilitro: "dl",
      decilitros: "dl",
      galon: "gal",
      galones: "gal",
      unidades: "unidad",
      unidad: "unidad",
      porciones: "porcion",
      porcion: "porcion",
      paquetes: "paquete",
      paquete: "paquete",
      cajas: "caja",
      caja: "caja",
    };
    return normalizadas[unidad.toLowerCase()] || unidad.toLowerCase();
  };

  const origenNorm = normalizarUnidad(unidadOrigen);
  const destinoNorm = normalizarUnidad(unidadDestino);

  if (!conversiones[origenNorm] || !conversiones[origenNorm][destinoNorm]) {
    return cantidad;
  }

  return cantidad * conversiones[origenNorm][destinoNorm];
};

// Función para obtener el siguiente estado
const getSiguienteEstado = (estadoActual) => {
  const estadosOrdenados = estadosPedido.value.sort(
    (a, b) => a.order - b.order
  );
  const indexActual = estadosOrdenados.findIndex(
    (e) => e.value === estadoActual
  );

  if (indexActual === -1 || indexActual >= estadosOrdenados.length - 2) {
    return null; // No hay siguiente estado o ya está en entregado/cancelado
  }

  return estadosOrdenados[indexActual + 1].value;
};

// Función para obtener el título del botón según el estado actual
const getSiguienteEstadoTitle = (estadoActual) => {
  const siguiente = getSiguienteEstado(estadoActual);
  if (!siguiente) return "";

  const estados = {
    pendiente: "Marcar como En preparación",
    "en preparación": "Marcar como Listo para entregar",
    listo: "Marcar como Entregado",
  };

  return estados[estadoActual] || `Cambiar a ${siguiente}`;
};

// Función para obtener el ícono del botón según el estado actual
const getSiguienteEstadoIcon = (estadoActual) => {
  const iconos = {
    pendiente: "fas fa-utensils", // De pendiente a preparación
    "en preparación": "fas fa-check-circle", // De preparación a listo
    listo: "fas fa-truck", // De listo a entregado
  };

  return iconos[estadoActual] || "fas fa-arrow-right";
};

// Función para avanzar al siguiente estado
const avanzarEstadoPedido = async (pedido) => {
  try {
    const siguienteEstado = getSiguienteEstado(pedido.estado);

    if (!siguienteEstado) {
      notificationSystem.show({
        type: "warning",
        title: "No se puede avanzar",
        message: "Este pedido ya está en el último estado posible",
        timeout: 4000,
      });
      return;
    }

    const datosActualizacion = {
      cliente_id: pedido.cliente.id,
      fecha_pedido: pedido.fecha_pedido,
      fecha_entrega: pedido.fecha_entrega,
      estado: siguienteEstado,
    };

    const response = await axios.put(
      `/api/pedidos/${pedido.id}/`,
      datosActualizacion
    );

    const pedidoActualizado = response.data;
    const index = pedidos.value.findIndex((p) => p.id === pedido.id);
    if (index !== -1) {
      pedidos.value[index] = { ...pedidos.value[index], ...pedidoActualizado };
    }

    // Obtener el label del nuevo estado para el mensaje
    const nuevoEstadoObj = estadosPedido.value.find(
      (e) => e.value === siguienteEstado
    );
    const labelNuevoEstado = nuevoEstadoObj
      ? nuevoEstadoObj.label
      : siguienteEstado;

    notificationSystem.show({
      type: "success",
      title: "Estado Actualizado",
      message: `Pedido de ${pedido.cliente.nombre} cambiado a: ${labelNuevoEstado}`,
      timeout: 4000,
    });
  } catch (error) {
    let mensajeError = "Error al actualizar el estado del pedido";
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

// Función para confirmar cancelación de pedido
const confirmarCancelarPedido = (pedido) => {
  if (pedido.estado === "entregado") {
    notificationSystem.show({
      type: "warning",
      title: "No se puede cancelar",
      message: "No se puede cancelar un pedido ya entregado",
      timeout: 4000,
    });
    return;
  }
  pedidoACancelar.value = pedido;
  showConfirmModalCancelar.value = true;
};

// Función para cancelar pedido
const cancelarPedido = async () => {
  try {
    const datosActualizacion = {
      cliente_id: pedidoACancelar.value.cliente.id,
      fecha_pedido: pedidoACancelar.value.fecha_pedido,
      fecha_entrega: pedidoACancelar.value.fecha_entrega,
      estado: "cancelado",
    };

    const response = await axios.put(
      `/api/pedidos/${pedidoACancelar.value.id}/`,
      datosActualizacion
    );

    const pedidoActualizado = response.data;
    const index = pedidos.value.findIndex(
      (p) => p.id === pedidoACancelar.value.id
    );
    if (index !== -1) {
      pedidos.value[index] = { ...pedidos.value[index], ...pedidoActualizado };
    }

    showConfirmModalCancelar.value = false;

    notificationSystem.show({
      type: "success",
      title: "Pedido Cancelado",
      message: `Pedido de ${pedidoACancelar.value.cliente.nombre} ha sido cancelado`,
      timeout: 4000,
    });
  } catch (error) {
    let mensajeError = "Error al cancelar el pedido";
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

// Función para calcular total del pedido
const calcularTotalPedido = (pedido) => {
  let total = 0;

  if (pedido.detalles) {
    pedido.detalles.forEach((detalle) => {
      const precioReceta = parseFloat(detalle.receta?.precio_venta) || 0;
      const cantidadReceta = parseFloat(detalle.cantidad) || 0;
      const subtotalReceta = precioReceta * cantidadReceta;
      total += subtotalReceta;

      if (
        detalle.ingredientes_extra &&
        Array.isArray(detalle.ingredientes_extra)
      ) {
        detalle.ingredientes_extra.forEach((ingrediente) => {
          const precioIngrediente =
            parseFloat(ingrediente.insumo?.precio_unitario) || 0;
          const cantidadIngrediente = parseFloat(ingrediente.cantidad) || 0;

          const unidadInsumo =
            ingrediente.insumo?.unidad_medida?.abreviatura || "unidad";
          const unidadIngrediente =
            ingrediente.unidad_medida?.abreviatura || "unidad";

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

    // Calcular fecha de fabricación (3 días antes de la entrega)
    const fechaEntrega = new Date(formPedido.value.fecha_entrega);
    const fechaFabricacion = new Date(fechaEntrega);
    fechaFabricacion.setDate(fechaEntrega.getDate() - 3);

    const fechaFabricacionStr = fechaFabricacion.toISOString().split("T")[0];

    let response;
    if (esEdicionPedido.value) {
      const datosActualizacion = {
        cliente_id: formPedido.value.cliente_id,
        fecha_pedido: formPedido.value.fecha_pedido,
        fecha_entrega: formPedido.value.fecha_entrega,
        estado: formPedido.value.estado,
      };

      response = await axios.put(
        `/api/pedidos/${formPedido.value.id}/`,
        datosActualizacion
      );

      await fetchPedidos();
      closeModal();

      notificationSystem.show({
        type: "success",
        title: "Pedido actualizado",
        message: `Pedido actualizado correctamente. Fecha de fabricación recalculada: ${formatFecha(
          fechaFabricacionStr
        )}`,
        timeout: 5000,
      });
    } else {
      const datosNuevoPedido = {
        cliente_id: formPedido.value.cliente_id,
        fecha_pedido: formPedido.value.fecha_pedido,
        fecha_entrega: formPedido.value.fecha_entrega,
        estado: formPedido.value.estado,
        detalles: [],
      };

      response = await axios.post("/api/pedidos/", datosNuevoPedido);

      await fetchPedidos();
      closeModal();

      notificationSystem.show({
        type: "success",
        title: "Pedido creado",
        message: `Pedido creado correctamente. La fecha de fabricación automática es: ${formatFecha(
          fechaFabricacionStr
        )}`,
        timeout: 5000,
      });

      const nuevoPedidoCompleto = pedidos.value.find(
        (pedido) => pedido.id === response.data.id
      );

      if (nuevoPedidoCompleto) {
        setTimeout(() => {
          showAgregarRecetaModal(nuevoPedidoCompleto);
        }, 500);
      }
    }
  } catch (error) {
    let errorMessage = "Error al guardar el pedido";

    if (error.response?.data) {
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
      timeout: 6000,
    });
  }
};

const guardarCliente = async () => {
  try {
    await axios.post("/api/clientes/", formCliente.value);
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
    let errorMessage = "Error al guardar el cliente";

    if (error.response?.status === 400) {
      if (error.response.data?.error) {
        errorMessage = error.response.data.error;
      } else if (typeof error.response.data === "object") {
        const errors = [];
        for (const key in error.response.data) {
          if (Array.isArray(error.response.data[key])) {
            errors.push(...error.response.data[key]);
          } else {
            errors.push(`${key}: ${error.response.data[key]}`);
          }
        }
        errorMessage = errors.join(", ");
      } else if (typeof error.response.data === "string") {
        errorMessage = error.response.data;
      }
    } else if (error.response?.status === 409) {
      errorMessage = "Ya existe un cliente con ese nombre o teléfono";
    } else if (!error.response) {
      errorMessage = "Error de conexión. Verifique su internet.";
    }

    notificationSystem.show({
      type: "error",
      title: "Error al crear cliente",
      message: errorMessage,
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

    await fetchCategorias();
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

    await fetchProveedores();
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

    const datosParaEnviar = {
      nombre: formInsumo.value.nombre,
      categoria_id: formInsumo.value.categoria_id || null,
      unidad_medida_id: formInsumo.value.unidad_medida_id,
      stock_minimo: parseFloat(formInsumo.value.stock_minimo),
      precio_unitario: formInsumo.value.precio_unitario
        ? parseFloat(formInsumo.value.precio_unitario)
        : null,
      proveedor_id: formInsumo.value.proveedor_id || null,
      stock_actual: 0,
      activo: true,
    };

    const response = await axios.post("/api/insumos/crear/", datosParaEnviar);

    await fetchInsumos();
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

    const datosReceta = {
      nombre: formReceta.value.nombre,
      rinde: formReceta.value.rinde,
      unidad_rinde: formReceta.value.unidad_rinde,
      costo_unitario: parseFloat(formReceta.value.costo_unitario) || 0,
      costo_total: parseFloat(formReceta.value.costo_total) || 0,
      precio_venta: parseFloat(formReceta.value.precio_venta) || 0,
    };

    const response = await axios.post("/api/recetas/", datosReceta);

    await fetchRecetas();
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

// Computed properties para el PageHeader
const pedidosStats = computed(() => {
  // Contar pedidos por estado
  const counts = {};
  estadosPedido.value.forEach((estado) => {
    counts[estado.value] = pedidos.value.filter(
      (p) => p.estado === estado.value
    ).length;
  });

  // Crear stats para cada estado
  return estadosPedido.value.map((estado) => {
    const count = counts[estado.value] || 0;

    return {
      type: estado.color, // Usar el color definido para cada estado
      label: `${count} ${estado.label}`,
      compactLabel: `${count} ${estado.label.split(" ")[0]}`, // Para mobile: solo primera palabra
      icon: getEstadoIcon(estado.value),
      tooltip: `Ver pedidos ${estado.label.toLowerCase()}`,
      value: estado.value,
      count: count,
    };
  });
});

// Agrega esta función para obtener iconos por estado:
const getEstadoIcon = (estado) => {
  const icons = {
    pendiente: "fas fa-clock",
    "en preparación": "fas fa-utensils",
    listo: "fas fa-check-circle",
    entregado: "fas fa-truck",
    cancelado: "fas fa-ban",
  };
  return icons[estado] || "fas fa-circle";
};

const pedidosFilters = computed(() => [
  {
    type: "text",
    placeholder: "Buscar cliente...",
    value: searchTerm.value,
    autocomplete: "off",
  },
  {
    type: "checkbox",
    label: "Solo atrasados",
    checked: filtroAtrasados.value,
    id: "filtro-atrasados",
  },
]);

// Métodos para manejar eventos del PageHeader
const handlePedidoStatClick = (stat) => {
  // Si ya está seleccionado este estado, limpiar filtro
  if (estadoSeleccionado.value === stat.value) {
    estadoSeleccionado.value = "";
    searchTerm.value = "";
    filtroAtrasados.value = false;
  } else {
    // Seleccionar este estado específico
    estadoSeleccionado.value = stat.value;
    searchTerm.value = "";
    filtroAtrasados.value = false;
  }
  resetearPaginacion();
};

const handlePedidoFilterChange = ({ filter, value }) => {
  if (filter.placeholder?.includes("Buscar cliente")) {
    searchTerm.value = value;
    resetearPaginacion();
  } else if (filter.placeholder?.includes("Estado")) {
    estadoSeleccionado.value = value;
    resetearPaginacion();
  } else if (filter.type === "checkbox" && filter.id === "filtro-atrasados") {
    filtroAtrasados.value = value;
    resetearPaginacion();
  }
};

const limpiarFiltrosPedidos = () => {
  estadoSeleccionado.value = "";
  searchTerm.value = "";
  filtroAtrasados.value = false;
  resetearPaginacion();
};

// Método para obtener estadísticas rápidas
const estadisticasPedidos = computed(() => {
  const hoy = new Date().toISOString().split("T")[0];
  const atrasados = notificacionesPedidosAtrasados.value.length;
  const paraHoy = notificacionesPedidosParaHoy.value.length;
  const paraManana = notificacionesPedidosParaManana.value.length;

  const totalActivos = pedidos.value.filter(
    (p) => p.estado !== "entregado" && p.estado !== "cancelado"
  ).length;

  return {
    atrasados,
    paraHoy,
    paraManana,
    totalActivos,
  };
});

const closeModal = () => {
  showModalPedido.value = false;
  showNuevoClienteModal.value = false;
  showModalReceta.value = false;
  showModalIngrediente.value = false;
  showNuevaRecetaModal.value = false;
  showNuevoInsumoModal.value = false;
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
    // Error silencioso
  }
};

const fetchProveedores = async () => {
  try {
    const response = await axios.get("/api/proveedores/");
    proveedores.value = response.data;
  } catch (err) {
    // Error silencioso
  }
};

const fetchClientes = async () => {
  try {
    const response = await axios.get("/api/clientes/");
    clientes.value = response.data;
  } catch (err) {
    // Error silencioso
  }
};

const fetchRecetas = async () => {
  try {
    const response = await axios.get("/api/recetas/");
    recetas.value = response.data;
  } catch (err) {
    // Error silencioso
  }
};

const fetchInsumos = async () => {
  try {
    const response = await axios.get("/api/insumos/");
    insumos.value = response.data.insumos || response.data;
  } catch (err) {
    // Error silencioso
  }
};

const fetchUnidadesMedida = async () => {
  try {
    const response = await axios.get("/api/unidades-medida/");
    unidadesMedida.value = response.data;
  } catch (err) {
    // Error silencioso
  }
};

// Cargar datos al montar el componente
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  Promise.all([
    fetchPedidos(),
    fetchClientes(),
    fetchRecetas(),
    fetchInsumos(),
    fetchUnidadesMedida(),
    fetchCategorias(),
    fetchProveedores(),
  ]).catch((error) => {
    loading.value = false;
    if (error.response?.status === 401) {
      logout();
    }
  });
});
</script>

<style scoped>
/* ----------------------------- CARD DE PEDIDOS ----------------------------- */
.pedidos-card {
  max-height: calc(100vh - 220px);
  overflow-y: auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 16px;
  margin: 0 auto;
  border: 1px solid #eaeaea;
}

.pedidos-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pedido-item {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  border-left: 4px solid #f0f0f0;
}

/* Estados de los pedidos */
.pedido-item.pedido-pendiente {
  border-left: 4px solid #ffc107; /* Amarillo */
}

.pedido-item.pedido-en-preparación {
  border-left: 4px solid #17a2b8; /* Azul turquesa */
}

.pedido-item.pedido-listo {
  border-left: 4px solid #28a745; /* Verde */
}

.pedido-item.pedido-entregado {
  border-left: 4px solid #6c757d; /* Gris */
}

.pedido-item.pedido-cancelado {
  border-left: 4px solid #dc3545; /* Rojo */
}

/* Hover effect para todos los estados */
.pedido-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

/* Contenedor compacto */
.pedido-item-compact {
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

.estado-indicador.pendiente {
  background-color: #ffc107; /* Amarillo */
  box-shadow: 0 0 0 3px rgba(255, 193, 7, 0.2);
}

.estado-indicador.en-preparación {
  background-color: #17a2b8; /* Azul turquesa */
  box-shadow: 0 0 0 3px rgba(23, 162, 184, 0.2);
}

.estado-indicador.listo {
  background-color: #28a745; /* Verde */
  box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.2);
}

.estado-indicador.entregado {
  background-color: #6c757d; /* Gris */
  box-shadow: 0 0 0 3px rgba(108, 117, 125, 0.2);
}

.estado-indicador.cancelado {
  background-color: #dc3545; /* Rojo */
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.2);
}

/* Información principal */
.info-principal {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
  gap: 8px;
}

.cliente-nombre {
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

.badge-estado,
.badge-total {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge-estado.pendiente {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  color: #856404;
}

.badge-estado.en-preparación {
  background: linear-gradient(135deg, #d1ecf1, #a6e3e9);
  color: #0c5460;
}

.badge-estado.listo {
  background: linear-gradient(135deg, #d4edda, #a8e6a3);
  color: #155724;
}

.badge-estado.entregado {
  background: linear-gradient(135deg, #e2e3e5, #c8c9cb);
  color: #383d41;
}

.badge-estado.cancelado {
  background: linear-gradient(135deg, #f8d7da, #f5b7b1);
  color: #721c24;
}

.badge-total {
  background: #e9ecef;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.info-detalles {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detalle-grupo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detalle-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: #6c757d;
}

.detalle-item i {
  width: 12px;
  text-align: center;
  color: var(--color-primary);
}

.fecha-atrasada {
  color: #dc3545 !important;
  font-weight: 600;
}

.fecha-hoy {
  color: #e0a800 !important;
  font-weight: 600;
}

/* Acciones */
.acciones-container {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  flex-wrap: nowrap;
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

.btn-accion:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.btn-accion:disabled:hover {
  transform: none !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
}

.btn-entregado {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.btn-entregado:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1c7430);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(40, 167, 69, 0.3);
}

.btn-editar {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.btn-editar:hover:not(:disabled) {
  background: linear-gradient(135deg, #2980b9, #21618c);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
}

.btn-eliminar {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
}

.btn-eliminar:hover:not(:disabled) {
  background: linear-gradient(135deg, #c0392b, #a93226);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(231, 76, 60, 0.3);
}

/* Botones pequeños para acciones internas */
.btn-accion-small {
  width: 28px;
  height: 28px;
  font-size: 11px;
}

/* ----------------------------- DESPLEGABLE DE DETALLES ----------------------------- */
.pedido-detalles-desplegable {
  background: #fafbfc;
  border-top: 1px solid #eef1f4;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

.detalles-content {
  padding: 20px;
}

.agregar-receta-container {
  margin-bottom: 20px;
  text-align: left;
  border-bottom: 1px dashed #e1e5e9;
  padding-bottom: 16px;
}

.btn-agregar-receta {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 12px 20px;
  cursor: pointer;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(40, 167, 69, 0.2);
  font-size: 0.9rem;
}

.btn-agregar-receta:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
  background: linear-gradient(135deg, #218838, #1e9e8a);
}

.pedido-entregado-mensaje {
  background: linear-gradient(135deg, #d4f7e2, #c3f0d9);
  color: #0f5132;
  padding: 14px 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  text-align: center;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 0.9rem;
  border-left: 4px solid #28a745;
}

.pedido-entregado-mensaje i {
  color: #28a745;
  font-size: 1.1rem;
}

/* ----------------------------- RECETAS E INGREDIENTES ----------------------------- */
.recetas-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.receta-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.receta-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #d1e7ff;
}

.receta-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa, #f1f3f5);
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid transparent;
}

.receta-header:hover {
  background: linear-gradient(135deg, #f1f3f5, #e9ecef);
}

.receta-info {
  flex: 1;
  min-width: 0;
}

.receta-titulo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  gap: 12px;
}

.receta-nombre {
  font-weight: 700;
  color: #2c3e50;
  font-size: 1rem;
  flex: 1;
}

.receta-precio {
  font-weight: 700;
  color: #28a745;
  background: rgba(40, 167, 69, 0.1);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  border: 1px solid rgba(40, 167, 69, 0.2);
  white-space: nowrap;
}

.receta-observaciones {
  font-size: 0.8rem;
  color: #6c757d;
  font-style: italic;
  background: rgba(108, 117, 125, 0.05);
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.receta-header-acciones {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
}

.chevron-icon {
  color: #6c757d;
  font-size: 0.9rem;
  transition: transform 0.2s ease;
}

.receta-header:hover .chevron-icon {
  color: #495057;
}

.receta-detalles {
  padding: 20px;
  background: white;
  border-top: 1px solid #f1f3f5;
  animation: slideDown 0.2s ease-out;
}

.ingredientes-extras {
  margin-bottom: 20px;
}

.ingredientes-extras h4 {
  margin-bottom: 12px;
  color: #495057;
  font-size: 0.95rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e9ecef;
}

.ingrediente-extra {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  transition: all 0.2s ease;
  margin-bottom: 8px;
}

.ingrediente-extra:hover {
  background: #ffffff;
  border-color: #d1e7ff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.ingrediente-extra:last-child {
  margin-bottom: 0;
}

.ingrediente-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: #495057;
  flex: 1;
}

.ingrediente-acciones {
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.ingrediente-extra:hover .ingrediente-acciones {
  opacity: 1;
}

.receta-acciones {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed #e9ecef;
}

.btn-agregar-ingrediente {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(23, 162, 184, 0.2);
  font-size: 0.85rem;
}

.btn-agregar-ingrediente:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(23, 162, 184, 0.3);
  background: linear-gradient(135deg, #138496, #117a8b);
}

.receta-item.expanded .receta-header {
  background: linear-gradient(135deg, #e3f2fd, #e1f5fe);
  border-bottom-color: #d1e7ff;
}

.receta-item.expanded .receta-header .chevron-icon {
  transform: rotate(180deg);
  color: #007bff;
}

/* ----------------------------- BOTÓN FLOTANTE NUEVO PEDIDO ----------------------------- */
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

/* ----------------------------- PAGINACIÓN ----------------------------- */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
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

/* SECCION DE ACCIONES */

.btn-siguiente-estado {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.btn-siguiente-estado:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1c7430);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(40, 167, 69, 0.3);
}

.btn-cancelar {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: white;
}

.btn-cancelar:hover:not(:disabled) {
  background: linear-gradient(135deg, #e0a800, #d39e00);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(255, 193, 7, 0.3);
}

/* ==============================
   RESPONSIVE DESIGN
   ============================== */

/* Tablets */
@media (max-width: 1024px) {
  .pedidos-card {
    padding: 15px;
  }

  .detalles-content {
    padding: 18px;
  }

  .receta-header {
    padding: 14px 18px;
  }

  .receta-detalles {
    padding: 18px;
  }
}

/* Tablets pequeñas y móviles grandes */
@media (max-width: 768px) {
  .pedidos-card {
    padding: 12px;
  }

  .pedido-item-compact {
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

  .info-detalles {
    flex-direction: column;
    gap: 6px;
  }

  .detalle-grupo {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .detalles-content {
    padding: 16px;
  }

  .receta-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding: 14px 16px;
  }

  .receta-titulo {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .receta-precio {
    align-self: flex-start;
  }

  .receta-header-acciones {
    align-self: flex-end;
    margin-left: 0;
    margin-top: 8px;
  }

  .ingrediente-extra {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    padding: 14px;
  }

  .ingrediente-info {
    justify-content: space-between;
  }

  .ingrediente-acciones {
    align-self: flex-end;
    opacity: 1;
  }

  .receta-acciones {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .btn-agregar-ingrediente {
    justify-content: center;
  }

  .btn-nuevo-pedido-flotante {
    bottom: 20px;
    right: 20px;
    padding: 14px 20px;
    font-size: 0.9rem;
  }

  .acciones-container {
    gap: 4px;
  }

  .btn-accion {
    width: 30px;
    height: 30px;
    font-size: 11px;
  }
}

/* Móviles pequeños */
@media (max-width: 480px) {
  .pedidos-card {
    padding: 8px;
  }

  .pedido-item-compact {
    padding: 8px 10px;
    gap: 8px;
  }

  .cliente-nombre {
    font-size: 0.9rem;
  }

  .badge-estado,
  .badge-total {
    font-size: 0.65rem;
    padding: 2px 6px;
  }

  .detalle-item {
    font-size: 0.75rem;
  }

  .acciones-container {
    gap: 2px;
  }

  .btn-accion {
    width: 28px;
    height: 28px;
    padding: 5px;
  }

  .btn-accion i {
    font-size: 0.8rem;
  }

  .btn-nuevo-pedido-flotante {
    bottom: 15px;
    right: 15px;
    padding: 12px 18px;
    font-size: 0.8rem;
  }

  .btn-nuevo-pedido-flotante span {
    display: none;
  }

  .detalles-content {
    padding: 12px;
  }

  .agregar-receta-container {
    text-align: center;
  }

  .btn-agregar-receta {
    width: 100%;
    justify-content: center;
    padding: 14px 16px;
  }

  .receta-header {
    padding: 12px 14px;
  }

  .receta-detalles {
    padding: 14px;
  }

  .ingrediente-extra {
    padding: 12px;
  }

  .ingrediente-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}

/* Pantallas muy pequeñas */
@media (max-width: 360px) {
  .pedido-item-compact {
    padding: 6px 8px;
    gap: 6px;
  }

  .cliente-nombre {
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
  .pedido-item:hover {
    transform: none;
  }

  .ingrediente-acciones {
    opacity: 1;
  }

  .receta-item:hover {
    transform: none;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  }

  .btn-agregar-receta,
  .btn-agregar-ingrediente,
  .btn-accion {
    min-height: 44px;
    min-width: 44px;
  }

  .btn-nuevo-pedido-flotante {
    min-height: 44px;
  }
}
</style>
