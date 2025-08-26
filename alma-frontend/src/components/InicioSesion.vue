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
      <a href="#" class="forgot-password" @click.prevent="toggleRecoveryModal">
        ¿Olvidaste la contraseña?
      </a>
    </div>
  </div>
  <!-- Modal de recuperación -->
  <div v-if="showRecoveryModal" class="modal-overlay">
    <div class="modal-content">
      <h3>Recuperar Contraseña</h3>

      <div v-if="!codeSent">
        <input v-model="recoveryEmail" type="email" placeholder="Tu email" />
        <input
          v-model="whatsappNumber"
          type="tel"
          placeholder="5491123456789"
        />
        <button @click="sendWhatsAppCode">Enviar Código</button>
      </div>

      <div v-else-if="!verifiedCode">
        <p>Ingresa el código de 6 dígitos enviado por WhatsApp</p>
        <input v-model="recoveryCode" maxlength="6" />
        <button @click="verifyCode">Verificar</button>
      </div>

      <div v-else>
        <input
          v-model="newPassword"
          type="password"
          placeholder="Nueva contraseña"
        />
        <button @click="resetPassword">Cambiar Contraseña</button>
      </div>
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
const showRecoveryModal = ref(false); // Añade esta línea

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
    router.push("/inicio");
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail || "Credenciales incorrectas";
  }
};

// Función para mostrar el modal
const toggleRecoveryModal = () => {
  showRecoveryModal.value = !showRecoveryModal.value;
  if (!showRecoveryModal.value) {
    resetForm();
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
      token: recoveryCode.value, // Añade el código como token temporal
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

/* Estilos para el modal */
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
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
}

.modal-content input {
  display: block;
  width: 100%;
  padding: 8px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-content button {
  background-color: #7b5a50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}
</style>
