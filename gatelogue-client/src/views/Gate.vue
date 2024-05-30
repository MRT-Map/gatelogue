<script setup lang="ts">
  import { computed } from "vue";
import { gatelogueData } from "../stores/data"
  import { useRoute } from "vue-router"

  const route = useRoute();
  let gate = computed(() => gatelogueData.value?.gate[route.params.id as string])
</script>

<template>
  <main>
    {{ JSON.stringify(gate) }}
  </main>
</template>
