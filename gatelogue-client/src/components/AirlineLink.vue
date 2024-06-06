<script setup lang="ts">
import type { Airline } from "@/stores/schema";
import { computed } from "vue";
import { gatelogueData } from "@/stores/data";

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
