<script setup lang="ts">
import { ref, computed } from "vue";
import { gatelogueData } from "../stores/data";
import { useRoute } from "vue-router";

const route = useRoute();
let sel = computed(() => {
  return {
    cat: route.path.split("/")[1],
    id: route.path.split("/")[2],
  };
});
let objects = gatelogueData.value!;

const panels = [
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
];

const selPanel = ref(panels[0]);
const sortedObjects = computed(() => {
  console.warn(selPanel.value, objects[selPanel.value.cat]);
  return Object.entries(objects[selPanel.value.cat] as any).sort(
    ([_, a], [__, b]) =>
      (a as any)[selPanel.value.objDisplay].localeCompare(
        (b as any)[selPanel.value.objDisplay],
      ),
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
          {{ (o as any)[selPanel.objDisplay] }}
        </div>
      </RouterLink>
    </template>
  </nav>
</template>

<style scoped>
nav {
  background-color: #333;
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
  background-color: #111;
  margin: 0.5em;
  padding: 0.5em;
  text-align: center;
  user-select: none;
  box-shadow: #1118 0px 3px;
  transition: all 0.1s ease;
  color: white;
  text-overflow: ellipsis;
}
.button.sel {
  background-color: #f40;
  box-shadow: #f408 0px 3px;
}
.button:hover {
  background-color: #888;
  color: #111;
  box-shadow: #8888 0px 4px;
  transform: translateY(-1px);
  cursor: pointer;
}
.button.sel:hover {
  background-color: #f84;
  box-shadow: #f848 0px 4px;
}

.button:active {
  background-color: #aaa !important;
  box-shadow: #aaa8 0px 0px !important;
  transform: translateY(3px);
  color: #111;
}
</style>
