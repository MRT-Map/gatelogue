<script setup lang="ts">
import { type Gate as GateT, gatelogueData } from "@/stores/data";
import { computed, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import Gate from "./airport/Gate.vue";
import Sourced from "@/components/Sourced.vue";
import VueJsonPretty from "vue-json-pretty";

const route = useRoute();
const router = useRouter();
const airport = computed(
  () =>
    gatelogueData.value?.airport[route.params.id as string] ??
    Object.values(gatelogueData.value!.airport).find(
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
  airport.value.gates
    .map((g) => [g.v, gatelogueData.value!.gate[g.v]!] as [string, GateT])
    .sort(([, a], [, b]) => {
      if (!a.code) return 100;
      if (!b.code) return -100;
      return a.code!.localeCompare(b.code!, "en", { numeric: true });
    }),
);
const maxGateFlightsLength = computed(() =>
  Math.max(...gates.value.map(([, g]) => g.flights.length)),
);
</script>

<template>
  <main>
    <b class="code">{{ airport.code }}</b
    ><br />
    <a :href="airport.link?.v">
      <Sourced :sourced="airport.name">
        <b class="name">{{ airport.name?.v ?? "" }}</b>
      </Sourced> </a
    ><br />
    <b>
      <Sourced v-if="airport.world" :sourced="airport.world">
        {{ airport.world?.v }} World
      </Sourced>
      <Sourced v-if="airport.coordinates" :sourced="airport.coordinates">
        @ {{ airport.coordinates.v.join(", ") }}
      </Sourced>
    </b>
    <br /><br />
    <table>
      <tr v-for="[gateId, gate] in gates" :key="gateId">
        <Gate
          :gate-id="gateId"
          :gate="gate"
          :max-gate-flights-length="maxGateFlightsLength"
        />
      </tr>
    </table>
    <details>
      <summary>Json</summary>
      <VueJsonPretty :data="airport" :deep="1" />
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
