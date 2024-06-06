import type { AirData } from "./schema";
import { ref } from "vue";

export const gatelogueData = ref<AirData<true> | null>(null);

fetch("https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json")
  .then((res) => res.json())
  .then((json) => {
    gatelogueData.value = json.air;
  });
