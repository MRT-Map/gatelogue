<script setup lang="ts">
import type { AirGate } from "gatelogue-types";
import { RouterLink } from "vue-router";

const props = defineProps<{
  gate: AirGate;
}>();
</script>

<template>
  <RouterLink :to="`/airport/${gate.airport.i}`">
    {{ gate.airport.code }}-{{ gate.code ?? "?" }}
  </RouterLink>
</template>
