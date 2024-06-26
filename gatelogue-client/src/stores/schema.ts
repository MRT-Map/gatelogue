/* eslint-disable max-lines */
export type ID = string;
export type World = "Old" | "New";
export type RailMode = "warp" | "cart" | "traincart" | "vehicles";
export type SeaMode = "ferry" | "cruise";

export type Sourced<T, S extends boolean = true> = S extends true
  ? { v: T; s: string[] }
  : T;

export interface Located<S extends boolean = true> {
  world: Sourced<World, S> | null;
  coordinates: Sourced<[number, number]> | null;
  proximity: Record<string, Record<ID, Sourced<{ distance: number }>>>;
}

export interface Direction {
  forward_towards_code: ID;
  forward_direction_label: string | null;
  backward_direction_label: string | null;
  one_way: boolean;
}

export interface Connection {
  line: ID;
  direction: Direction | null;
}

export interface AirFlight<S extends boolean = true> {
  codes: string[];
  gates: Sourced<ID, S>[];
  airline: Sourced<ID, S>;
}

export interface AirAirport<S extends boolean = true> extends Located {
  code: string;
  name: Sourced<string, S> | null;
  link: Sourced<string, S> | null;
  gates: Sourced<ID, S>[];
}

export interface AirGate<S extends boolean = true> {
  code: string | null;
  flights: Sourced<ID, S>[];
  airport: Sourced<ID, S>;
  airline: Sourced<ID, S> | null;
  size: Sourced<string, S> | null;
}

export interface AirAirline<S extends boolean = true> {
  name: string;
  flights: Sourced<ID, S>[];
  link: Sourced<string, S> | null;
}

export interface AirData<S extends boolean = true> {
  flight: Record<ID, AirFlight<S>>;
  airport: Record<ID, AirAirport<S>>;
  gate: Record<ID, AirGate<S>>;
  airline: Record<ID, AirAirline<S>>;
}

export interface RailCompany<S extends boolean = true> {
  name: string;
  lines: Sourced<ID, S>[];
  stations: Sourced<ID, S>[];
}

export interface RailLine<S extends boolean = true> {
  code: string;
  company: Sourced<ID, S>;
  ref_station: Sourced<ID, S>;
  mode: Sourced<RailMode, S> | null;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
}

export interface RailStation<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<ID, S>;
}

export interface RailData<S extends boolean = true> {
  rail_company: Record<ID, RailCompany<S>>;
  rail_line: Record<ID, RailLine<S>>;
  station: Record<ID, RailStation<S>>;
}

export interface SeaCompany<S extends boolean = true> {
  name: string;
  lines: Sourced<ID, S>[];
  stops: Sourced<ID, S>[];
}

export interface SeaLine<S extends boolean = true> {
  code: string;
  company: Sourced<ID, S>;
  ref_stop: Sourced<ID, S>;
  mode: Sourced<SeaMode, S> | null;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
}

export interface SeaStop<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<ID, S>;
}

export interface SeaData<S extends boolean = true> {
  sea_company: Record<ID, SeaCompany<S>>;
  sea_line: Record<ID, SeaLine<S>>;
  sea_stop: Record<ID, SeaStop<S>>;
}

export interface BusCompany<S extends boolean = true> {
  name: string;
  lines: Sourced<ID, S>[];
  stops: Sourced<ID, S>[];
}

export interface BusLine<S extends boolean = true> {
  code: string;
  company: Sourced<ID, S>;
  ref_stop: Sourced<ID, S>;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
}

export interface BusStop<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<ID, S>;
  connections: Record<ID, Sourced<Connection>[]>;
}

export interface BusData<S extends boolean = true> {
  bus_company: Record<ID, BusCompany<S>>;
  bus_line: Record<ID, BusLine<S>>;
  bus_stop: Record<ID, BusStop<S>>;
}

export interface GatelogueData<S extends boolean = true> {
  version: 1;
  timestamp: string;
  air: AirData<S>;
  rail: RailData<S>;
  sea: SeaData<S>;
  bus: BusData<S>;
}

