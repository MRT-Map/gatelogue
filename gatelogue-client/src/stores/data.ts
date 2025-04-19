import { ref } from "vue";
import {GD} from "gatelogue-types";

export const gd = ref<GD | null>(null);

fetch("https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json")
  .then((res) => res.json())
  .then((json) => {
    gd.value = new GD(json);
  });
