<script setup lang="ts">
import type { AirGate, StringID } from "@/stores/schema";
import { computed } from "vue";
import { gd } from "@/stores/data";
import { RouterLink } from "vue-router";

const props = defineProps<{
  gate?: AirGate;
  gateId?: StringID<AirGate>;
}>();

const gate = computed(() => props.gate ?? gd.value?.airGate(props.gateId!)!);
const airport = computed(
  () => gd.value?.airAirport(gate.value.airport.v.toString())!,
);
</script>

<template>
  <RouterLink :to="`/airport/${airport.i}`">
    {{ airport.code }}-{{ gate.code ?? "?" }}
  </RouterLink>
</template>
