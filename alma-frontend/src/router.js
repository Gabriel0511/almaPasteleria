// src/router.js
import { createRouter, createWebHistory } from 'vue-router';
import InicioSesion from './components/InicioSesion.vue';
import Principal from './components/Principal.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: InicioSesion },
  { path: '/dashboard', component: Principal },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
