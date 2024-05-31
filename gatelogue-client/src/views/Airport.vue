<script setup lang="ts">
import { type Gate as GateT, gatelogueData } from "@/stores/data";
import Gate from "./airport/Gate.vue";
import Sourced from "@/components/Sourced.vue";
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const airport = computed(
  () => gatelogueData.value?.airport[route.params.id as string]!,
);
const gates = computed(() =>
  airport.value.gates
    .map((g) => [g.v, gatelogueData.value!.gate[g.v]!] as [string, GateT])
    .sort(([, a], [, b]) =>
      a.code!.localeCompare(b.code!, "en", { numeric: true }),
    ),
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
