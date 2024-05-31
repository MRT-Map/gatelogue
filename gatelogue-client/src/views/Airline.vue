<script setup lang="ts">
import { computed } from "vue";
import { gatelogueData } from "@/stores/data";
import { useRoute } from "vue-router";

const route = useRoute();
let airline = computed(
  () => gatelogueData.value!.airline[route.params.id as string]!,
);
</script>

<template>
  <main>
    {{ JSON.stringify(airline) }}
  </main>
</template>
