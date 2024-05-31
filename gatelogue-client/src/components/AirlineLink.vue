<script setup lang="ts">
import { gatelogueData, type GatelogueData } from "@/stores/data";
import { computed } from "vue";

let props = defineProps<{
  airline?: GatelogueData["airline"][string];
  airlineId: string;
}>();

let airline = computed(
  () => props.airline ?? gatelogueData.value?.airline[props.airlineId]!,
);
</script>

<template>
  <RouterLink :to="`/airline/${airlineId}`">{{ airline.name }}</RouterLink>
</template>
