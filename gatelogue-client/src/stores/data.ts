import { type Ref, ref } from "vue";
import { GD } from "gatelogue-types";

export const gd: Ref<GD | null> = ref(null);

GD.get().then((res) => {
  res.db.run(`
    CREATE INDEX AirAirlineNameIndex ON AirAirline(name);
    CREATE INDEX AirFlightAirlineIndex ON AirFlight(airline);
    CREATE INDEX AirFlightFromIndex ON AirFlight("from");
    CREATE INDEX AirFlightToIndex ON AirFlight("to");
    CREATE INDEX AirGateAirlineIndex ON AirGate(airline);
    CREATE INDEX AirGateAirportIndex ON AirGate(airport);
    CREATE INDEX AirAirportCodeIndex ON AirAirport(code);
    CREATE INDEX NodeTypeIndex ON Node(type);
  `);
  gd.value = res;
});
