<template>
  <aside class="sidebar">
    <button
      v-for="item in menuItems"
      :key="item.text"
      @click="$emit('navigate', item.route)"
      :class="{ active: isActive(item.route) }"
    >
      <i :class="item.icon"></i>
      <span>{{ item.text }}</span>
    </button>
    <div class="footer-icon">
      <i class="fas fa-clipboard-check"></i>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

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

defineEmits(["navigate"]);
</script>

<style scoped>
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
</style>
