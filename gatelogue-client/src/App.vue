<script setup lang="ts">
import { RouterView, useRoute } from "vue-router";
import Loading from "./views/Loading.vue";
import Sidebar from "./components/Sidebar.vue";
import { gd } from "./stores/data";
const route = useRoute();
</script>

<template>
  <Transition mode="out-in">
    <div v-if="gd == null"><Loading /></div>
    <div v-else>
      <Sidebar />
      <RouterView v-slot="{ Component }">
        <Transition mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </RouterView>
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
  margin: 0;
  padding: 1em 1em 0;
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
hr {
  border-style: solid;
  color: var(--col-c);
}
</style>
<style scoped>
/*noinspection CssUnusedSymbol*/
.v-enter-active,
.v-leave-active {
  transition: all 0.15s ease;
}
/*noinspection CssUnusedSymbol*/
.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
