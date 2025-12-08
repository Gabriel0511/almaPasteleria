<!-- components/PageHeader.vue -->
<template>
  <section class="principal-content">
    <!-- Título de la página -->
    <h3 class="card-title1" :class="{ 'mobile-center': isMobile }">
      {{ title }}
      <span v-if="showTotal" class="total-counter-small">
        ({{ total }} Total)
      </span>
    </h3>

    <!-- Contenedor para estadísticas y filtros -->
    <div class="filtros-estadisticas-container">
      <!-- Estadísticas (badges) -->
      <div v-if="stats && stats.length > 0" class="estadisticas-stock">
        <div
          v-for="(stat, index) in stats"
          :key="index"
          class="estadistica-item"
        >
          <span
            class="estadistica-badge"
            :class="[stat.type || 'total', { active: isStatActive(stat) }]"
            @click="handleStatClick(stat)"
            :title="stat.tooltip || stat.label"
          >
            <i :class="stat.icon"></i>
            <span class="badge-text">{{ formatStatLabel(stat) }}</span>
          </span>
        </div>

        <!-- Botón para limpiar filtros -->
        <div
          v-if="showClearButton && hasActiveFilters"
          class="estadistica-item"
        >
          <span
            class="estadistica-badge limpiar-filtro"
            @click="handleClearFilters"
          >
            <i class="fas fa-times"></i>
            <span class="badge-text">Limpiar</span>
          </span>
        </div>
      </div>

      <!-- Filtros (inputs/selects) -->
      <div v-if="filters && filters.length > 0" class="filtros-derecha">
        <div
          v-for="(filter, index) in filters"
          :key="index"
          class="filtro-group"
        >
          <!-- Input de texto -->
          <input
            v-if="filter.type === 'text'"
            :type="filter.inputType || 'text'"
            :placeholder="filter.placeholder"
            :value="filter.value"
            @input="handleFilterChange(filter, $event)"
            class="filtro-input"
            :autocomplete="filter.autocomplete || 'off'"
          />

          <!-- Select dropdown -->
          <select
            v-else-if="filter.type === 'select'"
            :value="filter.value"
            @change="handleFilterChange(filter, $event)"
            class="filtro-select"
          >
            <option value="">
              {{ filter.defaultOption || "Seleccionar..." }}
            </option>
            <option
              v-for="option in filter.options"
              :key="option.value || option"
              :value="option.value || option"
            >
              {{ option.label || option }}
            </option>
          </select>

          <!-- Input de fecha -->
          <input
            v-else-if="filter.type === 'date'"
            type="date"
            :value="filter.value"
            @input="handleFilterChange(filter, $event)"
            class="filtro-input"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  showTotal: {
    type: Boolean,
    default: false,
  },
  total: {
    type: [Number, String],
    default: 0,
  },
  stats: {
    type: Array,
    default: () => [],
  },
  filters: {
    type: Array,
    default: () => [],
  },
  showClearButton: {
    type: Boolean,
    default: true,
  },
  activeFilterType: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["stat-click", "filter-change", "clear-filters"]);

// Responsive
const isMobile = ref(false);
const isTablet = ref(false);

const checkViewport = () => {
  isMobile.value = window.innerWidth <= 767;
  isTablet.value = window.innerWidth >= 768 && window.innerWidth <= 1024;
};

const handleStatClick = (stat) => {
  emit("stat-click", stat);
};

const handleFilterChange = (filter, event) => {
  let value;
  if (filter.type === "checkbox") {
    value = event.target.checked;
  } else {
    value = event.target.value;
  }
  emit("filter-change", { filter, value });
};

const handleClearFilters = () => {
  emit("clear-filters");
};

const hasActiveFilters = computed(() => {
  return (
    props.activeFilterType ||
    props.filters.some((f) => {
      if (f.type === "checkbox") {
        return f.checked;
      }
      return f.value && f.value !== "";
    })
  );
});

const isStatActive = (stat) => {
  return props.activeFilterType === stat.type;
};

const formatStatLabel = (stat) => {
  if (stat.format === "compact" && isMobile.value) {
    return stat.compactLabel || stat.label;
  }
  return stat.label;
};

onMounted(() => {
  checkViewport();
  window.addEventListener("resize", checkViewport);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkViewport);
});
</script>

<style scoped>
/* Importar estilos globales */
@import "../assets/styles/global.css";

/* ==============================
   ESTILOS BASE PAGEHEADER
   ============================== */
.principal-content {
  display: flex;
  flex-direction: column;
  margin-bottom: 25px;
  width: 100%;
}

.card-title1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title1.mobile-center {
  justify-content: center;
  text-align: center;
}

.total-counter-small {
  font-size: 0.7em;
  color: var(--color-primary);
  font-weight: 600;
  background: rgba(108, 117, 125, 0.1);
  padding: 4px 8px;
  border-radius: 8px;
}

.filtros-estadisticas-container {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 20px;
  width: 100%;
}

/* Estadísticas */
.estadisticas-stock {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  flex: 1;
}

.estadistica-item {
  display: flex;
}

.estadistica-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  user-select: none;
  white-space: nowrap;
}

