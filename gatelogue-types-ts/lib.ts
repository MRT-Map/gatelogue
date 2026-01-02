/**
 * # Usage
 * The data can be imported into your JavaScript/TypeScript project with classes and type definitions.
 * * retrieving from npmjs.com:
 *   * npm: `npm i gatelogue-types`
 *   * yarn: `yarn add gatelogue-types`
 *   * pnpm: `pnpm add gatelogue-types`
 *   * denoL `deno add npm:gatelogue-types`
 *   * bun: `bun add gatelogue-types`
 * * retrieving from jsr.io:
 *   * npm: `npx jsr add @mrt-map/gatelogue-types`
 *   * yarn: `yarn add jsr:@mrt-map/gatelogue-types`
 *   * pnpm: `pnpm i jsr:@mrt-map/gatelogue-types`
 *   * deno: `deno add jsr:@mrt-map/gatelogue-types`
 *   * bun: `bunx jsr add @mrt-map/gatelogue-types`
 *
 * To import directly from the repository:
 * * npm: `npm i 'https://gitpkg.vercel.app/mrt-map/gatelogue/gatelogue-types-ts?main'`
 * * yarn: `yarn add 'https://gitpkg.vercel.app/mrt-map/gatelogue/gatelogue-types-ts?main'`
 * * pnpm: `pnpm add mrt-map/gatelogue#path:/gatelogue-types-ts`
 * * bun: `bun add 'git+https://gitpkg.vercel.app/mrt-map/gatelogue/gatelogue-types-ts?main'`
 *
 * To retrieve the data:
 * @example
 * ```ts
 * import { GD } from "gatelogue-types";
 * await GD.get() // retrieve data, with sources
 * await GD.getNoSources() // retrieve data, no sources
 * ```
 *
 * @packageDocumentation
 */

/* eslint-disable @typescript-eslint/no-unused-vars */

export type StringID<_ extends Node> = string;
export type IntID<_ extends Node> = number;
export type ID<T extends Node> = StringID<T> | IntID<T>
export type World = "Old" | "New" | "Space";
export type RailMode = "warp" | "cart" | "traincarts" | "vehicles";
export type SeaMode = "ferry" | "cruise";
export type PlaneMode =
  | "helicopter"
  | "seaplane"
  | "warp plane"
  | "traincarts plane";
export type WarpType = "premier" | "terminus" | "portal" | "misc";
export type Rank =
  | "Unranked"
  | "Councillor"
  | "Mayor"
  | "Senator"
  | "Governor"
  | "Premier"
  | "Community";

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
  coordinates: Sourced<[number, number], S> | null;
  proximity: Record<
    StringID<Located>,
    Sourced<{ distance: number; explicit: boolean }, S>
  >;
  shared_facility: Sourced<IntID<Located>, S>[];
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
  names: Sourced<string[], S> | null;
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
  local: boolean;
}

export interface RailLine<S extends boolean = true> extends Node {
  code: string;
  mode: Sourced<RailMode, S> | null;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
  company: Sourced<IntID<RailCompany<S>>, S>;
  stations: Sourced<IntID<RailStation<S>>, S>[];
}

export interface RailStation<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<IntID<RailCompany<S>>, S>;
  connections: Record<
    StringID<RailStation<S>>,
    Sourced<Connection<RailLine, RailStation, S>, S>[]
  >;
}

export interface SeaCompany<S extends boolean = true> extends Node {
  name: string;
  lines: Sourced<IntID<SeaLine<S>>, S>[];
  stops: Sourced<IntID<SeaStop<S>>, S>[];
  local: boolean;
}

export interface SeaLine<S extends boolean = true> extends Node {
  code: string;
  mode: Sourced<SeaMode, S> | null;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
  company: Sourced<IntID<SeaCompany<S>>, S>;
  stops: Sourced<IntID<SeaStop<S>>, S>[];
}

export interface SeaStop<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<IntID<SeaCompany<S>>, S>;
  connections: Record<
    StringID<SeaStop<S>>,
    Sourced<Connection<SeaLine, SeaStop, S>, S>[]
  >;
}

export interface BusCompany<S extends boolean = true> extends Node {
  name: string;
  lines: Sourced<IntID<BusLine<S>>, S>[];
  stops: Sourced<IntID<BusStop<S>>, S>[];
  local: boolean;
}

export interface BusLine<S extends boolean = true> extends Node {
  code: string;
  name: Sourced<string, S> | null;
  colour: Sourced<string, S> | null;
  company: Sourced<IntID<BusCompany<S>>, S>;
  stops: Sourced<IntID<BusStop<S>>, S>[];
}

export interface BusStop<S extends boolean = true> extends Located<S> {
  codes: string[];
  name: Sourced<string, S> | null;
  company: Sourced<IntID<BusCompany<S>>, S>;
  connections: Record<
    StringID<BusStop<S>>,
    Sourced<Connection<BusLine, BusStop, S>, S>[]
  >;
}

