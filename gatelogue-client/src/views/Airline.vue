<script setup lang="ts">
import { computed } from "vue";
import { gatelogueData, type Flight as FlightT } from "@/stores/data";
import { useRoute } from "vue-router";
import Flight from "./airline/Flight.vue";

const route = useRoute();
let airline = computed(
  () => gatelogueData.value!.airline[route.params.id as string]!,
);
let flights = computed(() =>
  airline.value.flights
    .map((f) => [f.v, gatelogueData.value!.flight[f.v]!] as [string, FlightT])
    //.sort(([_, a], [__, b]) => a.codes[0]!.localeCompare(b.codes[0]!)),
    .sort(([_, a], [__, b]) => parseInt(a.codes[0]) - parseInt(b.codes[0])),
);
</script>

<template>
  <main>
    <a :href="airline.link?.v">
      <b class="name">{{ airline.name }}</b> </a
    ><br />
    <table>
      <tr v-for="[flightId, flight] in flights">
        <Flight :flightId="flightId" :flight="flight"></Flight>
      </tr>
    </table>
  </main>
</template>

<style scoped>
main {
  height: calc(100vh - 1em);
  width: calc(90vw - 9em);
  float: right;
  padding: 1em;
  padding-bottom: 0;
  overflow-y: auto;
  text-align: center;
}
.name {
  font-size: 5em;
}
table {
  width: 90%;
}
</style>
