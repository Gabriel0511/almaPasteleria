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

  <!-- Modal de recuperación actualizado -->
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

      <div v-if="recoveryStep === 'request'" class="modal-step">
        <p class="modal-text">
          Ingresa tu email y te enviaremos un código de recuperación.
        </p>
        <input
          v-model="recoveryEmail"
          type="email"
          placeholder="Tu email"
          class="modal-input"
          :disabled="isSendingCode"
        />
        <button
          @click="sendResetCode"
          class="modal-button"
          :disabled="isSendingCode"
        >
          <span v-if="isSendingCode">Enviando...</span>
          <span v-else>Enviar Código</span>
        </button>
        <p v-if="cooldown > 0" class="cooldown-text">
          ⏳ Espera {{ cooldown }} segundos para solicitar otro código
        </p>
      </div>

      <div v-else-if="recoveryStep === 'verify'" class="modal-step">
        <p class="modal-text">
          Ingresa el código de 8 dígitos que recibiste por email.
          <br /><small>Revisa también tu carpeta de spam.</small>
        </p>
        <input
          v-model="recoveryCode"
          maxlength="8"
          class="modal-input code-input"
          placeholder="XXXXXX"
          :disabled="isVerifying"
          @input="formatCode"
        />
        <p v-if="remainingAttempts !== null" class="attempts-text">
          Intentos restantes: {{ remainingAttempts }}
        </p>
        <button
          @click="verifyCode"
          class="modal-button"
          :disabled="isVerifying"
        >
          <span v-if="isVerifying">Verificando...</span>
          <span v-else>Verificar Código</span>
        </button>
        <button
          @click="recoveryStep = 'request'"
          class="modal-button secondary"
        >
          Solicitar nuevo código
        </button>
      </div>

      <div v-else-if="recoveryStep === 'reset'" class="modal-step">
        <p class="modal-text">
          Crea tu nueva contraseña (mínimo 8 caracteres).
        </p>
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
          >
            <span class="eye-icon">{{ showNewPassword ? "🙈" : "👁️" }}</span>
          </button>
        </div>

        <div class="password-strength" v-if="newPassword">
          <div class="strength-bar" :class="passwordStrengthClass"></div>
          <p class="strength-text">Fortaleza: {{ passwordStrengthText }}</p>
        </div>

        <button
          @click="resetPassword"
          class="modal-button"
          :disabled="isResetting"
        >
          <span v-if="isResetting">Cambiando...</span>
          <span v-else>Cambiar Contraseña</span>
        </button>
      </div>

      <div
        v-else-if="recoveryStep === 'success'"
        class="modal-step success-step"
      >
        <div class="success-icon">✅</div>
        <h4 class="success-title">¡Contraseña Cambiada!</h4>
        <p class="success-text">
          Tu contraseña ha sido actualizada exitosamente.
          <br />Ya puedes iniciar sesión con tu nueva contraseña.
        </p>
        <button @click="toggleRecoveryModal" class="modal-button">
          Cerrar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const email = ref("");
const password = ref("");
const router = useRouter();
const errorMessage = ref("");
const showRecoveryModal = ref(false);
const showPassword = ref(false);
const showNewPassword = ref(false);

// Variables específicas para recuperación por email
const recoveryEmail = ref("");
const recoveryCode = ref("");
const newPassword = ref("");
const recoveryStep = ref("request"); // 'request', 'verify', 'reset', 'success'
const isSendingCode = ref(false);
const isVerifying = ref(false);
const isResetting = ref(false);
const cooldown = ref(0);
const remainingAttempts = ref(null);
const verificationToken = ref("");

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
    resetRecoveryForm();
  }
};