export interface SpawnWarp<S extends boolean = true> extends Located<S> {
  name: string;
  warp_type: WarpType;
}

export interface Town<S extends boolean = true> extends Located<S> {
  name: string;
  rank: Sourced<Rank, S>;
  mayor: Sourced<string, S>;
  deputy_mayor: Sourced<string | null, S>;
}

export interface GatelogueData {
  version: number;
  timestamp: string;
  nodes: Record<StringID<Node>, Node>;
}

// noinspection JSUnusedGlobalSymbols
export class GD<S extends boolean = true> {
  data: GatelogueData;

  constructor(data: GatelogueData) {
    this.data = data;
  }

  static async get(): Promise<GD> {
    return new GD(
      await fetch(
        "https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data.json",
      ).then((res) => res.json()),
    );
  }

  static async getNoSources(): Promise<GD<false>> {
    return new GD(
      await fetch(
        "https://raw.githubusercontent.com/MRT-Map/gatelogue/dist/data_no_sources.json",
      ).then((res) => res.json()),
    );
  }

  node(id: ID<Node>): Node | undefined {
    return this.data.nodes[typeof id === "string" ? id : id.toString()] as never;
  }
  get nodes(): Node[] {
    return Object.values(this.data.nodes);
  }

  airFlight(id: ID<AirFlight<S>>): AirFlight<S> | undefined {
    return this.node(id) as never;
  }
  get airFlights(): AirFlight<S>[] {
    return this.nodes.filter((a) => a.type === "AirFlight") as never;
  }

  airAirport(id: ID<AirAirport<S>>): AirAirport<S> | undefined {
    return this.node(id) as never;
  }
  get airAirports(): AirAirport<S>[] {
    return this.nodes.filter((a) => a.type === "AirAirport") as never;
  }

  airGate(id: ID<AirGate<S>>): AirGate<S> | undefined {
    return this.node(id) as never;
  }
  get airGates(): AirGate<S>[] {
    return this.nodes.filter((a) => a.type === "AirGate") as never;
  }

  airAirline(id: ID<AirAirline<S>>): AirAirline<S> | undefined {
    return this.node(id) as never;
  }
  get airAirlines(): AirAirline<S>[] {
    return this.nodes.filter((a) => a.type === "AirAirline") as never;
  }

  railCompany(id: ID<RailCompany<S>>): RailCompany<S> | undefined {
    return this.node(id) as never;
  }
  get railCompanies(): RailCompany<S>[] {
    return this.nodes.filter((a) => a.type === "RailCompany") as never;
  }

  railLine(id: ID<RailLine<S>>): RailLine<S> | undefined {
    return this.node(id) as never;
  }
  get railLines(): RailLine<S>[] {
    return this.nodes.filter((a) => a.type === "RailLine") as never;
  }

  railStation(id: ID<RailStation<S>>): RailStation<S> | undefined {
    return this.node(id) as never;
  }
  get railStations(): RailStation<S>[] {
    return this.nodes.filter((a) => a.type === "RailStation") as never;
  }

  seaCompany(id: ID<SeaCompany<S>>): SeaCompany<S> | undefined {
    return this.node(id) as never;
  }
  get seaCompanies(): SeaCompany<S>[] {
    return this.nodes.filter((a) => a.type === "SeaCompany") as never;
  }

  seaLine(id: ID<SeaLine<S>>): SeaLine<S> | undefined {
    return this.node(id) as never;
  }
  get seaLines(): SeaLine<S>[] {
    return this.nodes.filter((a) => a.type === "SeaLine") as never;
  }

  seaStop(id: ID<SeaStop<S>>): SeaStop<S> | undefined {
    return this.node(id) as never;
  }
  get seaStops(): SeaStop<S>[] {
    return this.nodes.filter((a) => a.type === "SeaStop") as never;
  }

  busCompany(id: ID<BusCompany<S>>): BusCompany<S> | undefined {
    return this.node(id) as never;
  }
  get busCompanies(): BusCompany<S>[] {
    return this.nodes.filter((a) => a.type === "BusCompany") as never;
  }

  busLine(id: ID<BusLine<S>>): BusLine<S> | undefined {
    return this.node(id) as never;
  }
  get busLines(): BusLine<S>[] {
    return this.nodes.filter((a) => a.type === "BusLine") as never;
  }

  busStop(id: ID<BusStop<S>>): BusStop<S> | undefined {
    return this.node(id) as never;
  }
  get busStops(): BusStop<S>[] {
    return this.nodes.filter((a) => a.type === "BusStop") as never;
  }

  spawnWarp(id: ID<SpawnWarp<S>>): SpawnWarp<S> | undefined {
    return this.node(id) as never;
  }
  get spawnWarps(): SpawnWarp<S>[] {
    return this.nodes.filter((a) => a.type === "SpawnWarp") as never;
  }

  town(id: ID<Town<S>>): Town<S> | undefined {
    return this.node(id) as never;
  }
  get towns(): Town<S>[] {
    return this.nodes.filter((a) => a.type === "Town") as never;
  }
}
