<script setup lang="ts">
import type { AirFlight, AirGate, StringID } from "gatelogue-types";
import { computed } from "vue";
import { gd } from "@/stores/data";
import GateLink from "@/components/GateLink.vue";

const props = defineProps<{
  flight: AirFlight;
}>();
const size = computed(() => props.flight.from.size ?? props.flight.to.size);

const mrtTransitUrlParam = new URLSearchParams(window.location.search).get(
  "mrt-transit",
);
</script>

<template>
  <td class="flight-code">
    {{ flight.code }}
  </td>
  <td class="flight-size">
    {{ size }}
  </td>
  <td
    v-for="gate in [flight.from, flight.to]"
    :key="gate.code ?? '?'"
    class="flight-gates"
  >
    <!--    :class="{-->
    <!--      'mrt-transit':-->
    <!--        !gate.s2.includes('MRT Transit (Air)') && mrtTransitUrlParam,-->
    <!--    }"-->
    <!--  >-->
    <GateLink :gate="gate" />
  </td>
  <td class="closing">&nbsp;&nbsp;&nbsp;</td>
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
.flight-gates.mrt-transit {
  background-color: var(--acc-b);
}
.closing {
  font-size: 2em;
  border-radius: 0 0.5em 0.5em 0;
  background-color: var(--col-b);
  padding: 0.25em;
}
</style>
