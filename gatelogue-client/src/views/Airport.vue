<script setup lang="ts">
  import { computed } from "vue";
  import { gatelogueData } from "../stores/data"
  import { useRoute } from "vue-router"
  import Gate from "./airport/Gate.vue";

  const route = useRoute();
  let airport = computed(() => gatelogueData.value?.airport[route.params.id as string]!)
  let gates = computed(() => airport.value.gates.map(g => gatelogueData.value?.gate[g.v as string]!).sort((a, b) => a.code!.localeCompare(b.code!)))
</script>

<template>
  <main>
    <b class="code">{{ airport.code }}</b><br>
    <a :href="airport.link?.v as string">
      <b class="name">{{ airport.name?.v ?? "" }}</b>
    </a><br>
    <b>
    <template v-if="airport.world">
      {{ airport.world?.v }} World
    </template>
    <template v-if="airport.coordinates">
      @ {{ airport.coordinates.v[0] }}, {{ airport.coordinates.v[1] }}
    </template>
    </b>
    <br /><br />
    <table>
      <tr v-for="gate in gates">
        <Gate :gate="gate" />
      </tr>
    </table>
  </main>
</template>

<style scoped>
  main {
    height: calc( 100vh - 1em );
    width: calc( 90vw - 9em );
    float: right;
    padding: 1em;
    padding-bottom: 0;
    overflow-y: auto;
    text-align: center;
  }
  .code {
    font-size: 5em;
  }
  .name {
    font-size: 3em;
  }
  table {
    width: 90%;
  }
</style>