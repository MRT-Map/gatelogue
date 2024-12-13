/* eslint-disable max-lines */
export type StringID<_ extends Node> = string;
export type IntID<_ extends Node> = number;
export type World = "Old" | "New" | "Space";
export type RailMode = "warp" | "cart" | "traincart" | "vehicles";
export type SeaMode = "ferry" | "cruise";
export type PlaneMode =
  | "helicopter"
  | "seaplane"
  | "warp plane"
  | "traincarts plane";

export type Sourced<T, S extends boolean = true> = S extends true
  ? { v: T; s: string[] }
  : T;

export interface Node {
  i: IntID<Node>;
  source: string[];
  type: string;
}

export interface Located<S extends boolean = true> extends Node {
  world: Sourced<World, S> | null;
  coordinates: Sourced<[number, number]> | null;
  proximity: Record<StringID<Located>, Sourced<{ distance: number }>>;
  shared_facility: Sourced<IntID<Located>>[];
}

export interface Direction<St extends Located, S extends boolean = true> {
  direction: IntID<St>;
  forward_label: string | null;
  backward_label: string | null;
  one_way: boolean | Sourced<boolean, S>;
}

export interface Connection<
  L extends Node,
  St extends Located,
  S extends boolean = true,
> {
  line: IntID<L>;
  direction: Direction<St, S> | null;
}

export interface AirFlight<S extends boolean = true> extends Node {
  codes: string[];
  mode: Sourced<PlaneMode, S> | null;
  gates: Sourced<IntID<AirGate<S>>, S>[];
  airline: Sourced<IntID<AirAirline<S>>, S>;
}

export interface AirAirport<S extends boolean = true> extends Located {
  code: string;
  name: Sourced<string, S> | null;
  link: Sourced<string, S> | null;
  gates: Sourced<IntID<AirGate<S>>, S>[];
}

export interface AirGate<S extends boolean = true> extends Node {
  code: string | null;
  size: Sourced<string, S> | null;
  flights: Sourced<IntID<AirFlight<S>>, S>[];
  airport: Sourced<IntID<AirAirport<S>>, S>;
  airline: Sourced<IntID<AirAirline<S>>, S> | null;
}

export interface AirAirline<S extends boolean = true> extends Node {
  name: string;
  link: Sourced<string, S> | null;
  flights: Sourced<IntID<AirFlight<S>>, S>[];
  gates: Sourced<IntID<AirGate<S>>, S>[];
}

export interface RailCompany<S extends boolean = true> extends Node {
  name: string;
  lines: Sourced<IntID<RailLine<S>>, S>[];
  stations: Sourced<IntID<RailStation<S>>, S>[];
}

export interface RailLine<S extends boolean = true> extends Node {
  code: string;
  mode: Sourced<RailMode, S> | null;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
  company: Sourced<IntID<RailCompany<S>>, S>;
  ref_station: Sourced<IntID<RailStation<S>>, S>;
}

export interface RailStation<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<IntID<RailCompany<S>>, S>;
  connections: Record<
    StringID<RailStation<S>>,
    Sourced<Connection<RailLine, RailStation, S>>[]
  >;
}

export interface SeaCompany<S extends boolean = true> extends Node {
  name: string;
  lines: Sourced<IntID<SeaLine<S>>, S>[];
  stations: Sourced<IntID<SeaStop<S>>, S>[];
}

export interface SeaLine<S extends boolean = true> extends Node {
  code: string;
  mode: Sourced<SeaMode, S> | null;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
  company: Sourced<IntID<SeaCompany<S>>, S>;
  ref_stop: Sourced<IntID<SeaStop<S>>, S>;
}

export interface SeaStop<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<IntID<SeaCompany<S>>, S>;
  connections: Record<
    StringID<SeaStop<S>>,
    Sourced<Connection<SeaLine, SeaStop, S>>[]
  >;
}

export interface BusCompany<S extends boolean = true> extends Node {
  name: string;
  lines: Sourced<IntID<BusLine<S>>, S>[];
  stations: Sourced<IntID<BusStop<S>>, S>[];
}

export interface BusLine<S extends boolean = true> extends Node {
  code: string;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
  company: Sourced<IntID<BusCompany<S>>, S>;
  ref_stop: Sourced<IntID<BusStop<S>>, S>;
}

export interface BusStop<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<IntID<BusCompany<S>>, S>;
  connections: Record<
    StringID<BusStop<S>>,
    Sourced<Connection<BusLine, BusStop, S>>[]
  >;
}

export interface GatelogueData {
  version: 1;
  timestamp: string;
  nodes: Record<StringID<Node>, Node>;
}

export class GD<S extends boolean = true> {
  data: GatelogueData;

  constructor(data: GatelogueData) {
    this.data = data;
  }

  airFlight(id: StringID<AirFlight<S>>): AirFlight<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get airFlights(): AirFlight<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "AirFlight",
    ) as any;
  }

  airAirport(id: StringID<AirAirport<S>>): AirAirport<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get airAirports(): AirAirport<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "AirAirport",
    ) as any;
  }

  airGate(id: StringID<AirGate<S>>): AirGate<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get airGates(): AirGate<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "AirGate",
    ) as any;
  }

  airAirline(id: StringID<AirAirline<S>>): AirAirline<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get airAirlines(): AirAirline<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "AirAirline",
    ) as any;
  }

  railCompany(id: StringID<RailCompany<S>>): RailCompany<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get railCompanies(): RailCompany<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "RailCompany",
    ) as any;
  }

  railLine(id: StringID<RailLine<S>>): RailLine<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get railLines(): RailLine<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "RailLine",
    ) as any;
  }

  railStation(id: StringID<RailStation<S>>): RailStation<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get railStations(): RailStation<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "RailStation",
    ) as any;
  }

  seaCompany(id: StringID<SeaCompany<S>>): SeaCompany<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get seaCompanies(): SeaCompany<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "SeaCompany",
    ) as any;
  }

  seaLine(id: StringID<SeaLine<S>>): SeaLine<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get seaLines(): SeaLine<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "SeaLine",
    ) as any;
  }

  seaStop(id: StringID<SeaStop<S>>): SeaStop<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get seaStops(): SeaStop<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "SeaStop",
    ) as any;
  }

  busCompany(id: StringID<BusCompany<S>>): BusCompany<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get busCompanies(): BusCompany<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "BusCompany",
    ) as any;
  }

  busLine(id: StringID<BusLine<S>>): BusLine<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get busLines(): BusLine<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "BusLine",
    ) as any;
  }

  busStop(id: StringID<BusStop<S>>): BusStop<S> | undefined {
    return this.data.nodes[id] as any;
  }
  get busStops(): BusStop<S>[] {
    return Object.values(this.data.nodes).filter(
      (a) => a.type == "BusStop",
    ) as any;
  }
}
