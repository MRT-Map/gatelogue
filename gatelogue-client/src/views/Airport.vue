<script setup lang="ts">
import { computed, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AirAirport, AirGate } from "gatelogue-types";
import Gate from "./airport/Gate.vue";
import { gd } from "@/stores/data";

const route = useRoute();
const router = useRouter();
const airport = computed(() => {
  const result = gd.value!.execGetZeroOrOne<[number]>(
    "SELECT i FROM AirAirport WHERE i = ? UNION ALL SELECT i FROM AirAirport WHERE code = ?",
    [parseInt(route.params.id as string), route.params.id as string],
  );
  if (result === null) return undefined as never;
  return new AirAirport(result[0], gd.value!);
});
watchEffect(() => {
  if (airport.value === undefined) {
    router.replace("/").then(() => router.go(0));
  }
  router.replace(`/airport/${encodeURIComponent(airport.value.code)}`);
});

const gates = computed(() =>
  gd
    .value!.execGetMany<[string | null, number]>(
      "SELECT code, i FROM AirGate WHERE airport = ?",
      [airport.value.i],
    )
    .map(([code, i]): [string | null, AirGate] => [
      code,
      new AirGate(i, gd.value!),
    ])
    .sort(([aCode], [bCode]) => {
      if (!aCode) return 100;
      if (!bCode) return -100;
      return aCode!.localeCompare(bCode!, "en", { numeric: true });
    })
    .map(([, a]) => a),
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
