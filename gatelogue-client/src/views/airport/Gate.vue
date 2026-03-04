<script setup lang="ts">
import type { AirGate } from "gatelogue-types";
import AirlineLink from "@/components/AirlineLink.vue";
import Flight from "./Flight.vue";
import { computed } from "vue";

const props = defineProps<{
  gate: AirGate;
  maxGateFlightsLength?: number;
}>();
const oneFlight = computed(() => {
  if (
      (props.gate.flightsFromHere.length > 0 ||
          props.gate.flightsToHere.length > 0)
  ) {
    return (props.gate.flightsFromHere[0] ?? props.gate.flightsToHere[0]!)
  }
  return undefined;
})
const airline = computed(() => {
  if (props.gate.airline) return props.gate.airline;
  return oneFlight.value?.airline;
});
const gateWidth = computed(() => {
  // eslint-disable-next-line
  let width: number | null | undefined = props.gate.width;
  if (width !== null) {
    return width.toString()
  }
  width = oneFlight.value?.aircraft?.width;
  if (width !== undefined) {
    return `≥${width}`
  }
  return undefined
})
</script>

<template>
  <td class="gate-code">{{ gate.code }}</td>
  <td class="gate-size-mode">
    <b>{{ gateWidth }}</b><br>{{ gate.mode?.replaceAll(" plane", "") ?? "&nbsp;" }}
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
.gate-size-mode {
  background-color: var(--col-c);
  padding: 0.25em;
  font-size: 1.5em;
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
