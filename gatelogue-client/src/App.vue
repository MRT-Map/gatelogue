<script setup lang="ts">
import Loading from "./views/Loading.vue";
import { RouterView } from "vue-router";
import Sidebar from "./components/Sidebar.vue";
import { gatelogueData } from "./stores/data";
</script>

<template>
  <Transition mode="out-in">
    <div v-if="gatelogueData == null"><Loading /></div>
    <div v-else>
      <Sidebar />
      <RouterView />
    </div>
  </Transition>
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
  margin: 0;
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
<style scoped>
.v-enter-active,
.v-leave-active {
  transition: all 0.25s ease;
}
.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
