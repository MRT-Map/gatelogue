<script setup lang="ts">
import { computed } from "vue";
import { gatelogueData, type GatelogueData } from "../../stores/data";
import AirlineLink from "@/components/AirlineLink.vue";
let props = defineProps<{
  flightId: string;
  gateId: string;
  includeAirline: boolean;
}>();
let flight = computed(() => gatelogueData.value!.flight[props.flightId]!);
let otherGates = computed(() => {
  return flight.value.gates
    .filter((g) => g.v !== props.gateId)
    .map((g) => gatelogueData.value!.gate[g.v]!)
    .map((g) => [g, gatelogueData.value!.airport[g.airport.v]!])
    .map(([g, a]) => `${a.code}${g.code ? "-" + g.code : ""}`);
});
let airline = computed(() => flight.value.airline.v);
</script>

<template>
  <td class="gate-flights">
    <b
      ><template v-if="includeAirline"
        ><AirlineLink :airlineId="airline"
      /></template>
      {{ flight.codes[0] }}</b
    >
    <br />
    <template v-for="gate in otherGates">
      {{ gate }}
      <br />
    </template>
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
