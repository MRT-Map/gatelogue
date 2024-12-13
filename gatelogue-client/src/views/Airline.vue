<script setup lang="ts">
import { computed, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { AirFlight } from "@/stores/schema";
import Flight from "./airline/Flight.vue";
import VueJsonPretty from "vue-json-pretty";
import { gd } from "@/stores/data";
import GateLink from "@/components/GateLink.vue";
import Sourced from "@/components/Sourced.vue";

const route = useRoute();
const router = useRouter();
const airline = computed(
  () =>
    gd.value!.airAirline(route.params.id as string) ??
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
  airline.value.flights
    .map(
      (f) =>
        [f.v.toString(), gd.value!.airFlight(f.v.toString())!] as [
          string,
          AirFlight,
        ],
    )
    .sort(([, a], [, b]) => {
      if (!a.codes[0]) return 100;
      if (!b.codes[0]) return -100;
      return a.codes[0]!.localeCompare(b.codes[0]!, "en", { numeric: true });
    }),
);
const maxFlightGatesLength = computed(() =>
  Math.max(...flights.value.map(([, f]) => f.gates.length)),
);

const gates = computed(() =>
  airline.value.gates
    .map((g) => ({ s: g.s, v: gd.value!.airGate(g.v.toString())! }))
    .sort((g1, g2) => {
      const a1 = gd.value!.airAirport(g1.v.airport.v.toString())!.code;
      const a2 = gd.value!.airAirport(g2.v.airport.v.toString())!.code;
      return a1 === a2
        ? (g1.v.code ?? "?").localeCompare(g2.v.code ?? "?")
        : a1.localeCompare(a2);
    }),
);
</script>

<template>
  <main>
    <a :href="airline.link?.v">
      <b class="name">{{ airline.name }}</b></a
    ><br />
    <table>
      <tr v-for="[flightId, flight] in flights" :key="flightId">
        <Flight
          :flight-id="flightId"
          :flight="flight"
          :max-flight-gates-length="maxFlightGatesLength"
        ></Flight>
      </tr>
    </table>
    <hr />
    <h1>Owned Gates</h1>
    <div class="owned-gates">
      <div
        v-for="gate in gates"
        :key="gate.v.code ?? '?'"
        class="owned-gate"
        :class="{ empty: gate.v.flights.length == 0 }"
      >
        <Sourced :sourced="gate">
          <GateLink :gate="gate.v" />
        </Sourced>
      </div>
    </div>
    <span> Source: {{ airline.source.join(", ") }} </span>
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
