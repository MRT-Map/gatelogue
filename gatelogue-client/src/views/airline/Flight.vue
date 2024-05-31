<script setup lang="ts">
import {
  type Airport,
  type Flight,
  type Gate,
  gatelogueData,
} from "@/stores/data";
import { RouterLink } from "vue-router";
import Sourced from "@/components/Sourced.vue";
import { computed } from "vue";

const props = defineProps<{
  flightId: string;
  flight?: Flight;
  maxFlightGatesLength?: number;
}>();
const flight = computed(
  () => props.flight ?? gatelogueData.value!.flight[props.flightId]!,
);
const gates = computed(() =>
  flight.value.gates
    .map((g) => [g.s, gatelogueData.value!.gate[g.v]] as [string[], Gate])
    .map(([s, g]) => ({
      v: [g, gatelogueData.value!.airport[g.airport.v]] as [Gate, Airport],
      s: s.concat(g.airport.s),
    })),
);
const size = computed(
  () => gates.value.map((g) => g.v[0].size).filter((s) => s?.v)[0],
);
</script>

<template>
  <td class="flight-code">{{ flight.codes.join(" ") }}</td>
  <td class="flight-size">
    <Sourced :sourced="size" />
  </td>
  <td v-for="gate in gates" :key="gate.v[1].code" class="flight-gates">
    <Sourced :sourced="gate">
      <RouterLink :to="`/airport/${gate.v[0].airport.v}`">
        {{ gate.v[1].code }}-{{ gate.v[0].code ?? "?" }}
      </RouterLink>
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
