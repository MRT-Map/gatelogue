<script setup lang="ts">
import type { AirFlight, AirGate, StringID } from "@/stores/schema";
import Sourced from "@/components/Sourced.vue";
import { computed } from "vue";
import { gd } from "@/stores/data";
import GateLink from "@/components/GateLink.vue";

const props = defineProps<{
  flightId: StringID<AirFlight>;
  flight?: AirFlight;
  maxFlightGatesLength?: number;
}>();
const flight = computed(
  () => props.flight ?? gd.value!.airFlight(props.flightId)!,
);
const gates = computed(() =>
  flight.value.gates
    .map((g) => [g.s, gd.value!.airGate(g.v.toString())] as [string[], AirGate])
    .map(([s, g]) => ({
      v: g,
      s: s.concat(g.airport.s),
    })),
);
const size = computed(
  () => gates.value.map((g) => g.v.size).filter((s) => s?.v)[0],
);
</script>

<template>
  <td class="flight-code">{{ flight.codes.join(" ") }}</td>
  <td class="flight-size">
    <Sourced :sourced="size" />
  </td>
  <td v-for="gate in gates" :key="gate.v.code ?? '?'" class="flight-gates">
    <Sourced :sourced="gate">
      <GateLink :gate="gate.v" />
    </Sourced>
  </td>
  <td
    class="closing"
    :colspan="
      Math.max(0, (maxFlightGatesLength ?? 2) + 1 - flight.gates.length)
    "
  >
    &nbsp;&nbsp;&nbsp;
  </td>
</template>

<style scoped>
.flight-code {
  font-size: 2em;
  border-radius: 0.5em 0 0 0.5em;
  background-color: var(--acc-a);
  padding: 0.25em;
  font-weight: bold;
  width: 2em;
}
.flight-size {
  background-color: var(--col-b);
  padding: 0.25em;
  font-size: 1.5em;
  font-weight: bold;
  width: 2em;
}
.flight-gates {
  background-color: var(--col-c);
  padding: 0.25em;
  width: 5em;
  min-width: 5em;
  max-width: 5em;
}
.closing {
  font-size: 2em;
  border-radius: 0 0.5em 0.5em 0;
  background-color: var(--col-b);
  padding: 0.25em;
}
</style>
