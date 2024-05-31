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
let maxFlightGatesLength = computed(() =>
  Math.max(...flights.value.map(([_, f]) => f.gates.length)),
);
</script>

<template>
  <main>
    <a :href="airline.link?.v">
      <b class="name">{{ airline.name }}</b> </a
    ><br />
    <table>
      <tr v-for="[flightId, flight] in flights">
        <Flight
          :flightId="flightId"
          :flight="flight"
          :maxFlightGatesLength="maxFlightGatesLength"
        ></Flight>
      </tr>
    </table>
  </main>
</template>

<style scoped>
.name {
  font-size: 5em;
}
table {
  width: 100%;
}
</style>
