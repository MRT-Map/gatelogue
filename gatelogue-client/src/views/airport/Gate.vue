<script setup lang="ts">
import { computed } from "vue";
import { gatelogueData, type GatelogueData } from "../../stores/data";
import Flight from "./Flight.vue";
import AirlineLink from "@/components/AirlineLink.vue";

let props = defineProps<{
  gate: GatelogueData["gate"][string];
}>();
let airline = computed(() =>
  props.gate.code && props.gate.code !== "?" && props.gate.flights.length > 0
    ? (gatelogueData.value?.flight[props.gate.flights[0].v as string]?.airline
        .v as string) ?? ""
    : "",
);
</script>

<template>
  <td class="gate-code">{{ gate.code }}</td>
  <td class="gate-size">{{ gate.size?.v ?? "?" }}</td>
  <td class="gate-airline">
    <template v-if="airline !== ''"
      ><AirlineLink :airlineId="airline"
    /></template>
  </td>
  <template v-for="flight in gate.flights">
    <Flight
      :gateId="gate.id as string"
      :flightId="flight.v as string"
      :includeAirline="airline === ''"
    />
  </template>
  <td class="closing" :colspan="Math.max(0, 7 - gate.flights.length)">
    &nbsp;&nbsp;&nbsp;
  </td>
</template>

<style>
.gate-code {
  font-size: 2em;
  border-radius: 0.5em 0 0 0.5em;
  background-color: #f40;
  padding: 0.25em;
  font-weight: bold;
  width: 2em;
}
.gate-size {
  background-color: #555;
  padding: 0.25em;
  font-size: 1.5em;
  font-weight: bold;
  width: 2em;
}
.gate-airline {
  background-color: #333;
  padding: 0.25em;
  font-size: 1.5em;
  color: #fff;
  width: 2em;
}
.closing {
  font-size: 2em;
  border-radius: 0 0.5em 0.5em 0;
  background-color: #333;
  padding: 0.25em;
}
</style>
