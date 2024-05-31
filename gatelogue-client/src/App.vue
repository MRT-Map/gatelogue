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
main {
  height: calc(100vh - 1em);
  width: calc(100vw - 15em);
  float: right;
  padding: 1em;
  padding-bottom: 0;
  overflow-y: auto;
  text-align: center;
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
  color: var(--acc-b);
}
</style>
