import { createRouter, createWebHistory } from "vue-router";
import InicioSesion from "./components/InicioSesion.vue";
import Principal from "./components/Principal.vue";
import Stock from "./components/Stock.vue";
import Pedidos from "./components/Pedidos.vue";
import Recetas from "./components/Recetas.vue"; // ✅ Agregar esta importación
import Reportes from "./components/Reportes.vue";

const routes = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: InicioSesion,
    meta: { requiresAuth: false },
  },
  {
    path: "/inicio",
    name: "Principal",
    component: Principal,
    meta: { requiresAuth: true },
  },
  {
    path: "/stock",
    name: "Stock",
    component: Stock,
    meta: { requiresAuth: true },
  },
  {
    path: "/pedidos",
    name: "Pedidos",
    component: Pedidos,
    meta: { requiresAuth: true },
  },
  {
    path: "/recetas",
    name: "Recetas",
    component: Recetas, // ✅ Ahora el componente está importado
    meta: { requiresAuth: true },
  },
  {
    path: "/reportes",
    name: "Reportes",
    component: Reportes,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Guardia de navegación
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("access_token");

  // Si la ruta requiere autenticación y no hay token
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "Login" });
  }
  // Si el usuario está autenticado pero intenta ir al login
  else if (to.name === "Login" && isAuthenticated) {
    next({ name: "Principal" });
  } else {
    next();
  }
});

export default router;
