<script setup lang="ts">
// eslint-disable-next-line no-undef
const version = APP_VERSION;
</script>

<template>
  <main>
    <div>
      <img src="/gat2-light.png" />
      <br />
      <span>Version {{ version }}</span
      ><br />
      <a href="https://github.com/MRT-Map/gatelogue">Github Repo</a><br />
      <span>Made by the MRT Mapping Services</span>
    </div>
  </main>
</template>

<style scoped>
main {
  font-size: 2em;
  font-weight: bold;
  width: calc(100vw - 10em);
}
div {
  padding: 25vh 0;
}
img {
  width: 40vw;
  height: auto;
}
a {
  color: var(--acc-a);
}
a:active {
  color: var(--acc-b);
}
</style>
