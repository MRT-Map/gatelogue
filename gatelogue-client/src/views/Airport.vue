<script setup lang="ts">
import { computed } from "vue";
import { gatelogueData, type Gate as GateT } from "@/stores/data";
import { useRoute } from "vue-router";
import Gate from "./airport/Gate.vue";
import Sourced from "@/components/Sourced.vue";

const route = useRoute();
let airport = computed(
  () => gatelogueData.value?.airport[route.params.id as string]!,
);
let gates = computed(() =>
  airport.value.gates
    .map((g) => [g.v, gatelogueData.value!.gate[g.v]!] as [string, GateT])
    .sort(([_, a], [__, b]) => a.code!.localeCompare(b.code!)),
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
      <tr v-for="[gateId, gate] in gates">
        <Gate :gateId="gateId" :gate="gate" />
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
