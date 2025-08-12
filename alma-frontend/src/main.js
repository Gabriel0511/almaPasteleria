// src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import "./style.css";
import router from "./router"; // Importamos el router
import axios from "axios";
// En tu archivo de configuración de Axios
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        const response = await axios.post("/api/auth/token/refresh/", {
          refresh: refreshToken,
        });

        localStorage.setItem("access_token", response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Si el refresh falla, redirigir a login
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
axios.defaults.baseURL = "http://localhost:8000/";
const app = createApp(App);
app.use(router); // Lo registramos
app.mount("#app");
