<script setup lang="ts">
import type { AirAirline, StringID } from "gatelogue-types";
import { computed } from "vue";
import { gd } from "@/stores/data";
import { RouterLink } from "vue-router";

const props = defineProps<{
  airline?: AirAirline;
  airlineId?: StringID<AirAirline>;
}>();

const airline = computed(
  () => props.airline ?? gd.value?.airAirline(props.airlineId!)!,
);
</script>

<template>
  <RouterLink :to="`/airline/${airline.i}`">{{ airline.name }}</RouterLink>
</template>
