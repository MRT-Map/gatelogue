<script setup lang="ts">
import { computed, ref } from "vue";
import {
  type AirAirline,
  type AirAirport,
  GD,
  type Node,
} from "gatelogue-types";
import { gd } from "@/stores/data";
import { useRoute } from "vue-router";

const route = useRoute();
const sel = computed(() => ({
  cat: route.path.split("/")[1],
  id: Number(route.path.split("/")[2]),
}));
const objects: GD = gd.value!;

interface Panel<T extends Node = Node> {
  cat: string;
  getter: () => T[];
  catDisplay: string;
  objDisplay: keyof T;
}

const airportPanel: Panel<AirAirport> = {
  cat: "airport",
  getter: () => objects.airAirports,
  catDisplay: "Airport",
  objDisplay: "code",
};
const airlinePanel: Panel<AirAirline> = {
  cat: "airline",
  getter: () => objects.airAirlines,
  catDisplay: "Airline",
  objDisplay: "name",
};
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const panels: Panel<any>[] = [airlinePanel, airportPanel] as const;

const selPanel = ref(panels[0]);
const sortedObjects = computed(() =>
  selPanel.value.getter().sort((a, b) => {
    if (a[selPanel.value.objDisplay] === null) return 100;
    if (b[selPanel.value.objDisplay] === null) return -100;
    return a[selPanel.value.objDisplay].localeCompare(
      b[selPanel.value.objDisplay],
    );
  }),
);
</script>

<template>
  <nav>
    <RouterLink to="/"><img src="/gat2-light.png" /></RouterLink>
    <hr />
    <template v-for="p in panels" :key="p.cat">
      <div
        class="button"
        :class="selPanel.cat === p.cat ? 'sel' : ''"
        @click="selPanel = p"
      >
        <button>
          <b>{{ p.catDisplay }}</b>
        </button>
      </div>
    </template>
    <hr />
    <template v-if="selPanel !== undefined">
      <RouterLink
        v-for="o in sortedObjects"
        :key="o.i"
        :to="`/${selPanel.cat}/${o.i}`"
      >
        <div
          class="button"
          :class="sel.cat === selPanel.cat && sel.id === o.i ? 'sel' : ''"
        >
          {{ o[selPanel.objDisplay] ?? o.name.v }}
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
  padding: 1em 1em 0;
  overflow-y: auto;
}
img {
  width: 100%;
  transition: all 0.1s ease;
}
img:hover {
  filter: drop-shadow(0 2px 0 var(--col-a));
  transform: translateY(-2px);
  cursor: pointer;
}
img:active {
  filter: opacity(0.5) drop-shadow(0 0 0 var(--col-b));
  transform: translateY(0px);
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
  box-shadow: var(--col-at) 0 3px;
  transition: all 0.1s ease;
  color: white;
  text-overflow: ellipsis;
}
.button.sel {
  background-color: var(--acc-a);
  box-shadow: var(--acc-at) 0 3px;
}
.button:hover {
  background-color: var(--col-d);
  color: var(--col-a);
  box-shadow: var(--col-dt) 0 4px;
  transform: translateY(-1px);
  cursor: pointer;
}
.button.sel:hover {
  background-color: var(--acc-b);
  box-shadow: var(--acc-bt) 0 4px;
}

.button:active {
  background-color: var(--col-e) !important;
  box-shadow: var(--col-et) 0 0 !important;
  transform: translateY(3px);
  color: var(--col-a);
}
</style>
