<template>
  <div class="app-layout">
    <Sidebar @navigate="handleNavigation" />

    <div class="main-container">
      <Header/>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import Sidebar from "./Sidebar.vue";
import Header from "./Header.vue";

const router = useRouter();

const handleNavigation = (route) => {
  router.push(route);
};

</script>
