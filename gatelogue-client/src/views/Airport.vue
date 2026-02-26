<script setup lang="ts">
import { computed, type ComputedRef, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { type AirAirport } from "gatelogue-types";
import Gate from "./airport/Gate.vue";
import VueJsonPretty from "vue-json-pretty";
import { gd } from "@/stores/data";

const route = useRoute();
const router = useRouter();
const airport: ComputedRef<AirAirport> = computed(
  () =>
    (gd.value?.getNode(
      parseInt(route.params.id as string),
      "AirAirport",
    ) as AirAirport | null) ??
    Object.values(gd.value!.airAirports).find(
      (a) =>
        a.code !== null && a.code === (route.params.id as string).toUpperCase(),
    )!,
);
watchEffect(() => {
  if (airport.value === undefined) {
    router.replace("/").then(() => router.go(0));
  } else if (airport.value.code) {
    router.replace(`/airport/${encodeURIComponent(airport.value.code)}`);
  }
});

const gates = computed(() =>
  airport.value.gates.slice().sort((a, b) => {
    if (!a.code) return 100;
    if (!b.code) return -100;
    return a.code!.localeCompare(b.code!, "en", { numeric: true });
  }),
);
const maxGateFlightsLength = computed(() =>
  Math.max(...gates.value.map((g) => g.flightsFromHere.length)),
);
</script>

<template>
  <main>
    <b class="code">{{ airport.code }}</b>
    <br />
    <a :href="airport.link ?? ''">
      <b class="name">{{ airport.names?.join(" / ") ?? "" }}</b>
    </a>
    <br />
    <b>
      <span v-if="airport.world"> {{ airport.world }} World </span>
      <span v-if="airport.coordinates">
        @ {{ airport.coordinates.join(", ") }}
      </span>
    </b>
    <br /><br />
    <table>
      <tr v-for="gate in gates" :key="gate.i">
        <Gate :gate="gate" :max-gate-flights-length="maxGateFlightsLength" />
      </tr>
    </table>
    <details>
      <summary>Json</summary>
      <VueJsonPretty :data="airport as any" :deep="1" />
    </details>
    <br />
  </main>
</template>

<style scoped>
.code {
  font-size: 5em;
}
.name {
  font-size: 3em;
}
table {
  width: 100%;
}
</style>
