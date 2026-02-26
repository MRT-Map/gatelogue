<script setup lang="ts">
import { computed, type ComputedRef, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { AirAirline } from "gatelogue-types";
import Flight from "./airline/Flight.vue";
import VueJsonPretty from "vue-json-pretty";
import { gd } from "@/stores/data";
import GateLink from "@/components/GateLink.vue";

const route = useRoute();
const router = useRouter();
const airline: ComputedRef<AirAirline> = computed(
  () =>
    (gd.value?.getNode(
      parseInt(route.params.id as string),
      "AirAirline",
    ) as AirAirline | null) ??
    Object.values(gd.value!.airAirlines).find(
      (a) => a.name === route.params.id,
    )!,
);
watchEffect(() => {
  if (airline.value === undefined) {
    router.replace("/").then(() => router.go(0));
  } else if (airline.value.name) {
    router.replace(`/airline/${encodeURIComponent(airline.value.name)}`);
  }
});

const flights = computed(() =>
  airline.value.flights.slice().sort((a, b) => {
    if (!a.code) return 100;
    if (!b.code) return -100;
    return a.code!.localeCompare(b.code!, "en", { numeric: true });
  }),
);

const gates = computed(() =>
  airline.value.gates.slice().sort((g1, g2) => {
    const a1 = g1.airport.code;
    const a2 = g2.airport.code;
    return a1 === a2
      ? (g1.code ?? "?").localeCompare(g2.code ?? "?")
      : a1.localeCompare(a2);
  }),
);
</script>

<template>
  <main>
    <a :href="airline.link ?? ''">
      <b class="name">{{ airline.name }}</b></a
    ><br />
    <table>
      <tr v-for="flight in flights" :key="flight.i">
        <Flight :flight="flight"></Flight>
      </tr>
    </table>
    <hr />
    <h1>Owned Gates</h1>
    <div class="owned-gates">
      <div
        v-for="gate in gates"
        :key="gate.code ?? '?'"
        class="owned-gate"
        :class="{
          empty:
            gate.flightsFromHere.length === 0 &&
            gate.flightsToHere.length === 0,
        }"
      >
        <GateLink :gate="gate" />
      </div>
    </div>
    <details>
      <summary>Json</summary>
      <VueJsonPretty :data="airline as any" :deep="1" />
    </details>
    <br />
  </main>
</template>

<style scoped>
.name {
  font-size: 5em;
}
table {
  width: 100%;
}
.owned-gates {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}
.owned-gate {
  background-color: var(--col-c);
  padding: 0.25em;
  margin: 1px;
  width: 5em;
  min-width: 5em;
  max-width: 5em;
  border-radius: 0.5em;
}
.owned-gate.empty {
  background-color: var(--col-b);
}
</style>
