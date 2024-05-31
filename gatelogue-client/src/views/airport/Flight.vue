<script setup lang="ts">
import { type Airport, type Gate, gatelogueData } from "@/stores/data";
import AirlineLink from "@/components/AirlineLink.vue";
import Sourced from "@/components/Sourced.vue";
import { computed } from "vue";

const props = defineProps<{
  flightId: string;
  gateId: string;
  includeAirline: boolean;
}>();
const flight = computed(() => gatelogueData.value!.flight[props.flightId]!);
const otherGates = computed(() =>
  flight.value.gates
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
    .map(([s, g, a]) => ({
      v: [`${a.code}${g.code ? `-${g.code}` : ""}`, g.airport.v] as [
        string,
        string,
      ],
      s,
    })),
);
const airline = computed(() => flight.value.airline);
</script>

<template>
  <td class="gate-flights">
    <b
      ><Sourced v-if="includeAirline" :sourced="airline"
        ><AirlineLink :airline-id="airline.v"
      /></Sourced>
      {{ flight.codes[0] }}</b
    >
    <Sourced v-for="gate in otherGates" :key="gate.v[0]" :sourced="gate">
      <br />
      <RouterLink :to="`/airport/${gate.v[1]}`">{{ gate.v[0] }}</RouterLink>
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
