<template>
  <BaseModal
    :show="show"
    :title="title"
    size="small"
    @update:show="$emit('update:show', $event)"
    @close="$emit('cancel')"
  >
    <p>{{ message }}</p>

    <template #footer>
      <ModalButtons
        :confirm-text="confirmText"
        @cancel="$emit('cancel')"
        @confirm="$emit('confirm')"
      />
    </template>
  </BaseModal>
</template>

<script setup>
import BaseModal from "./BaseModal.vue";
import ModalButtons from "./ModalButtons.vue";

defineProps({
  show: Boolean,
  title: String,
  message: String,
  confirmText: {
    type: String,
    default: "Eliminar",
  },
});

defineEmits(["update:show", "cancel", "confirm"]);
</script>
