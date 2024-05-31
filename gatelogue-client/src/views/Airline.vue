<script setup lang="ts">
import { type Flight as FlightT, gatelogueData } from "@/stores/data";
import Flight from "./airline/Flight.vue";
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const airline = computed(
  () => gatelogueData.value!.airline[route.params.id as string]!,
);
const flights = computed(() =>
  airline.value.flights
    .map((f) => [f.v, gatelogueData.value!.flight[f.v]!] as [string, FlightT])
    //.sort(([_, a], [__, b]) => a.codes[0]!.localeCompare(b.codes[0]!)),
    .sort(([, a], [, b]) => parseInt(a.codes[0]) - parseInt(b.codes[0])),
);
const maxFlightGatesLength = computed(() =>
  Math.max(...flights.value.map(([, f]) => f.gates.length)),
);
</script>

<template>
  <main>
    <a :href="airline.link?.v">
      <b class="name">{{ airline.name }}</b> </a
    ><br />
    <table>
      <tr v-for="[flightId, flight] in flights" :key="flightId">
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
