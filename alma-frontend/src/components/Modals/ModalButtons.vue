<!-- components/ModalButtons.vue -->
<template>
  <div class="modal-buttons">
    <button
      v-if="showCancel"
      @click="cancel"
      class="cancel-button"
      type="button"
    >
      {{ cancelText }}
    </button>
    <button
      @click="confirm"
      class="confirm-button"
      :disabled="confirmDisabled"
      type="button"
    >
      {{ confirmText }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  showCancel: {
    type: Boolean,
    default: true,
  },
  cancelText: {
    type: String,
    default: "Cancelar",
  },
  confirmText: {
    type: String,
    default: "Confirmar",
  },
  confirmDisabled: Boolean,
});

const emit = defineEmits(["cancel", "confirm"]);

const cancel = () => emit("cancel");
const confirm = () => emit("confirm");
</script>

<style scoped>
.modal-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-button,
.confirm-button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.cancel-button {
  background: #6c757d;
  color: white;
}

.cancel-button:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.confirm-button {
  background: var(--color-primary);
  color: white;
}

.confirm-button:hover:not(:disabled) {
  background: #9c7a6d;
  transform: translateY(-1px);
}

.confirm-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}
</style>
