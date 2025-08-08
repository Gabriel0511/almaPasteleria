// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import './style.css';
import router from './router'; // Importamos el router
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:8000/api';
const app = createApp(App);
app.use(router); // Lo registramos
app.mount('#app');
