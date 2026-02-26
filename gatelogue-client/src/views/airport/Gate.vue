<script setup lang="ts">
import type { AirGate } from "gatelogue-types";
import AirlineLink from "@/components/AirlineLink.vue";
import Flight from "./Flight.vue";
import { computed } from "vue";

const props = defineProps<{
  gate: AirGate;
  maxGateFlightsLength?: number;
}>();
const airline = computed(() => {
  if (props.gate.airline) return props.gate.airline;
  if (
    props.gate.code &&
    props.gate.code !== "?" &&
    (props.gate.flightsFromHere.length > 0 ||
      props.gate.flightsToHere.length > 0)
  )
    return [...props.gate.flightsFromHere, ...props.gate.flightsToHere][0]!
      .airline;
  return undefined;
});
</script>

<template>
  <td class="gate-code">{{ gate.code }}</td>
  <td class="gate-size">
    {{ gate.size }}
  </td>
  <td class="gate-airline">
    <template v-if="airline">
      <AirlineLink :airline="airline" />
    </template>
  </td>
  <template v-for="flight in gate.flightsFromHere" :key="flight.i">
    <Flight
      :gate="gate"
      :flight="flight"
      :include-airline="airline === undefined"
    />
  </template>
  <td
    class="closing"
    :colspan="
      Math.max(0, (maxGateFlightsLength ?? 6) + 1 - gate.flightsFromHere.length)
    "
  >
    &nbsp;&nbsp;&nbsp;
  </td>
</template>

<style scoped>
.gate-code {
  font-size: 2em;
  border-radius: 0.5em 0 0 0.5em;
  background-color: var(--acc-a);
  padding: 0.25em;
  font-weight: bold;
  width: 2em;
}
.gate-size {
  background-color: var(--col-c);
  padding: 0.25em;
  font-size: 1.5em;
  font-weight: bold;
  width: 2em;
}
.gate-airline {
  background-color: var(--col-b);
  padding: 0.25em;
  font-size: 1.5em;
  color: #fff;
  width: 2em;
}
.closing {
  font-size: 2em;
  border-radius: 0 0.5em 0.5em 0;
  background-color: var(--col-b);
  padding: 0.25em;
}
</style>
