<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">Iniciar Sesión</h1>

      <img
        src="/src/Logo Pasteleria.jpg"
        alt="Logo de Alma Pastelería"
        class="login-logo"
      />

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="email">Correo Electrónico</label>
          <input
            type="email"
            id="email"
            v-model="email"
            required
            placeholder="tu@email.com"
            class="form-input"
          />
        </div>

        <div class="form-group password-group">
          <label for="password">Contraseña</label>
          <div class="password-input-container">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              required
              placeholder=""
              class="form-input password-input"
            />
            <button
              type="button"
              class="toggle-password"
              @click="togglePasswordVisibility"
              :aria-label="
                showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'
              "
            >
              <span class="eye-icon">{{ showPassword ? "🙈" : "👁️" }}</span>
            </button>
          </div>
        </div>

        <button type="submit" class="login-button">Ingresar</button>
      </form>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const email = ref("");
const password = ref("");
const router = useRouter();
const errorMessage = ref("");
const showPassword = ref(false);

const handleSubmit = async () => {
  try {
    const response = await axios.post("/api/auth/login/", {
      email: email.value,
      password: password.value,
    });

    localStorage.setItem("access_token", response.data.access);
    localStorage.setItem("refresh_token", response.data.refresh);
    axios.defaults.headers.common[
      "Authorization"
    ] = `Bearer ${response.data.access}`;
    router.push("/inicio");
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail || "Credenciales incorrectas";
  }
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};
</script>

<style scoped>
/* Reset y base */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #8d6e69;
  padding: 1rem;
}

.login-card {
  background-color: #f4cdcd;
  padding: 2rem;
  border-radius: 25px;
  width: 100%;
  max-width: 420px;
  text-align: center;
  border: 1px solid #000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-title {
  font-size: clamp(1.8rem, 5vw, 2.2rem);
  color: #000;
  margin-bottom: 1rem;
  font-weight: 500;
}

.login-logo {
  width: clamp(120px, 30vw, 160px);
  height: clamp(120px, 30vw, 160px);
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
  align-items: flex-start;
  font-weight: 500;
  color: #000;
  width: 100%;
  max-width: 320px;
}

.form-group label {
  margin-bottom: 0.4rem;
  font-size: clamp(1rem, 3vw, 1.2rem);
}

.form-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #000;
  border-radius: 10px;
  background-color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #7f615c;
  box-shadow: 0 0 0 2px rgba(127, 97, 92, 0.2);
}

/* Password input styles */
.password-group {
  position: relative;
}

.password-input-container {
  position: relative;
  width: 100%;
}

.password-input {
  padding-right: 45px;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
  min-width: 30px;
  min-height: 30px;
}

.toggle-password:hover {
  background-color: #f0f0f0;
}

.eye-icon {
  font-size: 1.2rem;
  display: block;
}

.login-button {
  background-color: #7f615c;
  color: white;
  padding: 0.9rem;
  border: none;
  border-radius: 20px;
  font-size: clamp(1rem, 3vw, 1.1rem);
  font-weight: 500;
  cursor: pointer;
  margin-top: 1rem;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 320px;
}

.login-button:hover {
  background-color: #6b524e;
  transform: translateY(-1px);
}

.error-message {
  color: red;
  margin-top: 1rem;
  font-size: clamp(0.9rem, 2.5vw, 1rem);
}

/* Media Queries para responsividad */
@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
    border-radius: 20px;
  }

  .form-group {
    max-width: 280px;
  }

  .login-button {
    max-width: 280px;
  }
}

@media (max-width: 360px) {
  .login-card {
    padding: 1rem;
  }

  .form-input {
    padding: 0.7rem;
    font-size: 0.9rem;
  }

  .toggle-password {
    right: 8px;
    min-width: 25px;
    min-height: 25px;
  }

  .eye-icon {
    font-size: 1rem;
  }
}

@media (max-height: 600px) and (orientation: landscape) {
  .login-container {
    padding: 0.5rem;
  }

  .login-card {
    padding: 1rem;
    margin: 0.5rem 0;
  }

  .login-logo {
    width: 80px;
    height: 80px;
    margin-bottom: 1rem;
  }

  .login-form {
    gap: 0.8rem;
  }
}

/* Mejoras de accesibilidad */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
