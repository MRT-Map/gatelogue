<script setup lang="ts">
import type { AirAirline } from "gatelogue-types";
import { RouterLink } from "vue-router";

defineProps<{
  airline: AirAirline;
}>();
</script>

<template>
  <RouterLink :to="`/airline/${airline.i}`">{{ airline.name }}</RouterLink>
</template>
