// src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import "./assets/styles/global.css"; // ✅ Importar estilos globales
import router from "./router"; // Importamos el router
import axios from "axios";

axios.interceptors.request.use(
  (config) => {
    // Evita añadir el token a rutas públicas como login/refresh
    const publicUrls = ["/api/auth/login/", "/api/auth/token/refresh/"];
    if (publicUrls.some((url) => config.url.includes(url))) {
      return config;
    }

    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) throw new Error("No refresh token");

        const response = await axios.post("/api/auth/token/refresh/", {
          refresh: refreshToken,
        });

        localStorage.setItem("access_token", response.data.access);
        axios.defaults.headers.common[
          "Authorization"
        ] = `Bearer ${response.data.access}`;
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return axios(originalRequest);
      } catch (refreshError) {
        console.error("Error refreshing token:", refreshError);
        // Limpiar y redirigir
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        delete axios.defaults.headers.common["Authorization"];

        // Redirigir a login solo si no estamos ya en la página de login
        if (router.currentRoute.value.path !== "/login") {
          router.push("/login");
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
axios.defaults.baseURL = "http://localhost:8000/";
// En main.js, después de configurar axios.defaults.baseURL
const token = localStorage.getItem("access_token");
if (token) {
  axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}
const app = createApp(App);
app.use(router); // Lo registramos
app.mount("#app");
