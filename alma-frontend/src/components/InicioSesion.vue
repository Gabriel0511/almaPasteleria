<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">Iniciar Sesión</h1>

      <img src="/public/Logo Pasteleria.jpg" alt="Logo de Alma Pastelería" class="login-logo" />

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="username">Usuario</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder=""
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder=""
            class="form-input"
          />
        </div>

        <button type="submit" class="login-button">Ingresar</button>
      </form>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <a href="#" class="forgot-password">¿Olvidaste la contraseña?</a>
    </div>
  </div>
</template>
<script setup>
import { ref } from "vue";
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref("");
const password = ref("");
const router = useRouter();
const errorMessage = ref("");

const handleSubmit = async () => {
  try {
    const response = await axios.post('http://localhost:8000/api/auth/login/', {
      username: username.value,
      password: password.value
    });

    // Guardar tokens en localStorage o en una store (como Pinia)
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);

    // Redirigir al dashboard o página principal
    router.push('/');
  } catch (error) {
    if (error.response) {
      // El servidor respondió con un código de estado fuera del rango 2xx
      errorMessage.value = error.response.data.detail || "Credenciales incorrectas";
    } else {
      errorMessage.value = "Error de conexión con el servidor";
    }
  }
};
</script>
<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #8d6e69;
}

.login-card {
  background-color: #f4cdcd;
  padding: 2rem;
  border-radius: 25px;
  width: 100%;
  max-width: 420px; /* Más ancho */
  text-align: center;
  border: 1px solid #000;
}

.login-title {
  font-size: 2.2rem;
  color: #000;
  margin-bottom: 1rem;
  font-weight: 500;
}

.login-logo {
  width: 160px;
  height: 160px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 1.5rem;
  border: 3px solid #f4cdcd;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  align-items: center;
}

.form-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Alineado a la izquierda */
  font-weight: 500;
  color: #000;
  width: 90%;
}

.form-group label {
  margin-bottom: 0.4rem;
  font-size: 1.2rem; /* Más grande */
}

.form-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #000;
  border-radius: 10px;
  background-color: white;
  font-size: 1.05rem;
}

.login-button {
  background-color: #7f615c;
  color: white;
  padding: 0.9rem;
  border: none;
  border-radius: 20px;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.3s;
  width: 90%;
}

.login-button:hover {
  background-color: #6b524e;
}

.forgot-password {
  margin-top: 1.3rem;
  color: #000;
  font-size: 1rem;
  text-decoration: none;
  display: block;
}

.error-message {
  color: red;
  margin-top: 1rem;
}

</style>
