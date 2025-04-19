export type StringID<_ extends Node> = string;
export type IntID<_ extends Node> = number;
export type World = "Old" | "New" | "Space";
export type RailMode = "warp" | "cart" | "traincarts" | "vehicles";
export type SeaMode = "ferry" | "cruise";
export type PlaneMode = "helicopter" | "seaplane" | "warp plane" | "traincarts plane";
export type Sourced<T, S extends boolean = true> = S extends true ? {
    v: T;
    s: string[];
} : T;
export interface Node {
    i: IntID<Node>;
    source: string[];
    type: string;
}
export interface Located<S extends boolean = true> extends Node {
    world: Sourced<World, S> | null;
    coordinates: Sourced<[number, number]> | null;
    proximity: Record<StringID<Located>, Sourced<{
        distance: number;
        explicit: boolean;
    }>>;
    shared_facility: Sourced<IntID<Located>>[];
}
export interface Direction<St extends Located, S extends boolean = true> {
    direction: IntID<St>;
    forward_label: string | null;
    backward_label: string | null;
    one_way: boolean | Sourced<boolean, S>;
}
export interface Connection<L extends Node, St extends Located, S extends boolean = true> {
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
    local: boolean;
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
    connections: Record<StringID<RailStation<S>>, Sourced<Connection<RailLine, RailStation, S>>[]>;
}
export interface SeaCompany<S extends boolean = true> extends Node {
    name: string;
    lines: Sourced<IntID<SeaLine<S>>, S>[];
    stations: Sourced<IntID<SeaStop<S>>, S>[];
    local: boolean;
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
    connections: Record<StringID<SeaStop<S>>, Sourced<Connection<SeaLine, SeaStop, S>>[]>;
}
export interface BusCompany<S extends boolean = true> extends Node {
    name: string;
    lines: Sourced<IntID<BusLine<S>>, S>[];
    stations: Sourced<IntID<BusStop<S>>, S>[];
    local: boolean;
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
    connections: Record<StringID<BusStop<S>>, Sourced<Connection<BusLine, BusStop, S>>[]>;
}
export interface GatelogueData {
    version: number;
    timestamp: string;
    nodes: Record<StringID<Node>, Node>;
}
export declare class GD<S extends boolean = true> {
    data: GatelogueData;
    constructor(data: GatelogueData);
    static get(): Promise<GD>;
    static getNoSources(): Promise<GD<false>>;
    node(id: StringID<Node>): Node | undefined;
    get nodes(): Node[];
    airFlight(id: StringID<AirFlight<S>>): AirFlight<S> | undefined;
    get airFlights(): AirFlight<S>[];
    airAirport(id: StringID<AirAirport<S>>): AirAirport<S> | undefined;
    get airAirports(): AirAirport<S>[];
    airGate(id: StringID<AirGate<S>>): AirGate<S> | undefined;
    get airGates(): AirGate<S>[];
    airAirline(id: StringID<AirAirline<S>>): AirAirline<S> | undefined;
    get airAirlines(): AirAirline<S>[];
    railCompany(id: StringID<RailCompany<S>>): RailCompany<S> | undefined;
    get railCompanies(): RailCompany<S>[];
    railLine(id: StringID<RailLine<S>>): RailLine<S> | undefined;
    get railLines(): RailLine<S>[];
    railStation(id: StringID<RailStation<S>>): RailStation<S> | undefined;
    get railStations(): RailStation<S>[];
    seaCompany(id: StringID<SeaCompany<S>>): SeaCompany<S> | undefined;
    get seaCompanies(): SeaCompany<S>[];
    seaLine(id: StringID<SeaLine<S>>): SeaLine<S> | undefined;
    get seaLines(): SeaLine<S>[];
    seaStop(id: StringID<SeaStop<S>>): SeaStop<S> | undefined;
    get seaStops(): SeaStop<S>[];
    busCompany(id: StringID<BusCompany<S>>): BusCompany<S> | undefined;
    get busCompanies(): BusCompany<S>[];
    busLine(id: StringID<BusLine<S>>): BusLine<S> | undefined;
    get busLines(): BusLine<S>[];
    busStop(id: StringID<BusStop<S>>): BusStop<S> | undefined;
    get busStops(): BusStop<S>[];
}
//# sourceMappingURL=lib.d.ts.map