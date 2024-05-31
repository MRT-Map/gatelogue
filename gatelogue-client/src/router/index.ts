import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from "../views/Home.vue";
import AirlineView from "../views/Airline.vue";
import AirportView from "../views/Airport.vue";

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/airline/:id",
      name: "airline",
      component: AirlineView,
    },
    {
      path: "/airport/:id",
      name: "airport",
      component: AirportView,
    },
  ],
});

export default router;
