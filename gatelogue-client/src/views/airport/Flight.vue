<script setup lang="ts">
import { computed } from "vue";
import {
  gatelogueData,
  type Airport,
  type Gate,
  type GatelogueData,
} from "../../stores/data";
import AirlineLink from "@/components/AirlineLink.vue";
import Sourced from "@/components/Sourced.vue";
let props = defineProps<{
  flightId: string;
  gateId: string;
  includeAirline: boolean;
}>();
let flight = computed(() => gatelogueData.value!.flight[props.flightId]!);
let otherGates = computed(() => {
  return flight.value.gates
    .filter((g) => g.v !== props.gateId)
    .map((g) => [g.s, gatelogueData.value!.gate[g.v]!] as [string[], Gate])
    .map(
      ([s, g]) =>
        [
          s.concat(g.airport.s),
          g,
          gatelogueData.value!.airport[g.airport.v]!,
        ] as [string[], Gate, Airport],
    )
    .map(([s, g, a]) => {
      return {
        v: `${a.code}${g.code ? "-" + g.code : ""}`,
        s,
      };
    });
});
let airline = computed(() => flight.value.airline);
</script>

<template>
  <td class="gate-flights">
    <b
      ><Sourced v-if="includeAirline" :sourced="airline"
        ><AirlineLink :airlineId="airline.v"
      /></Sourced>
      {{ flight.codes[0] }}</b
    >
    <br />
    <Sourced v-for="gate in otherGates" :sourced="gate">
      {{ gate.v }}
      <br />
    </Sourced>
  </td>
</template>

<style>
.gate-flights {
  background-color: #555;
  padding: 0.25em;
  width: 5em;
  min-width: 5em;
  max-width: 5em;
}
</style>
