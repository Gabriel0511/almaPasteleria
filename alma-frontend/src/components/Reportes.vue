<template>
  <div class="app-layout">
    <Sidebar ref="sidebarRef" />

    <div class="main-container">
      <Header @toggle-sidebar="toggleSidebar" />
      <main class="main-content-repo">
        <div class="reportes-container">

          <!-- Pestañas para las 5 tablas -->
          <div class="tabs-container">
            <div class="tabs-header">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="cambiarTab(tab.id)"
                class="tab-button"
                :class="{ active: tabActiva === tab.id }"
              >
                <i :class="tab.icono"></i>
                {{ tab.nombre }}
                <span class="badge-contador">
                  {{ obtenerContador(tab.id) }}
                </span>
              </button>
            </div>

            <!-- Contenido de las pestañas -->
            <div class="tabs-content">
              <!-- Pestaña 1: Insumos Usados -->
              <div v-show="tabActiva === 'insumos-usados'" class="tab-pane">
                <!-- FILTROS ESPECÍFICOS - Insumos Usados -->
                <div class="filtros-pestaña">
                  <div class="filtros-grid">
                    <!-- Fecha Inicio -->
                    <div class="filtro-group">
                      <label for="fecha-inicio-insumos">Fecha Inicio</label>
                      <input
                        id="fecha-inicio-insumos"
                        type="date"
                        v-model="filtrosInsumosUsados.fechaInicio"
                        :max="filtrosInsumosUsados.fechaFin || fechaHoy"
                        class="filtro-input"
                        @change="validarFechasInsumosUsados"
                      />
                      <div v-if="errorFechaInsumosUsados" class="error-message">
                        {{ errorFechaInsumosUsados }}
                      </div>
                    </div>

                    <!-- Fecha Fin -->
                    <div class="filtro-group">
                      <label for="fecha-fin-insumos">Fecha Fin</label>
                      <input
                        id="fecha-fin-insumos"
                        type="date"
                        v-model="filtrosInsumosUsados.fechaFin"
                        :min="filtrosInsumosUsados.fechaInicio || ''"
                        :max="fechaHoy"
                        :disabled="fechaFinDisabledInsumosUsados"
                        class="filtro-input"
                        @change="validarFechasInsumosUsados"
                      />
                      <div v-if="errorFechaInsumosUsados" class="error-message">
                        {{ errorFechaInsumosUsados }}
                      </div>
                    </div>

                    <!-- Proveedor -->
                    <div class="filtro-group">
                      <label for="proveedor-insumos">Proveedor</label>
                      <select
                        id="proveedor-insumos"
                        v-model="filtrosInsumosUsados.proveedorId"
                        class="filtro-select"
                      >
                        <option value="">Todos los proveedores</option>
                        <option
                          v-for="proveedor in proveedores"
                          :key="proveedor.id"
                          :value="proveedor.id"
                        >
                          {{ proveedor.nombre }}
                        </option>
                      </select>
                    </div>

                    <!-- ¿Reponer? -->
                    <div class="filtro-group">
                      <label for="reponer-insumos">¿Reponer?</label>
                      <select
                        id="reponer-insumos"
                        v-model="filtrosInsumosUsados.reponer"
                        class="filtro-select"
                      >
                        <option value="">Todos</option>
                        <option value="si">Sí</option>
                        <option value="no">No</option>
                      </select>
                    </div>

                    <!-- Buscador de insumos -->
                    <div class="filtro-group buscador">
                      <label>&nbsp;</label>
                      <form autocomplete="off" class="search-form">
                        <input
                          autocomplete="off"
                          v-model="filtrosInsumosUsados.searchTerm"
                          type="text"
                          placeholder="🔍 Buscar insumo..."
                          class="search-input"
                        />
                      </form>
                    </div>
                  </div>

                  <!-- Indicadores de Filtros Activos con Botón Limpiar -->
                  <div
                    v-if="filtrosActivosInsumosUsados"
                    class="filtros-activos-info"
                  >
                    <div class="filtros-activos-content">
                      <small>
                        Filtros activos:
                        <span
                          v-if="filtroPeriodoInsumosUsados"
                          class="filtro-activo"
                        >
                          {{ filtroPeriodoInsumosUsados }}
                        </span>
                        <span
                          v-if="filtrosInsumosUsados.proveedorId"
                          class="filtro-activo"
                        >
                          Proveedor: {{ nombreProveedorInsumosUsados }}
                        </span>
                        <span
                          v-if="filtrosInsumosUsados.reponer"
                          class="filtro-activo"
                        >
                          Reponer: {{ filtrosInsumosUsados.reponer === 'si' ? 'Sí' : 'No' }}
                        </span>
                        <span
                          v-if="filtrosInsumosUsados.searchTerm"
                          class="filtro-activo"
                        >
                          Búsqueda: "{{ filtrosInsumosUsados.searchTerm }}"
                        </span>
                      </small>
                    </div>
                    <button
                      @click="limpiarFiltrosInsumosUsados"
                      class="btn-limpiar-filtros"
                    >
                      <i class="fas fa-broom"></i>
                      Limpiar Filtros
                    </button>
                  </div>
                </div>

                <!-- Tabla de Insumos Usados -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">📊 Insumos Utilizados</h3>
                    <!-- Botón Generar PDF -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="reporteFiltrado.length > 0"
                    >
                      <button
                        @click="generarPDF"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDF"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Insumo</th>
                          <th>Stock Usado</th>
                          <th>Stock Actual</th>
                          <th>Stock Mínimo</th>
                          <th>¿Reponer?</th>
                          <th>Proveedor</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in reporteFiltrado"
                          :key="item.id"
                          :class="{
                            'reportes-fila-stock-bajo': item.necesitaReposicion,
                          }"
                        >
                          <td class="reportes-columna-insumo-nombre">
                            {{ item.nombre }}
                            <span class="reportes-categoria-insumo"
                              >({{ item.categoria }})</span
                            >
                          </td>
                          <td class="reportes-columna-stock-usado">
                            {{ formatDecimal(item.stockUsado) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-stock-actual">
                            {{ formatDecimal(item.stockActual) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-stock-minimo">
                            {{ formatDecimal(item.stockMinimo) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-reposicion">
                            <span
                              class="reportes-badge"
                              :class="
                                item.necesitaReposicion ? 'alert' : 'success'
                              "
                            >
                              {{ item.necesitaReposicion ? "SÍ" : "NO" }}
                            </span>
                          </td>
                          <td class="reportes-columna-proveedor">
                            {{ item.proveedor || "Sin proveedor" }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loading" class="reportes-loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando reporte...</p>
                    </div>
                    <div
                      v-else-if="reporteFiltrado.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-inbox"></i>
                      <p>
                        No hay insumos con stock usado en el período
                        seleccionado
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pestaña 2: Recetas Hechas -->
              <div v-show="tabActiva === 'recetas-hechas'" class="tab-pane">
                <!-- FILTROS ESPECÍFICOS - Recetas Hechas -->
                <div class="filtros-pestaña">
                  <div class="filtros-grid">
                    <!-- Fecha Inicio -->
                    <div class="filtro-group">
                      <label for="fecha-inicio-recetas">Fecha Inicio</label>
                      <input
                        id="fecha-inicio-recetas"
                        type="date"
                        v-model="filtrosRecetasHechas.fechaInicio"
                        :max="filtrosRecetasHechas.fechaFin || fechaHoy"
                        class="filtro-input"
                        @change="validarFechasRecetasHechas"
                      />
                      <div v-if="errorFechaRecetasHechas" class="error-message">
                        {{ errorFechaRecetasHechas }}
                      </div>
                    </div>

                    <!-- Fecha Fin -->
                    <div class="filtro-group">
                      <label for="fecha-fin-recetas">Fecha Fin</label>
                      <input
                        id="fecha-fin-recetas"
                        type="date"
                        v-model="filtrosRecetasHechas.fechaFin"
                        :min="filtrosRecetasHechas.fechaInicio || ''"
                        :max="fechaHoy"
                        :disabled="fechaFinDisabledRecetasHechas"
                        class="filtro-input"
                        @change="validarFechasRecetasHechas"
                      />
                      <div v-if="errorFechaRecetasHechas" class="error-message">
                        {{ errorFechaRecetasHechas }}
                      </div>
                    </div>

                    <!-- Buscador de recetas -->
                    <div class="filtro-group buscador">
                      <label>&nbsp;</label>
                      <form autocomplete="off" class="search-form">
                        <input
                          autocomplete="off"
                          v-model="filtrosRecetasHechas.searchTerm"
                          type="text"
                          placeholder="🔍 Buscar receta..."
                          class="search-input"
                        />
                      </form>
                    </div>
                  </div>

                  <!-- Indicadores de Filtros Activos con Botón Limpiar -->
                  <div
                    v-if="filtrosActivosRecetasHechas"
                    class="filtros-activos-info"
                  >
                    <div class="filtros-activos-content">
                      <small>
                        Filtros activos:
                        <span
                          v-if="filtroPeriodoRecetasHechas"
                          class="filtro-activo"
                        >
                          {{ filtroPeriodoRecetasHechas }}
                        </span>
                        <span
                          v-if="filtrosRecetasHechas.searchTerm"
                          class="filtro-activo"
                        >
                          Búsqueda: "{{ filtrosRecetasHechas.searchTerm }}"
                        </span>
                      </small>
                    </div>
                    <button
                      @click="limpiarFiltrosRecetasHechas"
                      class="btn-limpiar-filtros"
                    >
                      <i class="fas fa-broom"></i>
                      Limpiar Filtros
                    </button>
                  </div>
                </div>

                <!-- Tabla de Recetas Hechas -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">🍽️ Recetas Hechas - Historial</h3>
                    <!-- Botón Generar PDF -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="recetasHechasFiltradas.length > 0"
                    >
                      <button
                        @click="generarPDFRecetas"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDFRecetas"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Receta</th>
                          <th>Total Preparado</th>
                          <th>Costo Total</th>
                          <th>Fecha de preparación</th>
                          <th>Precio Venta</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in recetasHechasFiltradas"
                          :key="'receta-' + item.id"
                        >
                          <td class="reportes-columna-receta-nombre">
                            {{ item.nombre }}
                          </td>
                          <td class="reportes-columna-cantidad">
                            {{ item.cantidad }}
                            {{ item.cantidad === 1 ? "vez" : "veces" }}
                          </td>
                          <td class="reportes-columna-costo">
                            ${{ formatDecimal(item.costo_total) }}
                          </td>
                          <td class="reportes-columna-fecha">
                            {{ formatearFechaCorta(item.ultima_preparacion) }}
                          </td>
                          <td class="reportes-columna-precio">
                            ${{ formatDecimal(item.precio_venta) }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingRecetas" class="reportes-loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando preparaciones...</p>
                    </div>
                    <div
                      v-else-if="recetasHechasFiltradas.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-utensils"></i>
                      <p>No hay preparaciones en el período seleccionado</p>
                      <small>
                        Las preparaciones aparecerán aquí después de usar el
                        botón "Preparar"
                      </small>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pestaña 3: Pedidos -->
              <div v-show="tabActiva === 'pedidos'" class="tab-pane">
                <!-- FILTROS ESPECÍFICOS - Pedidos -->
                <div class="filtros-pestaña">
                  <div class="filtros-grid">
                    <!-- Fecha Inicio -->
                    <div class="filtro-group">
                      <label for="fecha-inicio-pedidos">Fecha Inicio</label>
                      <input
                        id="fecha-inicio-pedidos"
                        type="date"
                        v-model="filtrosPedidos.fechaInicio"
                        :max="filtrosPedidos.fechaFin || fechaHoy"
                        class="filtro-input"
                        @change="validarFechasPedidos"
                      />
                      <div v-if="errorFechaPedidos" class="error-message">
                        {{ errorFechaPedidos }}
                      </div>
                    </div>

                    <!-- Fecha Fin -->
                    <div class="filtro-group">
                      <label for="fecha-fin-pedidos">Fecha Fin</label>
                      <input
                        id="fecha-fin-pedidos"
                        type="date"
                        v-model="filtrosPedidos.fechaFin"
                        :min="filtrosPedidos.fechaInicio || ''"
                        :max="fechaHoy"
                        :disabled="fechaFinDisabledPedidos"
                        class="filtro-input"
                        @change="validarFechasPedidos"
                      />
                      <div v-if="errorFechaPedidos" class="error-message">
                        {{ errorFechaPedidos }}
                      </div>
                    </div>

                    <!-- Cliente -->
                    <div class="filtro-group">
                      <label for="cliente-pedidos">Cliente</label>
                      <select
                        id="cliente-pedidos"
                        v-model="filtrosPedidos.clienteId"
                        class="filtro-select"
                      >
                        <option value="">Todos los clientes</option>
                        <option
                          v-for="cliente in clientes"
                          :key="cliente.id"
                          :value="cliente.id"
                        >
                          {{ cliente.nombre }}
                        </option>
                      </select>
                    </div>
                  </div>

                  <!-- Indicadores de Filtros Activos con Botón Limpiar -->
                  <div
                    v-if="filtrosActivosPedidos"
                    class="filtros-activos-info"
                  >
                    <div class="filtros-activos-content">
                      <small>
                        Filtros activos:
                        <span
                          v-if="filtroPeriodoPedidos"
                          class="filtro-activo"
                        >
                          {{ filtroPeriodoPedidos }}
                        </span>
                        <span
                          v-if="filtrosPedidos.clienteId"
                          class="filtro-activo"
                        >
                          Cliente: {{ nombreClientePedidos }}
                        </span>
                      </small>
                    </div>
                    <button
                      @click="limpiarFiltrosPedidos"
                      class="btn-limpiar-filtros"
                    >
                      <i class="fas fa-broom"></i>
                      Limpiar Filtros
                    </button>
                  </div>
                </div>

                <!-- Tabla de Pedidos -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">📦 Pedidos Entregados</h3>
                    <!-- Botón Generar PDF -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="pedidosFiltrados.length > 0"
                    >
                      <button
                        @click="generarPDFPedidos"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDFPedidos"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Pedido ID</th>
                          <th>Cliente</th>
                          <th>Recetas</th>
                          <th>Fecha Entrega</th>
                          <th>Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in pedidosFiltrados"
                          :key="'pedido-' + item.id"
                          :class="{
                            'reportes-fila-pedido-urgente':
                              item.estado === 'pendiente',
                          }"
                        >
                          <td class="reportes-columna-pedido-id">
                            #{{ item.id }}
                          </td>
                          <td class="reportes-columna-cliente">
                            {{ item.cliente }}
                          </td>
                          <td class="reportes-columna-recetas">
                            <div class="recetas-pedido-detalle">
                              {{ getRecetasText(item.detalles) }}
                            </div>
                            <!-- Mostrar ingredientes extra si existen -->
                            <div
                              v-if="hasIngredientesExtra(item.detalles)"
                              class="ingredientes-extra-detalle"
                            >
                              <small>
                                <strong>Ingredientes extra:</strong>
                                {{ getIngredientesExtraText(item.detalles) }}
                              </small>
                            </div>
                          </td>
                          <td class="reportes-columna-fecha">
                            {{ formatearFechaCorta(item.fecha_entrega) }}
                          </td>
                          <td class="reportes-columna-total">
                            ${{ formatDecimal(item.total) }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingPedidos" class="reportes-loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando pedidos...</p>
                    </div>
                    <div
                      v-else-if="pedidosFiltrados.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-shopping-bag"></i>
                      <p>No hay pedidos para la fecha seleccionada</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pestaña 4: Pérdidas de Insumos -->
              <div v-show="tabActiva === 'perdidas-insumos'" class="tab-pane">
                <!-- FILTROS ESPECÍFICOS - Pérdidas de Insumos -->
                <div class="filtros-pestaña">
                  <div class="filtros-grid">
                    <!-- Fecha Inicio -->
                    <div class="filtro-group">
                      <label for="fecha-inicio-perdidas">Fecha Inicio</label>
                      <input
                        id="fecha-inicio-perdidas"
                        type="date"
                        v-model="filtrosPerdidas.fechaInicio"
                        :max="filtrosPerdidas.fechaFin || fechaHoy"
                        class="filtro-input"
                        @change="validarFechasPerdidas"
                      />
                      <div v-if="errorFechaPerdidas" class="error-message">
                        {{ errorFechaPerdidas }}
                      </div>
                    </div>

                    <!-- Fecha Fin -->
                    <div class="filtro-group">
                      <label for="fecha-fin-perdidas">Fecha Fin</label>
                      <input
                        id="fecha-fin-perdidas"
                        type="date"
                        v-model="filtrosPerdidas.fechaFin"
                        :min="filtrosPerdidas.fechaInicio || ''"
                        :max="fechaHoy"
                        :disabled="fechaFinDisabledPerdidas"
                        class="filtro-input"
                        @change="validarFechasPerdidas"
                      />
                      <div v-if="errorFechaPerdidas" class="error-message">
                        {{ errorFechaPerdidas }}
                      </div>
                    </div>

                    <!-- Categoría -->
                    <div class="filtro-group">
                      <label for="categoria-perdidas">Categoría</label>
                      <select
                        id="categoria-perdidas"
                        v-model="filtrosPerdidas.categoria"
                        class="filtro-select"
                      >
                        <option value="">Todas las categorías</option>
                        <option
                          v-for="categoria in categoriasDisponibles"
                          :key="categoria"
                          :value="categoria"
                        >
                          {{ categoria }}
                        </option>
                      </select>
                    </div>

                    <!-- Motivo -->
                    <div class="filtro-group">
                      <label for="motivo-perdidas">Motivo</label>
                      <select
                        id="motivo-perdidas"
                        v-model="filtrosPerdidas.motivo"
                        class="filtro-select"
                      >
                        <option value="">Todos los motivos</option>
                        <option value="deterioro">Deterioro</option>
                        <option value="vencimiento">Vencimiento</option>
                        <option value="rotura">Rotura</option>
                        <option value="error">Error en registro</option>
                        <option value="uso_interno">Uso interno</option>
                        <option value="otro">Otro</option>
                      </select>
                    </div>

                    <!-- Buscador de insumos -->
                    <div class="filtro-group buscador">
                      <label>&nbsp;</label>
                      <form autocomplete="off" class="search-form">
                        <input
                          autocomplete="off"
                          v-model="filtrosPerdidas.searchTerm"
                          type="text"
                          placeholder="🔍 Buscar insumo..."
                          class="search-input"
                        />
                      </form>
                    </div>
                  </div>

                  <!-- Indicadores de Filtros Activos con Botón Limpiar -->
                  <div
                    v-if="filtrosActivosPerdidas"
                    class="filtros-activos-info"
                  >
                    <div class="filtros-activos-content">
                      <small>
                        Filtros activos:
                        <span
                          v-if="filtroPeriodoPerdidas"
                          class="filtro-activo"
                        >
                          {{ filtroPeriodoPerdidas }}
                        </span>
                        <span
                          v-if="filtrosPerdidas.categoria"
                          class="filtro-activo"
                        >
                          Categoría: {{ filtrosPerdidas.categoria }}
                        </span>
                        <span
                          v-if="filtrosPerdidas.motivo"
                          class="filtro-activo"
                        >
                          Motivo: {{ formatMotivoPerdida(filtrosPerdidas.motivo) }}
                        </span>
                        <span
                          v-if="filtrosPerdidas.searchTerm"
                          class="filtro-activo"
                        >
                          Búsqueda: "{{ filtrosPerdidas.searchTerm }}"
                        </span>
                      </small>
                    </div>
                    <button
                      @click="limpiarFiltrosPerdidas"
                      class="btn-limpiar-filtros"
                    >
                      <i class="fas fa-broom"></i>
                      Limpiar Filtros
                    </button>
                  </div>
                </div>

                <!-- Tabla de Historial de Pérdidas -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">📉 Historial de Pérdidas</h3>
                    <!-- Botón Generar PDF -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="historialPerdidasFiltrado.length > 0"
                    >
                      <button
                        @click="generarPDFPerdidas"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDFPerdidas"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Fecha</th>
                          <th>Insumo</th>
                          <th>Categoría</th>
                          <th>Cantidad</th>
                          <th>Motivo</th>
                          <th>Observaciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="perdida in historialPerdidasFiltrado"
                          :key="perdida.ids.join('-')"
                        >
                          <td class="reportes-columna-fecha">
                            {{ formatearFechaCorta(perdida.fecha) }}
                          </td>
                          <td class="reportes-columna-insumo-nombre">
                            <strong>{{ perdida.insumo_nombre }}</strong>
                          </td>
                          <td class="reportes-columna-categoria">
                            {{ perdida.categoria || "-" }}
                          </td>
                          <td class="reportes-columna-stock-usado">
                            {{ formatDecimal(perdida.cantidad) }}
                            {{ perdida.unidad }}
                          </td>
                          <td class="reportes-columna-reposicion">
                            <span
                              class="reportes-badge"
                              :class="perdida.motivo"
                            >
                              {{ formatMotivoPerdida(perdida.motivo) }}
                            </span>
                          </td>
                          <td class="reportes-columna-observaciones">
                            {{ perdida.observaciones || "-" }}
                            <small
                              v-if="perdida.ids.length > 1"
                              style="
                                display: block;
                                color: #666;
                                margin-top: 4px;
                              "
                            >
                              (Agrupado de {{ perdida.ids.length }} registros)
                            </small>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="loadingPerdidas" class="reportes-loading-state">
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando historial de pérdidas...</p>
                    </div>
                    <div
                      v-else-if="historialPerdidasFiltrado.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-search"></i>
                      <p>No se encontraron registros de pérdidas</p>
                      <small
                        v-if="filtrosActivosPerdidas"
                      >
                        Intenta con otros filtros
                      </small>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pestaña 5: Lista de Compras -->
              <div v-show="tabActiva === 'lista-compras'" class="tab-pane">
                <!-- FILTROS ESPECÍFICOS - Lista de Compras -->
                <div class="filtros-pestaña">
                  <div class="filtros-grid">
                    <!-- Proveedor -->
                    <div class="filtro-group">
                      <label for="proveedor-compras">Proveedor</label>
                      <select
                        id="proveedor-compras"
                        v-model="filtrosListaCompras.proveedorId"
                        class="filtro-select"
                      >
                        <option value="">Todos los proveedores</option>
                        <option
                          v-for="proveedor in proveedores"
                          :key="proveedor.id"
                          :value="proveedor.id"
                        >
                          {{ proveedor.nombre }}
                        </option>
                      </select>
                    </div>
                  </div>

                  <!-- Indicadores de Filtros Activos con Botón Limpiar -->
                  <div
                    v-if="filtrosActivosListaCompras"
                    class="filtros-activos-info"
                  >
                    <div class="filtros-activos-content">
                      <small>
                        Filtros activos:
                        <span
                          v-if="filtrosListaCompras.proveedorId"
                          class="filtro-activo"
                        >
                          Proveedor: {{ nombreProveedorListaCompras }}
                        </span>
                      </small>
                    </div>
                    <button
                      @click="limpiarFiltrosListaCompras"
                      class="btn-limpiar-filtros"
                    >
                      <i class="fas fa-broom"></i>
                      Limpiar Filtros
                    </button>
                  </div>
                </div>

                <!-- Tabla de Lista de Compras -->
                <div class="reportes-card">
                  <div class="reportes-table-header">
                    <h3 class="card-title">
                      📋 Lista de Compras - Próxima Semana
                    </h3>
                    <!-- Botón Generar PDF -->
                    <div
                      class="reportes-seccion-pdf"
                      v-if="listaComprasFiltrada.length > 0"
                    >
                      <button
                        @click="generarPDFListaCompras"
                        class="reportes-btn-generar-pdf"
                      >
                        <i class="fas fa-file-pdf"></i>
                        Generar PDF
                      </button>

                      <div
                        v-if="generandoPDFListaCompras"
                        class="reportes-estado-generando-pdf"
                      >
                        <i class="fas fa-spinner fa-spin"></i>
                        Generando PDF...
                      </div>
                    </div>
                  </div>
                  <div class="reportes-table-scroll-container">
                    <table class="reportes-table-content">
                      <thead>
                        <tr>
                          <th>Insumo</th>
                          <th>Stock Actual</th>
                          <th>Stock Mínimo</th>
                          <th>Pedidos</th>
                          <th>Compra sugerida</th>
                          <th>Proveedor</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="item in listaComprasFiltrada"
                          :key="'compra-' + item.id"
                          :class="{
                            'reportes-fila-urgente': item.totalComprar > 0,
                          }"
                        >
                          <td class="reportes-columna-insumo-nombre">
                            {{ item.nombre }}
                            <span class="reportes-categoria-insumo"
                              >({{ item.categoria }})</span
                            >
                          </td>
                          <td class="reportes-columna-stock-actual">
                            {{ formatDecimal(item.stockActual) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-stock-minimo">
                            {{ formatDecimal(item.stockMinimo) }}
                            {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-pedidos">
                            {{ formatDecimal(item.pedidos) }} {{ item.unidad }}
                          </td>
                          <td class="reportes-columna-total-comprar">
                            <strong
                              >{{ formatDecimal(item.totalComprar) }}
                              {{ item.unidad }}</strong
                            >
                          </td>
                          <td class="reportes-columna-proveedor">
                            {{ item.proveedor || "Sin proveedor" }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                    <div
                      v-if="loadingListaCompras"
                      class="reportes-loading-state"
                    >
                      <i class="fas fa-spinner fa-spin"></i>
                      <p>Cargando lista de compras...</p>
                    </div>
                    <div
                      v-else-if="listaComprasFiltrada.length === 0"
                      class="reportes-empty-state"
                    >
                      <i class="fas fa-check-circle"></i>
                      <p>
                        No hay insumos para comprar con los filtros actuales
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";

const router = useRouter();

// Referencia al sidebar para controlarlo desde el header
const sidebarRef = ref(null);

// Estado para controlar la pestaña activa
const tabActiva = ref("insumos-usados");

// ----------------------
// 🔹 NUEVA ESTRUCTURA DE PESTAÑAS
// ----------------------
const tabs = ref([
  {
    id: "insumos-usados",
    nombre: "Insumos Usados",
    icono: "fas fa-boxes",
  },
  {
    id: "recetas-hechas",
    nombre: "Recetas Hechas",
    icono: "fas fa-utensils",
  },
  { id: "pedidos", nombre: "Pedidos", icono: "fas fa-clipboard-list" },
  {
    id: "perdidas-insumos",
    nombre: "Pérdidas de Insumos",
    icono: "fas fa-minus-circle",
  },
  {
    id: "lista-compras",
    nombre: "Lista de Compras",
    icono: "fas fa-shopping-cart",
  },
]);

// ----------------------
// 🔹 NUEVOS FILTROS POR PESTAÑA
// ----------------------
// Filtros para Insumos Usados
const filtrosInsumosUsados = ref({
  fechaInicio: "",
  fechaFin: "",
  proveedorId: "",
  reponer: "",
  searchTerm: "",
});

// Filtros para Recetas Hechas
const filtrosRecetasHechas = ref({
  fechaInicio: "",
  fechaFin: "",
  searchTerm: "",
});

// Filtros para Pedidos
const filtrosPedidos = ref({
  fechaInicio: "",
  fechaFin: "",
  clienteId: "",
});

// Filtros para Pérdidas de Insumos
const filtrosPerdidas = ref({
  fechaInicio: "",
  fechaFin: "",
  categoria: "",
  motivo: "",
  searchTerm: "",
});

// Filtros para Lista de Compras
const filtrosListaCompras = ref({
  proveedorId: "",
});

// ----------------------
// 🔹 ERRORES DE VALIDACIÓN DE FECHAS
// ----------------------
const errorFechaInsumosUsados = ref("");
const errorFechaRecetasHechas = ref("");
const errorFechaPedidos = ref("");
const errorFechaPerdidas = ref("");

// ----------------------
// 🔹 PROPIEDADES COMPUTADAS PARA DISABLED DE FECHA FIN
// ----------------------
const fechaFinDisabledInsumosUsados = computed(() => !filtrosInsumosUsados.value.fechaInicio);
const fechaFinDisabledRecetasHechas = computed(() => !filtrosRecetasHechas.value.fechaInicio);
const fechaFinDisabledPedidos = computed(() => !filtrosPedidos.value.fechaInicio);
const fechaFinDisabledPerdidas = computed(() => !filtrosPerdidas.value.fechaInicio);

// ----------------------
// 🔹 COMPUTED PROPERTIES PARA FILTROS ACTIVOS
// ----------------------
// Insumos Usados
const filtrosActivosInsumosUsados = computed(() => {
  return (
    filtrosInsumosUsados.value.fechaInicio ||
    filtrosInsumosUsados.value.fechaFin ||
    filtrosInsumosUsados.value.proveedorId ||
    filtrosInsumosUsados.value.reponer ||
    filtrosInsumosUsados.value.searchTerm
  );
});

// Insumos Usados
const filtroPeriodoInsumosUsados = computed(() => {
  if (filtrosInsumosUsados.value.fechaInicio && filtrosInsumosUsados.value.fechaFin) {
    return `Período: ${formatearFechaCorta(filtrosInsumosUsados.value.fechaInicio)} - ${formatearFechaCorta(filtrosInsumosUsados.value.fechaFin)}`;
  } else if (filtrosInsumosUsados.value.fechaInicio) {
    return `Fecha: ${formatearFechaCorta(filtrosInsumosUsados.value.fechaInicio)}`;
  }
  return "";
});

const nombreProveedorInsumosUsados = computed(() => {
  if (!filtrosInsumosUsados.value.proveedorId) return "";
  const proveedor = proveedores.value.find(p => p.id === parseInt(filtrosInsumosUsados.value.proveedorId));
  return proveedor ? proveedor.nombre : "Proveedor no encontrado";
});

// Recetas Hechas
const filtrosActivosRecetasHechas = computed(() => {
  return (
    filtrosRecetasHechas.value.fechaInicio ||
    filtrosRecetasHechas.value.fechaFin ||
    filtrosRecetasHechas.value.searchTerm
  );
});

// Recetas Hechas
const filtroPeriodoRecetasHechas = computed(() => {
  if (filtrosRecetasHechas.value.fechaInicio && filtrosRecetasHechas.value.fechaFin) {
    return `Período: ${formatearFechaCorta(filtrosRecetasHechas.value.fechaInicio)} - ${formatearFechaCorta(filtrosRecetasHechas.value.fechaFin)}`;
  } else if (filtrosRecetasHechas.value.fechaInicio) {
    return `Fecha: ${formatearFechaCorta(filtrosRecetasHechas.value.fechaInicio)}`;
  }
  return "";
});

// Pedidos
const filtrosActivosPedidos = computed(() => {
  return (
    filtrosPedidos.value.fechaInicio ||
    filtrosPedidos.value.fechaFin ||
    filtrosPedidos.value.clienteId
  );
});

// Pedidos
const filtroPeriodoPedidos = computed(() => {
  if (filtrosPedidos.value.fechaInicio && filtrosPedidos.value.fechaFin) {
    return `Período: ${formatearFechaCorta(filtrosPedidos.value.fechaInicio)} - ${formatearFechaCorta(filtrosPedidos.value.fechaFin)}`;
  } else if (filtrosPedidos.value.fechaInicio) {
    return `Fecha: ${formatearFechaCorta(filtrosPedidos.value.fechaInicio)}`;
  }
  return "";
});

const nombreClientePedidos = computed(() => {
  if (!filtrosPedidos.value.clienteId) return "";
  const cliente = clientes.value.find(c => c.id === parseInt(filtrosPedidos.value.clienteId));
  return cliente ? cliente.nombre : "Cliente no encontrado";
});

// Pérdidas de Insumos
const filtrosActivosPerdidas = computed(() => {
  return (
    filtrosPerdidas.value.fechaInicio ||
    filtrosPerdidas.value.fechaFin ||
    filtrosPerdidas.value.categoria ||
    filtrosPerdidas.value.motivo ||
    filtrosPerdidas.value.searchTerm
  );
});

// Pérdidas de Insumos
const filtroPeriodoPerdidas = computed(() => {
  if (filtrosPerdidas.value.fechaInicio && filtrosPerdidas.value.fechaFin) {
    return `Período: ${formatearFechaCorta(filtrosPerdidas.value.fechaInicio)} - ${formatearFechaCorta(filtrosPerdidas.value.fechaFin)}`;
  } else if (filtrosPerdidas.value.fechaInicio) {
    return `Fecha: ${formatearFechaCorta(filtrosPerdidas.value.fechaInicio)}`;
  }
  return "";
});

// Lista de Compras
const filtrosActivosListaCompras = computed(() => {
  return filtrosListaCompras.value.proveedorId;
});

const nombreProveedorListaCompras = computed(() => {
  if (!filtrosListaCompras.value.proveedorId) return "";
  const proveedor = proveedores.value.find(p => p.id === parseInt(filtrosListaCompras.value.proveedorId));
  return proveedor ? proveedor.nombre : "Proveedor no encontrado";
});

// ----------------------
// 🔹 MÉTODOS PARA CAMBIAR PESTAÑA
// ----------------------
const cambiarTab = (tabId) => {
  tabActiva.value = tabId;
};

const obtenerContador = (tabId) => {
  switch (tabId) {
    case "insumos-usados":
      return reporteFiltrado.value.length;
    case "recetas-hechas":
      return recetasHechasFiltradas.value.length;
    case "pedidos":
      return pedidosFiltrados.value.length;
    case "perdidas-insumos":
      return historialPerdidasFiltrado.value.length;
    case "lista-compras":
      return listaComprasFiltrada.value.length;
    default:
      return 0;
  }
};

// ----------------------
// 🔹 WATCHERS PARA AUTOCOMPLETAR FECHA FIN
// ----------------------
// Watcher para Insumos Usados
watch(() => filtrosInsumosUsados.value.fechaInicio, (nuevaFechaInicio) => {
  if (nuevaFechaInicio && !filtrosInsumosUsados.value.fechaFin) {
    // Autocompletar Fecha Fin con fecha actual
    filtrosInsumosUsados.value.fechaFin = fechaHoy.value;
    // Llamar a validación y carga de datos
    validarFechasInsumosUsados();
  } else if (!nuevaFechaInicio) {
    // Limpiar Fecha Fin si se borra Fecha Inicio
    filtrosInsumosUsados.value.fechaFin = "";
  }
});

// Watcher para Recetas Hechas
watch(() => filtrosRecetasHechas.value.fechaInicio, (nuevaFechaInicio) => {
  if (nuevaFechaInicio && !filtrosRecetasHechas.value.fechaFin) {
    // Autocompletar Fecha Fin con fecha actual
    filtrosRecetasHechas.value.fechaFin = fechaHoy.value;
    // Llamar a validación y carga de datos
    validarFechasRecetasHechas();
  } else if (!nuevaFechaInicio) {
    // Limpiar Fecha Fin si se borra Fecha Inicio
    filtrosRecetasHechas.value.fechaFin = "";
  }
});

// Watcher para Pedidos
watch(() => filtrosPedidos.value.fechaInicio, (nuevaFechaInicio) => {
  if (nuevaFechaInicio && !filtrosPedidos.value.fechaFin) {
    // Autocompletar Fecha Fin con fecha actual
    filtrosPedidos.value.fechaFin = fechaHoy.value;
    // Llamar a validación y carga de datos
    validarFechasPedidos();
  } else if (!nuevaFechaInicio) {
    // Limpiar Fecha Fin si se borra Fecha Inicio
    filtrosPedidos.value.fechaFin = "";
  }
});

// Watcher para Pérdidas
watch(() => filtrosPerdidas.value.fechaInicio, (nuevaFechaInicio) => {
  if (nuevaFechaInicio && !filtrosPerdidas.value.fechaFin) {
    // Autocompletar Fecha Fin con fecha actual
    filtrosPerdidas.value.fechaFin = fechaHoy.value;
    // Llamar a validación y carga de datos
    validarFechasPerdidas();
  } else if (!nuevaFechaInicio) {
    // Limpiar Fecha Fin si se borra Fecha Inicio
    filtrosPerdidas.value.fechaFin = "";
  }
});

// ----------------------
// 🔹 MÉTODOS DE VALIDACIÓN DE FECHAS
// ----------------------
// Validación para Insumos Usados
const validarFechasInsumosUsados = () => {
  errorFechaInsumosUsados.value = "";
  
  const fechaInicio = filtrosInsumosUsados.value.fechaInicio;
  const fechaFin = filtrosInsumosUsados.value.fechaFin;
  
  if (fechaInicio && fechaFin) {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    
    if (fin < inicio) {
      errorFechaInsumosUsados.value = "La fecha fin no puede ser anterior a la fecha inicio";
      return false;
    }
  }
  
  // Si hay fechas válidas, cargar datos
  if (fechaInicio || fechaFin) {
    fetchReportes();
  }
  
  return true;
};

// Validación para Recetas Hechas
const validarFechasRecetasHechas = () => {
  errorFechaRecetasHechas.value = "";
  
  const fechaInicio = filtrosRecetasHechas.value.fechaInicio;
  const fechaFin = filtrosRecetasHechas.value.fechaFin;
  
  if (fechaInicio && fechaFin) {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    
    if (fin < inicio) {
      errorFechaRecetasHechas.value = "La fecha fin no puede ser anterior a la fecha inicio";
      return false;
    }
  }
  
  // Si hay fechas válidas, cargar datos
  if (fechaInicio || fechaFin) {
    fetchRecetasHechas();
  }
  
  return true;
};

// Validación para Pedidos
const validarFechasPedidos = () => {
  errorFechaPedidos.value = "";
  
  const fechaInicio = filtrosPedidos.value.fechaInicio;
  const fechaFin = filtrosPedidos.value.fechaFin;
  
  if (fechaInicio && fechaFin) {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    
    if (fin < inicio) {
      errorFechaPedidos.value = "La fecha fin no puede ser anterior a la fecha inicio";
      return false;
    }
  }
  
  // Si hay fechas válidas, cargar datos
  if (fechaInicio || fechaFin) {
    fetchPedidos();
  }
  
  return true;
};

// Validación para Pérdidas
const validarFechasPerdidas = () => {
  errorFechaPerdidas.value = "";
  
  const fechaInicio = filtrosPerdidas.value.fechaInicio;
  const fechaFin = filtrosPerdidas.value.fechaFin;
  
  if (fechaInicio && fechaFin) {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    
    if (fin < inicio) {
      errorFechaPerdidas.value = "La fecha fin no puede ser anterior a la fecha inicio";
      return false;
    }
  }
  
  // Si hay fechas válidas, cargar datos
  if (fechaInicio || fechaFin) {
    fetchHistorialPerdidas();
  }
  
  return true;
};

// ----------------------
// 🔹 MÉTODOS PARA LIMPIAR FILTROS
// ----------------------
// Limpiar filtros de Insumos Usados
const limpiarFiltrosInsumosUsados = () => {
  filtrosInsumosUsados.value = {
    fechaInicio: "",
    fechaFin: "",
    proveedorId: "",
    reponer: "",
    searchTerm: "",
  };
  errorFechaInsumosUsados.value = "";
  fetchReportes();
};

// Limpiar filtros de Recetas Hechas
const limpiarFiltrosRecetasHechas = () => {
  filtrosRecetasHechas.value = {
    fechaInicio: "",
    fechaFin: "",
    searchTerm: "",
  };
  errorFechaRecetasHechas.value = "";
  fetchRecetasHechas();
};

// Limpiar filtros de Pedidos
const limpiarFiltrosPedidos = () => {
  filtrosPedidos.value = {
    fechaInicio: "",
    fechaFin: "",
    clienteId: "",
  };
  errorFechaPedidos.value = "";
  fetchPedidos();
};

// Limpiar filtros de Pérdidas
const limpiarFiltrosPerdidas = () => {
  filtrosPerdidas.value = {
    fechaInicio: "",
    fechaFin: "",
    categoria: "",
    motivo: "",
    searchTerm: "",
  };
  errorFechaPerdidas.value = "";
  fetchHistorialPerdidas();
};

// Limpiar filtros de Lista de Compras
const limpiarFiltrosListaCompras = () => {
  filtrosListaCompras.value = {
    proveedorId: "",
  };
  fetchListaCompras();
};

// ----------------------
// 🔹 MÉTODOS PARA EL SIDEBAR
// ----------------------
const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleSidebar();
  }
};

// ----------------------
// 🔹 ESTADO Y DATOS
// ----------------------
const reportes = ref([]);
const listaCompras = ref([]);
const recetasHechas = ref([]);
const pedidos = ref([]);
const proveedores = ref([]);
const clientes = ref([]);
const loading = ref(true);
const loadingListaCompras = ref(false);
const loadingRecetas = ref(false);
const loadingPedidos = ref(false);
const generandoPDF = ref(false);
const generandoPDFListaCompras = ref(false);
const generandoPDFRecetas = ref(false);
const generandoPDFPedidos = ref(false);
const generandoPDFPerdidas = ref(false);
const mostrarFiltros = ref(false);
const isMobile = ref(false);
const fechaHoy = ref(new Date().toISOString().split("T")[0]);

// Nueva variable de estado para pérdidas
const historialPerdidas = ref([]);
const loadingPerdidas = ref(false);

// ----------------------
// 🔹 COMPUTED PROPERTIES PARA FILTRADO
// ----------------------
// Insumos Usados
const reporteFiltrado = computed(() => {
  let filtered = [...reportes.value];

  // Filtrar por fechas (ya viene filtrado del backend)
  
  // Filtrar por proveedor
  if (filtrosInsumosUsados.value.proveedorId) {
    filtered = filtered.filter(
      (item) => item.proveedorId === parseInt(filtrosInsumosUsados.value.proveedorId)
    );
  }

  // Filtrar por reponer
  if (filtrosInsumosUsados.value.reponer) {
    if (filtrosInsumosUsados.value.reponer === "si") {
      filtered = filtered.filter((item) => item.necesitaReposicion);
    } else if (filtrosInsumosUsados.value.reponer === "no") {
      filtered = filtered.filter((item) => !item.necesitaReposicion);
    }
  }

  // Filtrar por término de búsqueda
  if (filtrosInsumosUsados.value.searchTerm) {
    const searchLower = filtrosInsumosUsados.value.searchTerm.toLowerCase();
    filtered = filtered.filter((item) =>
      item.nombre.toLowerCase().includes(searchLower) ||
      item.categoria.toLowerCase().includes(searchLower)
    );
  }

  // Filtrar solo insumos con stock usado > 0
  filtered = filtered.filter((item) => item.stockUsado > 0);

  return filtered;
});

// Recetas Hechas
const recetasHechasFiltradas = computed(() => {
  let filtered = [...recetasHechas.value];

  // Filtrar por término de búsqueda
  if (filtrosRecetasHechas.value.searchTerm) {
    const searchLower = filtrosRecetasHechas.value.searchTerm.toLowerCase();
    filtered = filtered.filter((item) =>
      item.nombre.toLowerCase().includes(searchLower)
    );
  }

  return filtered;
});

// Pedidos
const pedidosFiltrados = computed(() => {
  // Filtrar solo pedidos entregados en el frontend
  const pedidosEntregados = pedidos.value.filter(
    (pedido) => pedido.estado === "entregado"
  );

  // Aplicar filtro de fecha (ya viene filtrado del backend)
  let pedidosFiltrados = pedidosEntregados;

  // Filtrar por cliente
  if (filtrosPedidos.value.clienteId) {
    pedidosFiltrados = pedidosFiltrados.filter((pedido) => {
      // Suponiendo que pedido.cliente es un string con el nombre del cliente
      // Si necesitas comparar por ID, necesitarías tener el ID del cliente en los datos del pedido
      const clienteId = pedido.cliente_id || pedido.cliente?.id;
      return clienteId === parseInt(filtrosPedidos.value.clienteId);
    });
  }

  // Ordenar por fecha_entrega (del más nuevo al más viejo)
  return pedidosFiltrados.sort((a, b) => {
    const fechaA = new Date(a.fecha_entrega).getTime();
    const fechaB = new Date(b.fecha_entrega).getTime();
    return fechaB - fechaA; // Orden descendente
  });
});

// Lista de Compras
const listaComprasFiltrada = computed(() => {
  let filtered = [...listaCompras.value];

  // Filtrar por proveedor
  if (filtrosListaCompras.value.proveedorId) {
    filtered = filtered.filter(
      (item) => item.proveedorId === parseInt(filtrosListaCompras.value.proveedorId)
    );
  }

  // Mostrar solo los insumos que necesitan compra
  return filtered.filter((item) => item.totalComprar > 0);
});

// Pérdidas de Insumos
const historialPerdidasFiltrado = computed(() => {
  let filtered = [...historialPerdidas.value];

  // Aplicar filtro de categoría
  if (filtrosPerdidas.value.categoria) {
    filtered = filtered.filter(
      (perdida) => perdida.categoria === filtrosPerdidas.value.categoria
    );
  }

  // Aplicar filtro de motivo
  if (filtrosPerdidas.value.motivo) {
    filtered = filtered.filter(
      (perdida) => perdida.motivo === filtrosPerdidas.value.motivo
    );
  }

  // Filtrar por término de búsqueda
  if (filtrosPerdidas.value.searchTerm) {
    const searchLower = filtrosPerdidas.value.searchTerm.toLowerCase();
    filtered = filtered.filter((perdida) =>
      perdida.insumo_nombre.toLowerCase().includes(searchLower)
    );
  }

  // Agrupar pérdidas por nombre de insumo, fecha y motivo
  const grouped = {};
  filtered.forEach((perdida) => {
    const key = `${perdida.insumo_nombre}-${perdida.fecha}-${perdida.motivo}`;

    if (!grouped[key]) {
      grouped[key] = {
        ...perdida,
        cantidad: parseFloat(perdida.cantidad),
        ids: [perdida.id],
      };
    } else {
      grouped[key].cantidad += parseFloat(perdida.cantidad);
      grouped[key].ids.push(perdida.id);
    }
  });

  return Object.values(grouped);
});

// Obtener categorías únicas de TODAS las pérdidas
const categoriasDisponibles = computed(() => {
  const categorias = new Set();
  historialPerdidas.value.forEach((perdida) => {
    if (perdida.categoria) {
      categorias.add(perdida.categoria);
    }
  });
  return Array.from(categorias).sort();
});

// ----------------------
// 🔹 MÉTODOS DE UTILIDAD
// ----------------------
const formatDecimal = (value) => {
  if (!value) return "0";
  // Eliminar ceros decimales innecesarios
  const num = parseFloat(value);
  return num % 1 === 0 ? num.toString() : num.toFixed(3).replace(/\.?0+$/, "");
};

const formatearFechaCorta = (fecha) => {
  if (!fecha) return "";

  try {
    if (typeof fecha === "string" && /^\d{4}-\d{2}-\d{2}$/.test(fecha)) {
      const [year, month, day] = fecha.split("-");
      return `${day}/${month}/${year}`;
    }

    const fechaObj = new Date(fecha);
    if (isNaN(fechaObj.getTime())) {
      return "Fecha inválida";
    }

    const day = String(fechaObj.getDate()).padStart(2, '0');
    const month = String(fechaObj.getMonth() + 1).padStart(2, '0');
    const year = fechaObj.getFullYear();
    
    return `${day}/${month}/${year}`;
  } catch (error) {
    console.error("Error formateando fecha corta:", error, fecha);
    return "Fecha inválida";
  }
};

const formatMotivoPerdida = (motivo) => {
  const motivos = {
    deterioro: "Deterioro",
    vencimiento: "Vencimiento",
    rotura: "Rotura",
    error: "Error en registro",
    uso_interno: "Uso interno",
    otro: "Otro",
  };
  return motivos[motivo] || motivo;
};

const getRecetasText = (detalles) => {
  if (!detalles || detalles.length === 0) {
    return "Sin recetas";
  }

  return detalles
    .map((detalle) => {
      const recetaNombre = detalle.receta?.nombre || "Receta no disponible";
      const cantidad = detalle.cantidad || 1;
      return `${recetaNombre} (x${cantidad})`;
    })
    .join(", ");
};

const hasIngredientesExtra = (detalles) => {
  if (!detalles) return false;
  return detalles.some(
    (detalle) =>
      detalle.ingredientes_extra && detalle.ingredientes_extra.length > 0
  );
};

const getIngredientesExtraText = (detalles) => {
  if (!detalles) return "";

  const ingredientesExtra = [];
  detalles.forEach((detalle) => {
    if (detalle.ingredientes_extra && detalle.ingredientes_extra.length > 0) {
      detalle.ingredientes_extra.forEach((ing) => {
        const insumoNombre = ing.insumo?.nombre || "Insumo no disponible";
        const cantidad = ing.cantidad || 0;
        const unidad = ing.unidad_medida?.abreviatura || "u";
        ingredientesExtra.push(`${insumoNombre}: ${cantidad} ${unidad}`);
      });
    }
  });

  return ingredientesExtra.join(", ");
};

// ----------------------
// 🔹 MÉTODOS PARA GENERAR PDFs
// ----------------------
const generarPDF = async () => {
  try {
    generandoPDF.value = true;

    // Construir parámetros de filtro para el PDF
    const params = {
      solo_con_stock_usado: true,
    };
    
    // Usar las fechas de los filtros específicos
    if (filtrosInsumosUsados.value.fechaInicio) {
      params.fecha_inicio = filtrosInsumosUsados.value.fechaInicio;
    }
    if (filtrosInsumosUsados.value.fechaFin) {
      params.fecha_fin = filtrosInsumosUsados.value.fechaFin;
    }
    if (filtrosInsumosUsados.value.proveedorId) {
      params.proveedor_id = filtrosInsumosUsados.value.proveedorId;
    }

    console.log("📄 Parámetros enviados para PDF Insumos Usados:", params);

    // Hacer la petición para generar el PDF
    const response = await axios.get("/api/reportes/generar-pdf/", {
      params: params,
      responseType: "blob",
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `reporte_insumos_usados_${new Date().toISOString().split("T")[0]}.pdf`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDF.value = false;
  }
};

const generarPDFListaCompras = async () => {
  try {
    generandoPDFListaCompras.value = true;

    // Construir parámetros de filtro para el PDF
    const params = {};
    if (filtrosListaCompras.value.proveedorId) {
      params.proveedor_id = filtrosListaCompras.value.proveedorId;
    }

    // Hacer la petición para generar el PDF de lista de compras
    const response = await axios.get(
      "/api/reportes/generar-pdf-lista-compras/",
      {
        params: params,
        responseType: "blob",
      }
    );

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute(
      "download",
      `lista_compras_${new Date().toISOString().split("T")[0]}.pdf`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF de lista de compras:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDFListaCompras.value = false;
  }
};

const generarPDFRecetas = async () => {
  try {
    generandoPDFRecetas.value = true;

    const params = {};
    if (filtrosRecetasHechas.value.fechaInicio) {
      params.fecha_inicio = filtrosRecetasHechas.value.fechaInicio;
    }
    if (filtrosRecetasHechas.value.fechaFin) {
      params.fecha_fin = filtrosRecetasHechas.value.fechaFin;
    }

    const response = await axios.get("/api/recetas-por-fecha/pdf/", {
      params: params,
      responseType: "blob",
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    // Nombre del archivo basado en las fechas de filtro
    let fileName = "recetas_hechas";
    if (filtrosRecetasHechas.value.fechaInicio && filtrosRecetasHechas.value.fechaFin) {
      fileName = `recetas_${filtrosRecetasHechas.value.fechaInicio}_a_${filtrosRecetasHechas.value.fechaFin}`;
    } else {
      fileName = `recetas_${new Date().toISOString().split("T")[0]}`;
    }

    link.setAttribute("download", `${fileName}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF de recetas:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDFRecetas.value = false;
  }
};

const generarPDFPedidos = async () => {
  try {
    generandoPDFPedidos.value = true;

    const response = await axios.get("/api/pedidos/entregados/pdf/", {
      params: {
        fecha_inicio: filtrosPedidos.value.fechaInicio,
        fecha_fin: filtrosPedidos.value.fechaFin,
      },
      responseType: "blob",
    });

    // Crear un enlace temporal para descargar el PDF
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    // Nombre del archivo basado en las fechas de filtro
    let fileName = "pedidos_entregados";
    if (filtrosPedidos.value.fechaInicio && filtrosPedidos.value.fechaFin) {
      fileName = `pedidos_${filtrosPedidos.value.fechaInicio}_a_${filtrosPedidos.value.fechaFin}`;
    } else {
      fileName = `pedidos_entregados_${new Date().toISOString().split("T")[0]}`;
    }

    link.setAttribute("download", `${fileName}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF de pedidos:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDFPedidos.value = false;
  }
};

const generarPDFPerdidas = async () => {
  try {
    generandoPDFPerdidas.value = true;

    const params = {};
    if (filtrosPerdidas.value.fechaInicio) {
      params.fecha_inicio = filtrosPerdidas.value.fechaInicio;
    }
    if (filtrosPerdidas.value.fechaFin) {
      params.fecha_fin = filtrosPerdidas.value.fechaFin;
    }
    if (filtrosPerdidas.value.motivo) {
      params.motivo = filtrosPerdidas.value.motivo;
    }

    const response = await axios.get("/api/perdidas/generar-pdf/", {
      params: params,
      responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    let fileName = "historial_perdidas";
    if (filtrosPerdidas.value.fechaInicio && filtrosPerdidas.value.fechaFin) {
      fileName = `perdidas_${filtrosPerdidas.value.fechaInicio}_a_${filtrosPerdidas.value.fechaFin}`;
    } else {
      fileName = `perdidas_${new Date().toISOString().split("T")[0]}`;
    }

    link.setAttribute("download", `${fileName}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al generar PDF de pérdidas:", error);
    alert("Error al generar el PDF. Por favor, intente nuevamente.");
  } finally {
    generandoPDFPerdidas.value = false;
  }
};

// ----------------------
// 🔹 FETCH DATOS
// ----------------------
const fetchReportes = async () => {
  try {
    loading.value = true;

    const params = {};
    if (filtrosInsumosUsados.value.fechaInicio) {
      params.fecha_inicio = filtrosInsumosUsados.value.fechaInicio;
    }
    if (filtrosInsumosUsados.value.fechaFin) {
      params.fecha_fin = filtrosInsumosUsados.value.fechaFin;
    }
    if (filtrosInsumosUsados.value.proveedorId) {
      params.proveedor_id = filtrosInsumosUsados.value.proveedorId;
    }

    const response = await axios.get("/api/reportes/insumos/", { params });

    // ✅ VERIFICAR que la respuesta tenga datos
    if (!response.data) {
      throw new Error("No se recibieron datos del servidor");
    }

    reportes.value = response.data.map((item) => ({
      id: item.id,
      nombre: item.nombre,
      categoria: item.categoria,
      stockUsado: item.stock_usado || 0,
      stockActual: item.stock_actual,
      stockMinimo: item.stock_minimo,
      unidad: item.unidad_medida?.abreviatura || "u",
      necesitaReposicion: item.necesita_reposicion,
      proveedor: item.proveedor?.nombre || "Sin proveedor",
      proveedorId: item.proveedor?.id || null,
    }));
  } catch (error) {
    console.error("Error al cargar reportes:", error);
    reportes.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchListaCompras = async () => {
  try {
    loadingListaCompras.value = true;

    const params = {};
    if (filtrosListaCompras.value.proveedorId) {
      params.proveedor_id = filtrosListaCompras.value.proveedorId;
    }

    const response = await axios.get("/api/reportes/lista-compras/", {
      params,
    });

    if (!response.data) {
      throw new Error(
        "No se recibieron datos del servidor para lista de compras"
      );
    }

    listaCompras.value = response.data.map((item) => ({
      id: item.id,
      nombre: item.nombre,
      categoria: item.categoria,
      stockActual: item.stock_actual,
      stockMinimo: item.stock_minimo,
      pedidos: item.pedidos || 0,
      totalComprar: item.total_comprar || 0,
      unidad: item.unidad_medida?.abreviatura || "u",
      proveedor: item.proveedor?.nombre || "Sin proveedor",
      proveedorId: item.proveedor?.id || null,
    }));
  } catch (error) {
    console.error("Error al cargar lista de compras:", error);
    listaCompras.value = [];
  } finally {
    loadingListaCompras.value = false;
  }
};

const fetchRecetasHechas = async () => {
  try {
    loadingRecetas.value = true;

    const params = {};
    if (filtrosRecetasHechas.value.fechaInicio) {
      params.fecha_inicio = filtrosRecetasHechas.value.fechaInicio;
    }
    if (filtrosRecetasHechas.value.fechaFin) {
      params.fecha_fin = filtrosRecetasHechas.value.fechaFin;
    }

    console.log(
      "📊 Haciendo petición a /api/recetas-por-fecha/ con params:",
      params
    );

    const response = await axios.get("/api/recetas-por-fecha/", {
      params: params,
    });

    console.log("📊 Respuesta recibida:", response.data);

    if (!response.data) {
      throw new Error(
        "No se recibieron datos del servidor para recetas hechas"
      );
    }

    // Si el backend devuelve un error, mostrarlo
    if (response.data.error) {
      console.error("Error del backend:", response.data.error);
      recetasHechas.value = [];
      return;
    }

    recetasHechas.value = response.data.recetas.map((item) => ({
      id: item.id,
      nombre: item.nombre,
      cantidad: item.cantidad,
      rinde: item.rinde,
      unidad_rinde: item.unidad_rinde,
      costo_total: item.costo_total,
      precio_venta: item.precio_venta,
      veces_hecha_hoy: item.veces_hecha_hoy,
      ultima_preparacion: item.ultima_preparacion,
    }));

    console.log("📊 Datos procesados:", recetasHechas.value);
  } catch (error) {
    console.error("Error al cargar preparaciones:", error);
    recetasHechas.value = [];
  } finally {
    loadingRecetas.value = false;
  }
};

const fetchPedidos = async () => {
  try {
    loadingPedidos.value = true;

    // Obtener todos los pedidos (no solo los entregados, para poder filtrar en frontend)
    const response = await axios.get("/api/pedidos/", {
      params: {
        fecha_inicio: filtrosPedidos.value.fechaInicio,
        fecha_fin: filtrosPedidos.value.fechaFin,
      },
    });

    if (!response.data) {
      throw new Error("No se recibieron datos del servidor para pedidos");
    }

    console.log("Datos de pedidos recibidos:", response.data);

    pedidos.value = response.data.map((item) => ({
      id: item.id,
      cliente: item.cliente?.nombre || "Cliente no disponible",
      cliente_id: item.cliente?.id || null,
      total: item.total || 0,
      fecha_entrega: item.fecha_entrega,
      fecha_pedido: item.fecha_pedido,
      detalles: item.detalles || [],
      estado: item.estado || "pendiente",
    }));
  } catch (error) {
    console.error("Error al cargar pedidos:", error);
    pedidos.value = [];
  } finally {
    loadingPedidos.value = false;
  }
};

const fetchHistorialPerdidas = async () => {
  try {
    loadingPerdidas.value = true;

    const params = new URLSearchParams();
    if (filtrosPerdidas.value.fechaInicio) {
      params.append("fecha_inicio", filtrosPerdidas.value.fechaInicio);
    }
    if (filtrosPerdidas.value.fechaFin) {
      params.append("fecha_fin", filtrosPerdidas.value.fechaFin);
    }

    console.log("🔍 Fetching TODAS las pérdidas...");
    const response = await axios.get(`/api/perdidas/?${params.toString()}`);
    console.log("📊 Todas las pérdidas recibidas:", response.data);
    historialPerdidas.value = response.data;
  } catch (error) {
    console.error("Error al cargar historial de pérdidas:", error);
  } finally {
    loadingPerdidas.value = false;
  }
};

const fetchProveedores = async () => {
  try {
    const response = await axios.get("/api/proveedores/");
    proveedores.value = response.data;
  } catch (error) {
    console.error("Error al cargar proveedores:", error);
  }
};

const fetchClientes = async () => {
  try {
    const response = await axios.get("/api/clientes/");
    clientes.value = response.data;
  } catch (error) {
    console.error("Error al cargar clientes:", error);
  }
};

// Detectar cambios de tamaño de pantalla
onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile);
});

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768;
};

// ----------------------
// 🔹 MONTAR COMPONENTE
// ----------------------
onMounted(() => {
  if (!localStorage.getItem("access_token")) {
    router.push("/login");
    return;
  }

  Promise.all([
    fetchReportes(),
    fetchListaCompras(),
    fetchRecetasHechas(),
    fetchPedidos(),
    fetchHistorialPerdidas(),
    fetchProveedores(),
    fetchClientes(),
  ]).catch((error) => {
    console.error("Error cargando datos:", error);
    if (error.response?.status === 401) {
      router.push("/login");
    }
  });
});

// ----------------------
// 🔹 WATCHERS
// ----------------------
// Watchers para los filtros de búsqueda
watch(
  () => filtrosInsumosUsados.value.searchTerm,
  () => {
    // El filtrado se hace en el computed property
  }
);

watch(
  () => filtrosRecetasHechas.value.searchTerm,
  () => {
    // El filtrado se hace en el computed property
  }
);

watch(
  () => filtrosPerdidas.value.searchTerm,
  () => {
    // El filtrado se hace en el computed property
  }
);

// Watchers para los filtros de select
watch(
  () => filtrosInsumosUsados.value.proveedorId,
  () => {
    // El filtrado se hace en el computed property
  }
);

watch(
  () => filtrosInsumosUsados.value.reponer,
  () => {
    // El filtrado se hace en el computed property
  }
);

watch(
  () => filtrosPedidos.value.clienteId,
  () => {
    // El filtrado se hace en el computed property
  }
);

watch(
  () => filtrosPerdidas.value.categoria,
  () => {
    // El filtrado se hace en el computed property
  }
);

watch(
  () => filtrosPerdidas.value.motivo,
  () => {
    // El filtrado se hace en el computed property
  }
);

watch(
  () => filtrosListaCompras.value.proveedorId,
  () => {
    // El filtrado se hace en el computed property
  }
);

// Watcher para cambiar de pestaña
watch(tabActiva, (newTab) => {
  // Solo cargar datos si no están cargados
  if (newTab === "perdidas-insumos" && historialPerdidas.value.length === 0) {
    fetchHistorialPerdidas();
  }
});
</script>

<style scoped>
/* -------------------- PESTAÑAS -------------------- */
.tabs-container {
  margin-top: 20px;
  width: 100%;
}

.tabs-header {
  display: flex;
  background: white;
  border-radius: 10px 10px 0 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
}

.tab-button {
  flex: 1;
  min-width: 200px;
  background: #f8f9fa;
  border: none;
  padding: 15px 20px;
  font-size: 1rem;
  font-weight: 600;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background: #e9ecef;
  color: var(--color-primary);
}

.tab-button.active {
  background: white;
  color: var(--color-primary);
  border-bottom: 3px solid var(--color-primary);
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.05);
}

.tabs-content {
  background: white;
  border-radius: 0 0 10px 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 20px;
  min-height: 400px;
}

.tab-pane {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Badge para contador en pestañas */
.tab-button .badge-contador {
  background-color: var(--color-primary);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin-left: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* -------------------- FILTROS POR PESTAÑA -------------------- */
.filtros-pestaña {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filtros-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  align-items: end;
}

.filtro-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filtro-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 2px;
}

.filtro-input,
.filtro-select {
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  height: 42px;
  transition: all 0.3s ease;
  background: white;
  width: 100%;
}

.filtro-input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
  opacity: 0.6;
}

.filtro-input:focus,
.filtro-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(123, 90, 80, 0.1);
  transform: translateY(-1px);
}

/* Estilo para el buscador (estilo Principal.vue) */
.filtro-group.buscador {
  grid-column: 1 / -1;
}

.search-form {
  width: 100%;
}

.search-input {
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 14px;
  width: 100%;
  transition: all 0.3s ease;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(123, 90, 80, 0.1);
  transform: translateY(-1px);
}

.search-input::placeholder {
  color: #6c757d;
  opacity: 0.7;
}

/* MODIFICACIÓN ÚNICA: Contenedor unificado para filtros activos y botón limpiar */
.filtros-activos-info {
  margin-top: 15px;
  padding: 10px 15px;
  background: #e9ecef;
  border-radius: 6px;
  border-left: 4px solid var(--color-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filtros-activos-content {
  flex: 1;
  min-width: 0;
}

.filtro-activo {
  display: inline-block;
  background: var(--color-primary);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  margin: 0 5px;
  font-size: 0.8rem;
  white-space: nowrap;
}

/* Botón Limpiar Filtros - Integrado en la misma línea */
.btn-limpiar-filtros {
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 14px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-limpiar-filtros:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-limpiar-filtros:active {
  transform: translateY(0);
}

/* Mensajes de error */
.error-message {
  color: #dc3545;
  font-size: 0.75rem;
  margin-top: 2px;
  min-height: 16px;
}

/* -------------------- TABLA DE REPORTES -------------------- */
.reportes-card {
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: var(--color-background);
  border-radius: 10px;
  box-shadow: 10px 8px 10px #aaa;
  padding: 8px;
  padding-top: 2px;
  overflow-y: auto;
}

.reportes-table-header {
  flex-shrink: 0;
  padding: 15px;
  border-bottom: 1px solid #eee;
  background: var(--color-background);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* CONTENEDOR DE SCROLL PRINCIPAL */
.reportes-table-scroll-container {
  flex: 1;
  overflow: auto;
  position: relative;
  min-height: 400px;
  max-height: 600px;
  height: auto;
}

/* TABLA PRINCIPAL */
.reportes-table-content {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  background: white;
  margin: 0;
  position: relative;
}

/* THEAD STICKY */
.reportes-table-content thead {
  position: sticky;
  top: 0;
  z-index: 100;
}

.reportes-table-content th {
  background: linear-gradient(135deg, var(--color-primary), #6d4c41);
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  color: white;
  border-bottom: 2px solid #5a3f36;
  position: sticky;
  top: 0;
  z-index: 101;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.reportes-table-content td {
  padding: 10px 8px;
  border-bottom: 1px solid #eee;
  text-align: left;
  background: white;
}

.reportes-table-content tr:hover td {
  background-color: rgba(123, 90, 80, 0.05);
}

/* Centrar las columnas específicas */
.reportes-table-content th:nth-child(2),
.reportes-table-content th:nth-child(3),
.reportes-table-content th:nth-child(4),
.reportes-table-content th:nth-child(5),
.reportes-table-content td:nth-child(2),
.reportes-table-content td:nth-child(3),
.reportes-table-content td:nth-child(4),
.reportes-table-content td:nth-child(5) {
  text-align: center;
}

/* Filas con stock bajo */
.reportes-fila-stock-bajo td {
  background-color: rgba(220, 53, 69, 0.05);
  border-left: 3px solid var(--color-danger);
}

.reportes-fila-stock-bajo:hover td {
  background-color: rgba(220, 53, 69, 0.1);
}

/* Filas urgentes en lista de compras */
.reportes-fila-urgente td {
  background-color: rgba(40, 167, 69, 0.05);
  border-left: 3px solid var(--color-success);
}

.reportes-fila-urgente:hover td {
  background-color: rgba(40, 167, 69, 0.1);
}

/* Filas urgentes en pedidos */
.reportes-fila-pedido-urgente td {
  background-color: rgba(255, 193, 7, 0.05);
  border-left: 3px solid var(--color-warning);
}

.reportes-fila-pedido-urgente:hover td {
  background-color: rgba(255, 193, 7, 0.1);
}

/* Columnas específicas */
.reportes-columna-insumo-nombre,
.reportes-columna-receta-nombre {
  font-weight: 500;
  color: var(--color-text);
}

.reportes-categoria-insumo {
  font-size: 0.8rem;
  color: #666;
  font-style: italic;
}

.reportes-columna-stock-usado,
.reportes-columna-stock-actual,
.reportes-columna-stock-minimo,
.reportes-columna-pedidos,
.reportes-columna-cantidad,
.reportes-columna-total {
  font-family: monospace;
  font-weight: 500;
}

.reportes-columna-total-comprar {
  font-family: monospace;
  font-weight: 600;
  color: var(--color-success);
  text-align: center;
}

.reportes-columna-reposicion,
.reportes-columna-estado {
  text-align: center;
}

.reportes-columna-proveedor,
.reportes-columna-empleado,
.reportes-columna-cliente {
  color: #555;
}

.reportes-columna-fecha,
.reportes-columna-hora {
  text-align: center;
}

/* Estilos para los detalles de recetas en reportes */
.recetas-pedido-detalle {
  max-width: 300px;
  line-height: 1.4;
  font-size: 0.85rem;
  margin-bottom: 4px;
}

.ingredientes-extra-detalle {
  background: #f8f9fa;
  padding: 6px 8px;
  border-radius: 4px;
  border-left: 3px solid var(--color-primary);
  font-size: 0.75rem;
  color: #666;
  margin-top: 4px;
}

.ingredientes-extra-detalle strong {
  color: var(--color-primary);
}

.reportes-columna-recetas {
  max-width: 350px;
  word-wrap: break-word;
}

/* -------------------- BOTÓN PDF -------------------- */
.reportes-btn-generar-pdf {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.reportes-btn-generar-pdf:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.4);
}

.reportes-btn-generar-pdf:active {
  transform: translateY(0);
}

.reportes-estado-generando-pdf {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary);
  font-weight: 500;
}

/* -------------------- LOADING -------------------- */
.reportes-loading-state {
  text-align: center;
  padding: 3rem;
  color: var(--color-primary);
  width: 100%;
}

.reportes-loading-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

/* -------------------- ESTADO VACÍO -------------------- */
.reportes-empty-state {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
  margin: 1rem;
  width: 100%;
}

.reportes-empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.reportes-empty-state p {
  margin: 0;
  font-size: 1.1rem;
}

/* -------------------- Badges específicos para reportes -------------------- */
.reportes-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}

.reportes-badge.alert {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.reportes-badge.success {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.reportes-badge.warning {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

.reportes-badge.info {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.reportes-badge.default {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
}

/* Estilos para los badges de motivos de pérdida */
.reportes-badge.deterioro {
  background: #fff3cd;
  color: #856404;
}

.reportes-badge.vencimiento {
  background: #f8d7da;
  color: #721c24;
}

.reportes-badge.rotura {
  background: #e2e3e5;
  color: #383d41;
}

.reportes-badge.error {
  background: #d1ecf1;
  color: #0c5460;
}

.reportes-badge.uso_interno {
  background: #d4edda;
  color: #155724;
}

.reportes-badge.otro {
  background: #e2e3e5;
  color: #383d41;
}

.reportes-columna-observaciones {
  max-width: 250px;
  word-wrap: break-word;
}

/* -------------------- TÍTULO ESPECÍFICO PARA REPORTES -------------------- */
.reportes-card-title1 {
  color: var(--color-primary);
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 2px 4px rgba(123, 90, 80, 0.1);
}

.main-content-repo {
  flex: 1;
  padding: 15px;
  padding-top: 0%;
  padding-left: 135px;
  position: relative;
  z-index: 1;
  transition: margin-left 0.3s ease;
}

/* -------------------- MEJORAS RESPONSIVE -------------------- */
@media (max-width: 768px) {
  .tabs-header {
    flex-direction: column;
  }

  .main-content-repo {
    margin-left: 0;
    padding: 70px 10px 10px 10px;
    padding-top: 0%;
  }

  .tab-button {
    min-width: unset;
    border-radius: 0;
    border-bottom: 1px solid #dee2e6;
  }

  .tab-button.active {
    border-bottom: 3px solid var(--color-primary);
  }

  .filtros-grid {
    grid-template-columns: 1fr;
  }

  .filtros-activos-info {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .btn-limpiar-filtros {
    align-self: flex-end;
  }

  .reportes-seccion-pdf {
    flex-direction: column;
    gap: 10px;
  }

  .reportes-btn-generar-pdf {
    width: 100%;
    justify-content: center;
  }

  /* Ajustes para tabla en móvil */
  .reportes-table-scroll-container {
    max-height: 60vh;
  }

  .reportes-table-content {
    font-size: 0.8rem;
  }

  .reportes-table-content th,
  .reportes-table-content td {
    padding: 8px 4px;
  }

  .reportes-categoria-insumo {
    display: block;
    font-size: 0.7rem;
  }

  .reportes-table-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}

/* Scrollbar personalizado */
.reportes-table-scroll-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.reportes-table-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.reportes-table-scroll-container::-webkit-scrollbar-thumb {
  background: var(--color-primary);
  border-radius: 4px;
}

.reportes-table-scroll-container::-webkit-scrollbar-thumb:hover {
  background: #6d4c41;
}
</style>