import { type Ref, ref } from "vue";
import { GD } from "gatelogue-types";

export const gd: Ref<GD | null> = ref(null);

GD.get().then((res) => {
  gd.value = res;
});
