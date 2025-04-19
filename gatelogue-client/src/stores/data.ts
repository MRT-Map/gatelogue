import { ref } from "vue";
import {GD} from "gatelogue-types";

export const gd = ref<GD | null>(null);

GD.get()
  .then((res) => {
    gd.value = res;
  });
