import { GD } from "./schema";
import { ref } from "vue";

export const gd = ref<GD | null>(null);

fetch("https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json")
  .then((res) => res.json())
  .then((json) => {
    gd.value = new GD(json);
  });