.estadistica-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.estadistica-badge.active {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

/* Tipos de badges */
.estadistica-badge.critico {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
}

.estadistica-badge.bajo {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #212529;
}

.estadistica-badge.normal {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.estadistica-badge.total {
  background: linear-gradient(135deg, var(--color-primary), #9c7a6d);
  color: white;
}

.estadistica-badge.limpiar-filtro {
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
}

.estadistica-badge.limpiar-filtro:hover {
  background: linear-gradient(135deg, #138496, #117a8b);
}

.badge-text {
  margin-left: 4px;
}

/* Filtros */
.filtros-derecha {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
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
  min-width: 250px;
}

.filtro-input:focus,
.filtro-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(123, 90, 80, 0.1);
  transform: translateY(-1px);
}

/* ==============================
   RESPONSIVE COMPLETO
   ============================== */

/* Desktop grande (≥ 1200px) */
@media (min-width: 1200px) {
  .filtros-estadisticas-container {
    flex-wrap: nowrap;
  }

  .estadisticas-stock {
    flex-wrap: nowrap;
  }
}

/* Desktop (1025px - 1199px) */
@media (min-width: 1025px) and (max-width: 1199px) {
  .filtros-estadisticas-container {
    flex-wrap: wrap;
    gap: 15px;
  }

  .filtros-derecha {
    width: 100%;
    justify-content: flex-end;
  }
}

/* Tablet landscape (768px - 1024px) */
@media (min-width: 768px) and (max-width: 1024px) {
  .principal-content {
    align-items: center;
    text-align: center;
  }

  .card-title1 {
    width: 100%;
    text-align: center;
    justify-content: center;
    margin-bottom: 15px;
  }

  .filtros-estadisticas-container {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .estadisticas-stock {
    justify-content: center;
    order: 1;
  }

  .filtros-derecha {
    width: 100%;
    justify-content: center;
    order: 2;
    flex-wrap: wrap;
    gap: 10px;
  }

  .filtro-group {
    flex: 1;
    min-width: 200px;
  }

  .filtro-input,
  .filtro-select {
    min-width: 0;
    width: 100%;
  }
}

/* Mobile (≤ 767px) */
@media (max-width: 767px) {
  .principal-content {
    align-items: center;
    text-align: center;
    margin-bottom: 20px;
    gap: 12px;
  }

  .card-title1 {
    width: 100%;
    text-align: center;
    justify-content: center;
    margin-bottom: 0;
    font-size: 1.3rem;
    flex-direction: column;
    gap: 8px;
  }

  .total-counter-small {
    margin-top: 4px;
  }

  .filtros-estadisticas-container {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    width: 100%;
  }

  .estadisticas-stock {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    order: 1;
  }

  .estadistica-item {
    width: auto;
  }

  .estadistica-badge {
    padding: 6px 10px;
    font-size: 0.75rem;
    gap: 4px;
  }

  .badge-text {
    font-size: 0.7rem;
    margin-left: 3px;
  }

  /* Botón limpiar - tamaño específico */
  .estadistica-badge.limpiar-filtro {
    padding: 6px 10px;
    font-size: 0.75rem;
  }

  .filtros-derecha {
    width: 100%;
    flex-direction: column;
    gap: 10px;
    order: 2;
  }

  .filtro-group {
    width: 100%;
  }

  .filtro-input,
  .filtro-select {
    width: 100%;
    min-width: 0;
    padding: 10px 12px;
    font-size: 16px; /* Para evitar zoom en iOS */
    height: 44px;
  }

  /* Asegurar que los selects se vean bien en mobile */
  .filtro-select {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 12px center;
    background-size: 16px;
    padding-right: 40px;
  }
}

/* Mobile pequeño (≤ 480px) */
@media (max-width: 480px) {
  .card-title1 {
    font-size: 1.2rem;
  }

  .estadistica-badge {
    padding: 5px 8px;
    font-size: 0.7rem;
  }

  .badge-text {
    display: inline;
  }

  .estadistica-badge.limpiar-filtro {
    padding: 5px 8px;
    font-size: 0.7rem;
  }

  .filtro-input,
  .filtro-select {
    padding: 8px 10px;
    height: 40px;
  }

  .principal-content {
    gap: 10px;
    margin-bottom: 15px;
  }
}

/* Mobile muy pequeño (≤ 360px) */
@media (max-width: 360px) {
  .estadisticas-stock {
    gap: 6px;
  }

  .estadistica-badge {
    padding: 4px 6px;
    font-size: 0.65rem;
  }

  .badge-text {
    display: none; /* Solo iconos en pantallas muy pequeñas */
  }

  .estadistica-badge.limpiar-filtro .badge-text {
    display: none;
  }

  .estadistica-badge i {
    font-size: 0.8rem;
    margin-right: 0;
  }

  .card-title1 {
    font-size: 1.1rem;
  }

  .total-counter-small {
    font-size: 0.6rem;
    padding: 3px 6px;
  }
}

/* Para dispositivos táctiles */
@media (hover: none) and (pointer: coarse) {
  .estadistica-badge {
    padding: 10px 12px;
    min-height: 40px;
  }

  .filtro-input,
  .filtro-select {
    font-size: 16px;
    min-height: 44px;
  }

  @media (max-width: 767px) {
    .estadistica-badge {
      padding: 8px 10px;
      min-height: 36px;
    }
  }
}

/* Asegurar que el botón limpiar siempre tenga buen contraste */
.estadistica-badge.limpiar-filtro {
  border: 2px solid transparent;
}

.estadistica-badge.limpiar-filtro:hover,
.estadistica-badge.limpiar-filtro:active {
  border-color: rgba(255, 255, 255, 0.3);
}

/* Estado activo para botón limpiar */
.estadistica-badge.limpiar-filtro.active {
  border-color: rgba(255, 255, 255, 0.5);
  background: linear-gradient(135deg, #138496, #0c5259);
}
</style>
