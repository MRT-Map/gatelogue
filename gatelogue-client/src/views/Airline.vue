<script setup lang="ts">
import { computed, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { AirFlight } from "@/stores/schema";
import Flight from "./airline/Flight.vue";
import VueJsonPretty from "vue-json-pretty";
import { gd } from "@/stores/data";

const route = useRoute();
const router = useRouter();
const airline = computed(
  () =>
    gd.value!.airAirline(route.params.id as string) ??
    Object.values(gd.value!.airAirlines).find(
      (a) => a.name === route.params.id,
    )!,
);
watchEffect(() => {
  if (airline.value === undefined) {
    router.replace("/").then(() => router.go(0));
  } else if (airline.value.name) {
    router.replace(`/airline/${airline.value.name}`);
  }
});

const flights = computed(() =>
  airline.value.flights
    .map((f) => [f.v.toString(), gd.value!.airFlight(f.v.toString())!] as [string, AirFlight])
    .sort(([, a], [, b]) => {
      if (!a.codes[0]) return 100;
      if (!b.codes[0]) return -100;
      return a.codes[0]!.localeCompare(b.codes[0]!, "en", { numeric: true });
    }),
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
          :flight-id="flightId"
          :flight="flight"
          :max-flight-gates-length="maxFlightGatesLength"
        ></Flight>
      </tr>
    </table>
    <details>
      <summary>Json</summary>
      <VueJsonPretty :data="airline as any" :deep="1" />
    </details>
    <br />
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
