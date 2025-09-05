<template>
  <Sidebar @navigate="handleNavigation" />
  <div>Hola muuy buenas a todos gapisimos</div>
  <div class="card stock">
    <div class="stock-header-container">
      <h3 class="card-title">
        Stock
        <span v-if="insumosBajoStock > 0" class="badge">
          (Hay {{ insumosBajoStock }} insumos con bajo stock)
        </span>
      </h3>

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
    </div>

    <!-- Tabla estilo Figma -->
    <div class="stock-table-container">
      <table class="stock-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Categoría</th>
            <th>Cantidad</th>
            <th>Unidad</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in stockFiltrado"
            :key="item.nombre"
            :class="{ 'low-stock': item.bajoStock }"
          >
            <td>{{ item.nombre }}</td>
            <td>{{ item.categoria }}</td>
            <td>{{ formatDecimal(item.cantidad) }}</td>
            <td>{{ item.unidad }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Acciones -->
    <div class="stock-actions">
      <button class="btn-success">Nueva Compra</button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import Sidebar from "./Sidebar.vue"; // Ajusta la ruta según tu estructura

const router = useRouter();

const handleNavigation = (route) => {
  router.push(route);
};
</script>
