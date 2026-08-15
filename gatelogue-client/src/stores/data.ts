import { type Ref, shallowRef } from "vue";
import { BrowserGD } from "gatelogue-types";
import sqlite3InitModule from "@sqlite.org/sqlite-wasm";

export const gd: Ref<BrowserGD | null> = shallowRef(null);

(async () => {
  const sqlite3 = await sqlite3InitModule();
  const res = await BrowserGD.get(sqlite3);
  res.db.exec(`
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
})();
