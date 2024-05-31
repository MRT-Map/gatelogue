<script setup lang="ts">
import { type Airline, gatelogueData } from "@/stores/data";
import { computed } from "vue";

const props = defineProps<{
  airline?: Airline;
  airlineId: string;
}>();

const airline = computed(
  () => props.airline ?? gatelogueData.value?.airline[props.airlineId]!,
);
</script>

<template>
  <RouterLink :to="`/airline/${airlineId}`">{{ airline.name }}</RouterLink>
</template>
