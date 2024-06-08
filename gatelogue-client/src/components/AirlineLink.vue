<script setup lang="ts">
import type { Airline, ID } from "@/stores/schema";
import { computed } from "vue";
import { gd } from "@/stores/data";

const props = defineProps<{
  airline?: Airline;
  airlineId: ID;
}>();

const airline = computed(
  () => props.airline ?? gd.value?.airAirline(props.airlineId)!,
);
</script>

<template>
  <RouterLink :to="`/airline/${airlineId}`">{{ airline.name }}</RouterLink>
</template>
