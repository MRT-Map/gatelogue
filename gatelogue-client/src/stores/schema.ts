type ID = string;
type World = "Old" | "New";
type RailMode = "warp" | "cart" | "traincart" | "vehicles";

type Sourced<T, S extends boolean = true> = S extends true
  ? { v: T; s: string[] }
  : T;

export interface Flight<S extends boolean = true> {
  codes: string[];
  gates: Sourced<ID, S>[];
  airline: Sourced<ID, S>;
}

export interface Airport<S extends boolean = true> {
  code: string;
  name: Sourced<string, S> | null;
  world: Sourced<World, S> | null;
  coordinates: Sourced<[number, number]> | null;
  link: Sourced<string, S> | null;
  gates: Sourced<ID, S>[];
  proximity: Record<ID, string>;
}

export interface Gate<S extends boolean = true> {
  code: string | null;
  flights: Sourced<ID, S>[];
  airport: Sourced<ID, S>;
  airline: Sourced<ID, S> | null;
  size: Sourced<string, S> | null;
}

export interface Airline<S extends boolean = true> {
  name: string;
  flights: Sourced<ID, S>[];
  link: Sourced<string, S> | null;
}

export interface AirData<S extends boolean = true> {
  flight: Record<ID, Flight<S>>;
  airport: Record<ID, Airport<S>>;
  gate: Record<ID, Gate<S>>;
  airline: Record<ID, Airline<S>>;
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

export interface Direction {
  forward_towards_code: ID;
  forward_direction_label: string | null;
  backward_direction_label: string | null;
  one_way: boolean;
}

export interface RailConnection {
  line: ID;
  direction: Direction | null;
}

export interface Station<S extends boolean = true> {
  codes: string[];
  name: Sourced<string, S> | null;
  world: Sourced<World, S> | null;
  coordinates: Sourced<[number, number], S> | null;
  company: Sourced<ID, S>;
  connections: Record<ID, Sourced<RailConnection>[]>;
  proximity: Record<ID, string>;
}

export interface RailData<S extends boolean = true> {
  rail_company: Record<ID, RailCompany<S>>;
  rail_line: Record<ID, RailLine<S>>;
  station: Record<ID, Station<S>>;
}

export interface GatelogueData<S extends boolean = true> {
  version: 1;
  timestamp: string;
  air: AirData<S>;
  rail: RailData<S>;
}
