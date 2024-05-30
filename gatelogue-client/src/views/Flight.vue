<script setup lang="ts">
  import { computed } from "vue";
import { gatelogueData } from "../stores/data"
  import { useRoute } from "vue-router"

  const route = useRoute();
  let flight = computed(() => gatelogueData.value?.flight[route.params.id as string])
</script>

<template>
  <main>
    {{ JSON.stringify(flight) }}
  </main>
</template>
