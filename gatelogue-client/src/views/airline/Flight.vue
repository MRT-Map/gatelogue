<script setup lang="ts">
import type { AirFlight } from "gatelogue-types";
import { computed } from "vue";
import GateLink from "@/components/GateLink.vue";

const props = defineProps<{
  flight: AirFlight;
}>();
const aircraft = computed(() => props.flight.aircraft);

// const mrtTransitUrlParam = new URLSearchParams(window.location.search).get(
//   "mrt-transit",
// );
</script>

<template>
  <!--    :class="{-->
  <!--      'mrt-transit':-->
  <!--        !gate.s2.includes('MRT Transit (Air)') && mrtTransitUrlParam,-->
  <!--    }"-->
  <!--  >-->
  <td class="flight-code">
    {{ flight.code }}
  </td>
  <td class="flight-size-mode">
    <b>{{ aircraft?.name }} <small>{{ aircraft?.width ? `(↔${aircraft?.width})` : "" }}</small></b><br>{{ aircraft?.mode.replaceAll(" plane", "") }}
  </td>
  <td class="flight-gates">
    <GateLink :gate="flight.from" />
  </td>
  <td class="arrow">-></td>
  <td class="flight-gates">
    <GateLink :gate="flight.to" />
  </td>
  <td class="closing">
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
.flight-size-mode {
  background-color: var(--col-b);
  padding: 0.25em;
  font-size: 1.5em;
  width: 12em;
}
.flight-gates {
  background-color: var(--col-c);
  padding: 0.25em;
  width: 5em;
  min-width: 5em;
  max-width: 5em;
}
.arrow {
  font-size: 2em;
  font-weight: bolder;
  background-color: var(--col-b);
  padding: 0.25em;
  width: 2em;
}
/* .flight-gates.mrt-transit {
  background-color: var(--acc-b);
} */
.closing {
  font-size: 1em;
  border-radius: 0 0.5em 0.5em 0;
  background-color: var(--col-b);
  padding: 0.25em;
}
</style>
