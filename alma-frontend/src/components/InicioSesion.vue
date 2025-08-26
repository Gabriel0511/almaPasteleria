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
      <a href="#" class="forgot-password" @click.prevent="toggleRecoveryModal">
        ¿Olvidaste la contraseña?
      </a>
    </div>
  </div>

  <!-- Modal de recuperación -->
  <div
    v-if="showRecoveryModal"
    class="modal-overlay"
    @click="closeModalOnOutsideClick"
  >
    <div class="modal-content" @click.stop>
      <button
        class="modal-close"
        @click="toggleRecoveryModal"
        aria-label="Cerrar modal"
      >
        ×
      </button>

      <h3 class="modal-title">Recuperar Contraseña</h3>

      <div v-if="!codeSent" class="modal-step">
        <input
          v-model="recoveryEmail"
          type="email"
          placeholder="Tu email"
          class="modal-input"
        />
        <input
          v-model="whatsappNumber"
          type="tel"
          placeholder="Número de celular (sin 0 ni 15)"
          class="modal-input"
        />
        <button @click="sendWhatsAppCode" class="modal-button">
          Enviar Código
        </button>
      </div>

      <div v-else-if="!verifiedCode" class="modal-step">
        <p class="modal-text">
          Ingresa el código de 6 dígitos enviado por WhatsApp
        </p>
        <input
          v-model="recoveryCode"
          maxlength="6"
          class="modal-input code-input"
          placeholder="000000"
        />
        <button @click="verifyCode" class="modal-button">Verificar</button>
      </div>

      <div v-else class="modal-step">
        <div class="password-input-container">
          <input
            :type="showNewPassword ? 'text' : 'password'"
            v-model="newPassword"
            placeholder="Nueva contraseña"
            class="modal-input modal-password-input"
          />
          <button
            type="button"
            class="toggle-password"
            @click="toggleNewPasswordVisibility"
            :aria-label="
              showNewPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'
            "
          >
            <span class="eye-icon">{{ showNewPassword ? "🙈" : "👁️" }}</span>
          </button>
        </div>
        <button @click="resetPassword" class="modal-button">
          Cambiar Contraseña
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const email = ref("");
const password = ref("");
const router = useRouter();
const errorMessage = ref("");
const showRecoveryModal = ref(false);
const showPassword = ref(false);
const showNewPassword = ref(false);

// Variables para recuperación
const recoveryEmail = ref("");
const whatsappNumber = ref("");
const recoveryCode = ref("");
const newPassword = ref("");
const codeSent = ref(false);
const verifiedCode = ref(false);

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
    router.push("/dashboard");
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail || "Credenciales incorrectas";
  }
};

// Función para mostrar/ocultar contraseña principal
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};

// Función para mostrar/ocultar nueva contraseña en modal
const toggleNewPasswordVisibility = () => {
  showNewPassword.value = !showNewPassword.value;
};

// Función para mostrar el modal
const toggleRecoveryModal = () => {
  showRecoveryModal.value = !showRecoveryModal.value;
  if (!showRecoveryModal.value) {
    resetForm();
  }
};

// Función para cerrar el modal al hacer clic fuera
const closeModalOnOutsideClick = (event) => {
  if (event.target.classList.contains("modal-overlay")) {
    toggleRecoveryModal();
  }
};

// Cerrar con tecla ESC
const handleKeydown = (event) => {
  if (event.key === "Escape" && showRecoveryModal.value) {
    toggleRecoveryModal();
  }
};

const sendWhatsAppCode = async () => {
  if (!recoveryEmail.value || !whatsappNumber.value) {
    errorMessage.value = "Por favor completa todos los campos";
    return;
  }

  try {
    const response = await axios.post("/api/auth/password-reset/", {
      email: recoveryEmail.value,
      phone: whatsappNumber.value,
    });
    codeSent.value = true;
    errorMessage.value = "";
    console.log("En desarrollo:", response.data.whatsapp_url);
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error || "Error al enviar código";
  }
};

const verifyCode = async () => {
  if (!recoveryCode.value || recoveryCode.value.length !== 6) {
    errorMessage.value = "Por favor ingresa un código válido de 6 dígitos";
    return;
  }

  try {
    await axios.post("/api/auth/verify-reset-code/", {
      email: recoveryEmail.value,
      code: recoveryCode.value,
    });
    verifiedCode.value = true;
    errorMessage.value = "";
  } catch (error) {
    errorMessage.value = error.response?.data?.error || "Código inválido";
  }
};

const resetPassword = async () => {
  try {
    const response = await axios.post("/api/auth/reset-password/", {
      email: recoveryEmail.value,
      new_password: newPassword.value,
      token: recoveryCode.value,
    });

    alert("Contraseña cambiada con éxito");
    toggleRecoveryModal();
  } catch (error) {
    console.error("Error completo:", error);
    errorMessage.value =
      error.response?.data?.error ||
      error.response?.data?.detail ||
      "Error al cambiar contraseña";
  }
};

const resetForm = () => {
  recoveryEmail.value = "";
  whatsappNumber.value = "";
  recoveryCode.value = "";
  newPassword.value = "";
  codeSent.value = false;
  verifiedCode.value = false;
  errorMessage.value = "";
};

// Agregar y remover event listeners
onMounted(() => {
  document.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener("keydown", handleKeydown);
});
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

.forgot-password {
  margin-top: 1.3rem;
  color: #000;
  font-size: clamp(0.9rem, 2.5vw, 1rem);
  text-decoration: none;
  display: block;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #7f615c;
  text-decoration: underline;
}

.error-message {
  color: red;
  margin-top: 1rem;
  font-size: clamp(0.9rem, 2.5vw, 1rem);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 10px;
  width: 100%;
  max-width: 400px;
  position: relative;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.modal-close:hover {
  background-color: #f0f0f0;
}

.modal-title {
  font-size: clamp(1.2rem, 4vw, 1.5rem);
  margin-bottom: 1.5rem;
  text-align: center;
  color: #000;
}

.modal-step {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.modal-input:focus {
  outline: none;
  border-color: #7f615c;
  box-shadow: 0 0 0 2px rgba(127, 97, 92, 0.2);
}

.code-input {
  text-align: center;
  letter-spacing: 0.5rem;
  font-size: 1.2rem;
}

.modal-text {
  text-align: center;
  color: #666;
  font-size: clamp(0.9rem, 2.5vw, 1rem);
}

.modal-button {
  background-color: #7b5a50;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  width: 100%;
}

.modal-button:hover {
  background-color: #6b524e;
  transform: translateY(-1px);
}

.modal-password-input {
  padding-right: 45px;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Media Queries para responsividad */
@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
    border-radius: 20px;
  }

  .modal-content {
    padding: 1.5rem;
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

  .modal-content {
    padding: 1rem;
  }

  .form-input,
  .modal-input {
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
