<script setup lang="ts">
import type { AirFlight, AirGate } from "gatelogue-types";
import AirlineLink from "@/components/AirlineLink.vue";
import { computed } from "vue";
import GateLink from "@/components/GateLink.vue";

const props = defineProps<{
  flight: AirFlight;
  gate: AirGate;
  includeAirline: boolean;
}>();
const otherGate = computed(() =>
  props.flight.to === props.gate ? props.flight.from : props.flight.to,
);
</script>

<template>
  <td class="gate-flights">
    <b>
      <template v-if="includeAirline">
        <AirlineLink :airline="flight.airline" />
      </template>
      {{ flight.code }}
    </b>
    <br />
    <GateLink :gate="otherGate" />
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
