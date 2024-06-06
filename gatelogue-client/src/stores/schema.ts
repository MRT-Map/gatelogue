type ID = string;
type World = "Old" | "New";

export interface Sourced<T> {
  v: T;
  s: string[];
}

export interface Flight {
  codes: string[];
  gates: Sourced<ID>[];
  airline: Sourced<ID>;
}

export interface Airport {
  code: string;
  name: Sourced<string> | null;
  world: Sourced<World> | null;
  coordinates: Sourced<[number, number]> | null;
  link: Sourced<string> | null;
  gates: Sourced<ID>[];
  proximity: Record<ID, string>;
}

export interface Gate {
  code: string | null;
  flights: Sourced<ID>[];
  airport: Sourced<ID>;
  airline: Sourced<ID> | null;
  size: Sourced<string> | null;
}

export interface Airline {
  name: string;
  flights: Sourced<ID>[];
  link: Sourced<string> | null;
}

export interface AirData {
  flight: Record<ID, Flight>;
  airport: Record<ID, Airport>;
  gate: Record<ID, Gate>;
  airline: Record<ID, Airline>;
}

export interface RailCompany {
  name: string;
  lines: Sourced<ID>[];
  stations: Sourced<ID>[];
}

export interface RailLine {
  code: string;
  company: Sourced<ID>;
  ref_station: Sourced<ID>;
  mode: Sourced<"warp" | "cart" | "traincart" | "vehicles"> | null;
  name: Sourced<string> | null;
  colour: Sourced<string> | null;
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

export interface Station {
  codes: string[];
  name: Sourced<string> | null;
  world: Sourced<World> | null;
  coordinates: Sourced<[number, number]> | null;
  company: Sourced<ID>;
  connections: Record<ID, Sourced<RailConnection>[]>;
  proximity: Record<ID, string>;
}

export interface RailData {
  rail_company: Record<ID, RailCompany>;
  rail_line: Record<ID, RailLine>;
  station: Record<ID, Station>;
}

export interface GatelogueData {
  version: 1;
  timestamp: string;
  air: AirData;
  rail: RailData;
}
