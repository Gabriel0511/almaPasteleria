import { createRouter, createWebHistory } from "vue-router";
import InicioSesion from "./components/InicioSesion.vue";
import Principal from "./components/Principal.vue";
import Stock  from "./components/Stock.vue";

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
    name: "Principal", // Nombre de la ruta que coincide con tu redirección
    component: Principal,
    meta: { requiresAuth: true }, // Protege esta ruta
  },
  {
    path: "/stock",
    name: "Stock", // Nombre de la ruta que coincide con tu redirección
    component: Stock,
    meta: { requiresAuth: true }, // Protege esta ruta
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