export type Category<S extends boolean = true> =
  | AirFlight<S>
  | AirAirport<S>
  | AirGate<S>
  | AirAirline<S>
  | RailCompany<S>
  | RailLine<S>
  | RailStation<S>
  | SeaCompany<S>
  | SeaLine<S>
  | SeaStop<S>
  | BusCompany<S>
  | BusLine<S>
  | BusStop<S>;

export class GD<S extends boolean = true> {
  data: GatelogueData<S>;

  constructor(data: GatelogueData<S>) {
    this.data = data;
  }

  airFlight(id: ID): AirFlight<S> | undefined {
    return this.data.air.flight[id];
  }

  get airFlights(): Record<ID, AirFlight<S>> {
    return this.data.air.flight;
  }

  airAirport(id: ID): AirAirport<S> | undefined {
    return this.data.air.airport[id];
  }

  get airAirports(): Record<ID, AirAirport<S>> {
    return this.data.air.airport;
  }

  airGate(id: ID): AirGate<S> | undefined {
    return this.data.air.gate[id];
  }

  get airGates(): Record<ID, AirGate<S>> {
    return this.data.air.gate;
  }

  airAirline(id: ID): AirAirline<S> | undefined {
    return this.data.air.airline[id];
  }

  get airAirlines(): Record<ID, AirAirline<S>> {
    return this.data.air.airline;
  }

  railCompany(id: ID): RailCompany<S> | undefined {
    return this.data.rail.rail_company[id];
  }

  get railCompanies(): Record<ID, RailCompany<S>> {
    return this.data.rail.rail_company;
  }

  railLine(id: ID): RailLine<S> | undefined {
    return this.data.rail.rail_line[id];
  }

  get railLines(): Record<ID, RailLine<S>> {
    return this.data.rail.rail_line;
  }

  railStation(id: ID): RailStation<S> | undefined {
    return this.data.rail.station[id];
  }

  get railStations(): Record<ID, RailStation<S>> {
    return this.data.rail.station;
  }

  seaCompany(id: ID): SeaCompany<S> | undefined {
    return this.data.sea.sea_company[id];
  }

  get seaCompanies(): Record<ID, SeaCompany<S>> {
    return this.data.sea.sea_company;
  }

  seaLine(id: ID): SeaLine<S> | undefined {
    return this.data.sea.sea_line[id];
  }

  get seaLines(): Record<ID, SeaLine<S>> {
    return this.data.sea.sea_line;
  }

  seaStop(id: ID): SeaStop<S> | undefined {
    return this.data.sea.sea_stop[id];
  }

  get seaStops(): Record<ID, SeaStop<S>> {
    return this.data.sea.sea_stop;
  }

  busCompany(id: ID): BusCompany<S> | undefined {
    return this.data.bus.bus_company[id];
  }

  get busCompanies(): Record<ID, BusCompany<S>> {
    return this.data.bus.bus_company;
  }

  busLine(id: ID): BusLine<S> | undefined {
    return this.data.bus.bus_line[id];
  }

  get busLines(): Record<ID, BusLine<S>> {
    return this.data.bus.bus_line;
  }

  busStop(id: ID): BusStop<S> | undefined {
    return this.data.bus.bus_stop[id];
  }

  get busStops(): Record<ID, BusStop<S>> {
    return this.data.bus.bus_stop;
  }

  get(category: string, id: ID): Category<S> | undefined {
    switch (category) {
      case "flight":
        return this.airFlight(id);
      case "airport":
        return this.airAirport(id);
      case "gate":
        return this.airGate(id);
      case "airline":
        return this.airAirline(id);
      case "railcompany":
        return this.railCompany(id);
      case "railline":
        return this.railLine(id);
      case "station":
        return this.railStation(id);
      case "seacompany":
        return this.seaCompany(id);
      case "sealine":
        return this.seaLine(id);
      case "seastop":
        return this.seaStop(id);
      case "buscompany":
        return this.busCompany(id);
      case "busline":
        return this.busLine(id);
      case "busstop":
        return this.busStop(id);
      default:
        throw Error(`Unknown category ${category}`);
    }
  }
}
