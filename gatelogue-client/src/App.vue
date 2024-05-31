<script setup lang="ts">
import { RouterView } from "vue-router";
import { gatelogueData } from "./stores/data";
import Sidebar from "./components/Sidebar.vue";
</script>

<template>
  <div v-if="gatelogueData == null">Loading...</div>
  <div v-else>
    <Sidebar />
    <RouterView />
  </div>
</template>

<style>
body {
  background-color: #111;
  height: 100vh;
  font-family: "Hanken Grotesk", sans-serif;
  color: white;
  margin: 0;
  padding: 0;
  color-scheme: dark;
}
a {
  color: unset;
  text-decoration: none;
}
a:hover {
  color: unset;
  text-decoration: underline;
}
a:active {
  color: #f84;
}
</style>
