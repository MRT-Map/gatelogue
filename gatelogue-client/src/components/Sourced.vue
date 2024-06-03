<script setup lang="ts">
import { Tippy } from "vue-tippy";
import { computed } from "vue";
const props = defineProps<{
  sourced: { v: unknown; s: string[] } | undefined | null;
}>();
const content = computed(() => {
  const sources = [...new Set(props.sourced?.s)]
    .join(", ")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  return `<span class="tooltip"><b>Source:</b> ${sources}</span>`;
});
</script>

<template>
  <Tippy v-if="sourced?.s" :content="content">
    <slot>{{ sourced.v }}</slot>
  </Tippy>
  <slot v-else>{{ sourced?.v }}</slot>
</template>

<style>
.tooltip {
  background-color: #0008;
  border-radius: 0.25em;
  padding: 0.25em;
  font-size: 0.5em;
}
</style>
