import { createRouter, createWebHistory } from "vue-router";
import InicioSesion from "./components/InicioSesion.vue";
import Principal from "./components/Principal.vue";
import Stock from "./components/Stock.vue";
import Pedidos from "./components/Pedidos.vue";
import Recetas from "./components/Recetas.vue";
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
    meta: { requiresAuth: false, title: "Iniciar Sesión" },
  },
  {
    path: "/inicio",
    name: "Principal",
    component: Principal,
    meta: { requiresAuth: true, title: "Página Principal" },
  },
  {
    path: "/stock",
    name: "Stock",
    component: Stock,
    meta: { requiresAuth: true, title: "Stock Insumos" },
  },
  {
    path: "/pedidos",
    name: "Pedidos",
    component: Pedidos,
    meta: { requiresAuth: true, title: "Pedidos" },
  },
  {
    path: "/recetas",
    name: "Recetas",
    component: Recetas,
    meta: { requiresAuth: true, title: "Recetas" },
  },
  {
    path: "/reportes",
    name: "Reportes",
    component: Reportes,
    meta: { requiresAuth: true, title: "Reportes" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Guardia de navegación
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("access_token");

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: "Login" });
  } else if (to.name === "Login" && isAuthenticated) {
    next({ name: "Principal" });
  } else {
    next();
  }

  // ✅ También actualizamos el título de la pestaña del navegador
  if (to.meta.title) {
    document.title = to.meta.title + " | Pastelería";
  }
});

export default router;