const resetRecoveryForm = () => {
  recoveryEmail.value = "";
  recoveryCode.value = "";
  newPassword.value = "";
  verificationToken.value = "";
  recoveryStep.value = "request";
  isSendingCode.value = false;
  isVerifying.value = false;
  isResetting.value = false;
  cooldown.value = 0;
  remainingAttempts.value = null;
  errorMessage.value = "";
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

// Métodos
formatCode = () => {
  // Convertir a mayúsculas
  recoveryCode.value = recoveryCode.value.toUpperCase();

  // Limitar a 6 caracteres (cambiar de 8 a 6)
  if (recoveryCode.value.length > 6) {
    recoveryCode.value = recoveryCode.value.substring(0, 6);
  }
};

const sendResetCode = async () => {
  if (!recoveryEmail.value) {
    errorMessage.value = "Por favor ingresa tu email";
    return;
  }

  isSendingCode.value = true;
  errorMessage.value = "";

  try {
    const response = await axios.post("/api/auth/password-reset/", {
      email: recoveryEmail.value,
    });

    recoveryStep.value = "verify";
    remainingAttempts.value = 3;

    // Si hay cooldown, iniciar contador
    if (response.data.cooldown) {
      cooldown.value = response.data.cooldown;
      const timer = setInterval(() => {
        cooldown.value--;
        if (cooldown.value <= 0) {
          clearInterval(timer);
        }
      }, 1000);
    }

    alert("Código enviado. Revisa tu email (y spam).");
  } catch (error) {
    if (error.response?.status === 429) {
      errorMessage.value = error.response.data.error;
      cooldown.value = 60;
    } else {
      errorMessage.value =
        error.response?.data?.error || "Error al enviar código";
    }
  } finally {
    isSendingCode.value = false;
  }
};

const verifyCode = async () => {
  if (!recoveryCode.value || recoveryCode.value.length !== 6) {
    errorMessage.value = "Por favor ingresa un código válido de 6 dígitos";
    return;
  }

  isVerifying.value = true;
  errorMessage.value = "";

  try {
    const response = await axios.post("/api/auth/verify-reset-code/", {
      email: recoveryEmail.value,
      code: recoveryCode.value,
    });

    verificationToken.value = response.data.token;
    recoveryStep.value = "reset";
    remainingAttempts.value = null;
  } catch (error) {
    if (error.response?.data?.remaining_attempts !== undefined) {
      remainingAttempts.value = error.response.data.remaining_attempts;
    }
    errorMessage.value = error.response?.data?.error || "Código inválido";
  } finally {
    isVerifying.value = false;
  }
};

const resetPassword = async () => {
  if (!newPassword.value || newPassword.value.length < 8) {
    errorMessage.value = "La contraseña debe tener al menos 8 caracteres";
    return;
  }

  isResetting.value = true;
  errorMessage.value = "";

  try {
    const response = await axios.post("/api/auth/reset-password/", {
      email: recoveryEmail.value,
      token: verificationToken.value,
      new_password: newPassword.value,
    });

    recoveryStep.value = "success";
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error || "Error al cambiar contraseña";
  } finally {
    isResetting.value = false;
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

// Computed para fortaleza de contraseña
const passwordStrength = computed(() => {
  const pass = newPassword.value;
  if (!pass) return 0;

  let strength = 0;
  if (pass.length >= 8) strength += 1;
  if (/[A-Z]/.test(pass)) strength += 1;
  if (/[0-9]/.test(pass)) strength += 1;
  if (/[^A-Za-z0-9]/.test(pass)) strength += 1;

  return strength;
});

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value;
  if (strength === 0) return "strength-0";
  if (strength === 1) return "strength-1";
  if (strength === 2) return "strength-2";
  if (strength === 3) return "strength-3";
  return "strength-4";
});

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value;
  const texts = ["Muy débil", "Débil", "Regular", "Fuerte", "Muy fuerte"];
  return texts[strength];
});

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

/* Estilos adicionales para el modal de recuperación */

.cooldown-text {
  color: #ff9800;
  font-size: 0.9rem;
  margin-top: 10px;
  text-align: center;
}

.attempts-text {
  color: #f44336;
  font-size: 0.9rem;
  margin: 5px 0;
  text-align: center;
}

.code-input {
  text-align: center;
  letter-spacing: 2px;
  font-size: 1.2rem;
  font-weight: bold;
  font-family: monospace;
}

.password-strength {
  margin: 15px 0;
}

.strength-bar {
  height: 5px;
  border-radius: 3px;
  margin-bottom: 5px;
  transition: width 0.3s, background-color 0.3s;
}

.strength-0 {
  width: 25%;
  background-color: #f44336;
}
.strength-1 {
  width: 50%;
  background-color: #ff9800;
}
.strength-2 {
  width: 75%;
  background-color: #ffeb3b;
}
.strength-3 {
  width: 90%;
  background-color: #4caf50;
}
.strength-4 {
  width: 100%;
  background-color: #2e7d32;
}

.strength-text {
  font-size: 0.9rem;
  color: #666;
  text-align: center;
}

.secondary {
  background-color: #6c757d;
  margin-top: 10px;
}

.secondary:hover {
  background-color: #5a6268;
}

.success-step {
  text-align: center;
}

.success-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.success-title {
  color: #4caf50;
  margin-bottom: 15px;
}

.success-text {
  color: #666;
  margin-bottom: 25px;
  line-height: 1.5;
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

  .code-input {
    font-size: 1.1rem;
    letter-spacing: 1px;
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
