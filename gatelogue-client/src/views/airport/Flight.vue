<script setup lang="ts">
import type { AirGate } from "@/stores/schema";
import AirlineLink from "@/components/AirlineLink.vue";
import Sourced from "@/components/Sourced.vue";
import { computed } from "vue";
import { gd } from "@/stores/data";
import GateLink from "@/components/GateLink.vue";

const props = defineProps<{
  flightId: string;
  gateId: string;
  includeAirline: boolean;
}>();
const flight = computed(() => gd.value!.airFlight(props.flightId)!);
const otherGates = computed(() =>
  flight.value.gates
    .filter((g) => g.v.toString() !== props.gateId)
    .map(
      (g) => [g.s, gd.value!.airGate(g.v.toString())!] as [string[], AirGate],
    )
    .map(([s, g]) => ({ s: s.concat(g.airport.s), v: g })),
);
const airline = computed(() => flight.value.airline);
</script>

<template>
  <td class="gate-flights">
    <b
      ><Sourced v-if="includeAirline" :sourced="airline"
        ><AirlineLink :airline-id="airline.v.toString()"
      /></Sourced>
      {{ flight.codes[0] }}</b
    >
    <Sourced v-for="gate in otherGates" :key="gate.v.i" :sourced="gate">
      <br />
      <GateLink :gate="gate.v" />
    </Sourced>
  </td>
</template>

<style>
.gate-flights {
  background-color: var(--col-c);
  padding: 0.25em;
  width: 5em;
  min-width: 5em;
  max-width: 5em;
}
</style>
