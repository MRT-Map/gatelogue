<script setup lang="ts">
  import { computed } from "vue";
import { gatelogueData } from "../stores/data"
  import { useRoute } from "vue-router"

  const route = useRoute();
  let airport = computed(() => gatelogueData.value?.airport[route.params.id as string])
</script>

<template>
  <main>
    {{ JSON.stringify(airport) }}
  </main>
</template>
