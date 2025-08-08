// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import './style.css';
import router from './router'; // Importamos el router

const app = createApp(App);
app.use(router); // Lo registramos
app.mount('#app');
