import { ref, type Ref } from "vue";
import { type FromSchema } from "json-schema-to-ts";
import type schema from "./schema";

export type GatelogueData = FromSchema<typeof schema>

export const gatelogueData: Ref<GatelogueData | null> = ref(null)

fetch("https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json").then(res => res.json()).then(json => {gatelogueData.value = json})