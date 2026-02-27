<script setup lang="ts">
import { computed, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AirAirline, AirFlight, AirGate } from "gatelogue-types";
import Flight from "./airline/Flight.vue";
import { gd } from "@/stores/data";
import GateLink from "@/components/GateLink.vue";

const route = useRoute();
const router = useRouter();
const airline = computed(() => {
  const result = gd.value!.execGetZeroOrOne<[number]>(
    "SELECT i FROM AirAirline WHERE i = ? UNION ALL SELECT i FROM AirAirline WHERE name = ?",
    [parseInt(route.params.id as string), route.params.id as string],
  );
  if (result === null) return undefined as never;
  return new AirAirline(result[0], gd.value!);
});
watchEffect(() => {
  if (airline.value === undefined) {
    router.replace("/").then(() => router.go(0));
  }
  router.replace(`/airline/${encodeURIComponent(airline.value.name)}`);
});

const flights = computed(() =>
  gd
    .value!.execGetMany<[string, number]>(
      "SELECT code, i FROM AirFlight WHERE airline = ?",
      [airline.value.i],
    )
    .map(([code, i]): [string, AirFlight] => [
      code,
      new AirFlight(i, gd.value!),
    ])
    .sort(([aCode], [bCode]) => aCode!.localeCompare(bCode!, "en", { numeric: true }))
    .map(([, a]) => a),
);

const gates = computed(() =>
  gd
    .value!.execGetMany<[string, string | null, number]>(
      "SELECT AirAirport.code, AirGate.code, AirGate.i FROM AirGate LEFT JOIN AirAirport on AirAirport.i = AirGate.airport WHERE airline = ?",
      [airline.value.i],
    )
    .map(([aCode, gCode, i]): [string, string | null, AirGate] => [
      aCode,
      gCode,
      new AirGate(i, gd.value!),
    ])
    .sort(([aaCode, agCode], [baCode, bgCode]) =>
      aaCode === baCode
        ? (agCode ?? "?").localeCompare(bgCode ?? "?")
        : aaCode.localeCompare(baCode),
    )
    .map(([, , a]) => a),
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
