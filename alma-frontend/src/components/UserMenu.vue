<template>
  <div class="user-menu-container">
    <i class="fas fa-user user-icon" @click="toggleMenu"></i>
    <div v-if="isOpen" class="user-menu">
      <div class="menu-header">{{ userEmail }}</div>
      <div class="menu-item" @click="openChangePassword">
        Cambiar contraseña
      </div>
      <div class="menu-item" @click="logout">Cerrar sesión</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  userEmail: {
    type: String,
    default: "Usuario",
  },
});

const emit = defineEmits(["changePassword", "logout"]);

const isOpen = ref(false);

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const openChangePassword = () => {
  isOpen.value = false;
  emit("changePassword");
};

const logout = () => {
  isOpen.value = false;
  emit("logout");
};
</script>
