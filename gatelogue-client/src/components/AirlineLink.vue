<script setup lang="ts">
import { gatelogueData, type Airline, type GatelogueData } from "@/stores/data";
import { computed } from "vue";

let props = defineProps<{
  airline?: Airline;
  airlineId: string;
}>();

let airline = computed(
  () => props.airline ?? gatelogueData.value?.airline[props.airlineId]!,
);
</script>

<template>
  <RouterLink :to="`/airline/${airlineId}`">{{ airline.name }}</RouterLink>
</template>
