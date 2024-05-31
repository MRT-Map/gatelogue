<script setup lang="ts">
import { gatelogueData, type Category } from "@/stores/data";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
let sel = computed(() => {
  return {
    cat: route.path.split("/")[1],
    id: route.path.split("/")[2],
  };
});
let objects = gatelogueData.value!;

const panels: {
  cat: Category;
  catDisplay: string;
  objDisplay: string;
}[] = [
  {
    cat: "airport",
    catDisplay: "Airport",
    objDisplay: "code",
  },
  {
    cat: "airline",
    catDisplay: "Airline",
    objDisplay: "name",
  },
] as const;

const selPanel = ref(panels[0]);
const sortedObjects = computed(() => {
  return Object.entries(objects[selPanel.value.cat]).sort(([_, a], [__, b]) =>
    a[selPanel.value.objDisplay].localeCompare(b[selPanel.value.objDisplay]),
  );
});
</script>

<template>
  <nav>
    <template v-for="p in panels" :key="p.cat">
      <div
        class="button"
        @click="selPanel = p"
        :class="selPanel.cat === p.cat ? 'sel' : ''"
      >
        <button>
          <b>{{ p.catDisplay }}</b>
        </button>
      </div>
    </template>
    <hr />
    <template
      v-if="selPanel !== undefined"
      v-for="[id, o] in sortedObjects"
      :key="id"
    >
      <RouterLink :to="`/${selPanel.cat}/${id}`">
        <div
          class="button"
          :class="sel.cat === selPanel.cat && sel.id === id ? 'sel' : ''"
        >
          {{ o[selPanel.objDisplay] }}
        </div>
      </RouterLink>
    </template>
  </nav>
</template>

<style scoped>
nav {
  background-color: var(--col-b);
  height: calc(100vh - 1em);
  width: 10em;
  float: left;
  padding: 1em;
  padding-bottom: 0;
  overflow-y: auto;
}
button {
  all: unset;
}
a:hover {
  text-decoration: unset;
}
.button {
  border-radius: 1em;
  background-color: var(--col-a);
  margin: 0.5em;
  padding: 0.5em;
  text-align: center;
  user-select: none;
  box-shadow: var(--col-at) 0px 3px;
  transition: all 0.1s ease;
  color: white;
  text-overflow: ellipsis;
}
.button.sel {
  background-color: var(--acc-a);
  box-shadow: var(--acc-at) 0px 3px;
}
.button:hover {
  background-color: var(--col-d);
  color: var(--col-a);
  box-shadow: var(--col-dt) 0px 4px;
  transform: translateY(-1px);
  cursor: pointer;
}
.button.sel:hover {
  background-color: var(--acc-b);
  box-shadow: var(--acc-bt) 0px 4px;
}

.button:active {
  background-color: var(--col-e) !important;
  box-shadow: var(--col-et) 0px 0px !important;
  transform: translateY(3px);
  color: var(--col-a);
}
</style>