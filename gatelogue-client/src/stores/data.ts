import { type Ref, ref } from "vue";
import { type FromSchema } from "json-schema-to-ts";
import type schema from "./schema";

export type GatelogueData = FromSchema<typeof schema>;
export type Category = "flight" | "airport" | "airline" | "gate";
export type Flight = GatelogueData["flight"][string];
export type Airport = GatelogueData["airport"][string];
export type Airline = GatelogueData["airline"][string];
export type Gate = GatelogueData["gate"][string];

export const gatelogueData: Ref<GatelogueData | null> = ref(null);

fetch("https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json")
  .then((res) => res.json())
  .then((json) => {
    gatelogueData.value = json.air;
  });
