<template>
  <div>
    <!-- Overlay para cerrar el sidebar al hacer click fuera -->
    <div
      v-if="isMobile && sidebarOpen"
      class="sidebar-overlay"
      @click="closeSidebar"
    ></div>

    <!-- Sidebar -->
    <aside
      class="sidebar"
      :class="{ 
        'sidebar-open': sidebarOpen, 
        'sidebar-mobile': isMobile,
        'sidebar-hidden': isMobile && !sidebarOpen
      }"
    >
      <button
        v-for="item in menuItems"
        :key="item.text"
        @click="navigate(item.route)"
        :class="{ active: isActive(item.route) }"
      >
        <i :class="item.icon"></i>
        <span>{{ item.text }}</span>
      </button>
      <div class="footer-icon">
        <i class="fas fa-clipboard-check"></i>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const sidebarOpen = ref(false);
const isMobile = ref(false);

// Exponer métodos para que el padre pueda controlar el sidebar
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value;
};

const openSidebar = () => {
  sidebarOpen.value = true;
};

const closeSidebar = () => {
  sidebarOpen.value = false;
};

const menuItems = ref([
  { text: "Inicio", icon: "fas fa-house", route: "/inicio" },
  { text: "Stock", icon: "fas fa-box", route: "/stock" },
  { text: "Pedidos", icon: "fas fa-clipboard-list", route: "/pedidos" },
  { text: "Recetas", icon: "fas fa-book", route: "/recetas" },
  { text: "Reportes", icon: "fas fa-chart-line", route: "/reportes" },
]);

const isActive = (menuRoute) => {
  return route.path === menuRoute;
};

const checkScreenSize = () => {
  isMobile.value = window.innerWidth <= 768;
  // En desktop, el sidebar siempre está abierto
  if (!isMobile.value) {
    sidebarOpen.value = true;
  } else {
    sidebarOpen.value = false;
  }
};

const navigate = (routePath) => {
  router.push(routePath);
  if (isMobile.value) {
    closeSidebar();
  }
};

onMounted(() => {
  checkScreenSize();
  window.addEventListener("resize", checkScreenSize);
});

onUnmounted(() => {
  window.removeEventListener("resize", checkScreenSize);
});

// Exponer métodos al componente padre
defineExpose({
  toggleSidebar,
  openSidebar,
  closeSidebar
});

defineEmits(["navigate"]);
</script>

<style scoped>
/* Elimina el botón hamburguesa del sidebar ya que estará en el header */
.hamburger-btn {
  display: none;
}

/* Overlay para móviles */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* Sidebar base - Siempre visible en desktop */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 120px;
  background-color: #7b5a50;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 10px;
  z-index: 1000;
  transition: transform 0.3s ease;
}

/* Sidebar para móviles */
.sidebar-mobile {
  width: 200px;
  transform: translateX(-100%);
}

.sidebar-mobile.sidebar-open {
  transform: translateX(0);
}

/* Clase para ocultar completamente en móviles cuando está cerrado */
.sidebar-hidden {
  display: none;
}

.sidebar button {
  background: none;
  border: none;
  color: #fff;
  margin: 15px 0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 14px;
  width: 100%;
  padding: 10px;
  transition: background-color 0.3s;
}

.sidebar button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar button.active {
  background-color: rgba(255, 255, 255, 0.2);
  border-right: 3px solid white;
}

.sidebar button i {
  font-size: 20px;
  margin-bottom: 5px;
}

.footer-icon {
  margin-top: auto;
  margin-bottom: 10px;
  color: white;
  font-size: 22px;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {
  .sidebar:not(.sidebar-mobile) {
    display: none;
  }
}

@media (min-width: 769px) {
  .sidebar-overlay {
    display: none;
  }

  .sidebar-mobile {
    width: 120px;
    transform: translateX(0);
  }
}
</style>