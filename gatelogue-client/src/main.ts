import { createApp } from "vue";
import "./colors.css";

import App from "./App.vue";
import router from "./router";
import { tippy } from "vue-tippy";

const app = createApp(App);

app.use(router);

tippy.setDefaultProps({
  placement: "right",
  allowHTML: true,
  arrow: true,
  delay: 0,
});

app.mount("#app");
