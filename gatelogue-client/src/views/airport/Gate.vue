<script setup lang="ts">
import { type Gate, gatelogueData } from "@/stores/data";
import AirlineLink from "@/components/AirlineLink.vue";
import Flight from "./Flight.vue";
import Sourced from "@/components/Sourced.vue";
import { computed } from "vue";

const props = defineProps<{
  gate?: Gate;
  gateId: string;
  maxGateFlightsLength?: number;
}>();
const gate = computed(
  () => props.gate ?? gatelogueData.value!.gate[props.gateId]!,
);
const airline = computed(() => {
  if (gate.value.airline) return gate.value.airline;
  if (
    gate.value.code &&
    gate.value.code !== "?" &&
    gate.value.flights.length > 0
  )
    return gatelogueData.value!.flight[gate.value.flights[0].v]!.airline;
  return undefined;
});
</script>

<template>
  <td class="gate-code">{{ gate.code }}</td>
  <td class="gate-size">
    <Sourced :sourced="gate.size" />
  </td>
  <td class="gate-airline">
    <Sourced v-if="airline" :sourced="airline"
      ><AirlineLink :airline-id="airline.v"
    /></Sourced>
  </td>
  <template v-for="flight in gate.flights" :key="flight.v">
    <Flight
      :gate-id="gateId"
      :flight-id="flight.v"
      :include-airline="airline === undefined"
    />
  </template>
  <td
    class="closing"
    :colspan="
      Math.max(0, (maxGateFlightsLength ?? 6) + 1 - gate.flights.length)
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
