<script setup lang="ts">
import { computed } from "vue";
import { Tippy } from "vue-tippy";
let props = defineProps<{
  sourced: { v: any; s: string[] } | undefined | null;
}>();
let content = computed(() => {
  let sources = [...new Set(props.sourced?.s)].join(", ");
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
