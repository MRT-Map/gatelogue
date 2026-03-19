import { Node } from "./node.js";
import { LocatedNode } from "./located.js";
import type { GD } from "./lib.js";

export type AirMode =
  | "helicopter"
  | "seaplane"
  | "warp plane"
  | "traincarts plane";

export class AirAirline extends Node {
  get name(): string {
    return this.getColumn("AirAirline", "name");
  }
  get link(): string | null {
    return this.getColumn("AirAirline", "link");
  }

  get flights(): AirFlight[] {
    return this.getDerived(AirFlight, "air/airline_flights");
  }
  get gates(): AirGate[] {
    return this.getDerived(AirGate, "air/airline_gates");
  }
  get airports(): AirAirport[] {
    return this.getDerived(AirAirport, "air/airline_airports");
  }
}

export class AirAirport extends LocatedNode {
  get code(): string {
    return this.getColumn("AirAirport", "code");
  }
  get names(): string[] {
    return this.getSet("AirAirportNames", "name");
  }
  get link(): string | null {
    return this.getColumn("AirAirport", "link");
  }
  get modes(): AirMode[] {
    return this.getSet("AirAirportModes", "mode");
  }

  get gates(): AirGate[] {
    return this.getDerived(AirGate, "air/airport_gates");
  }
}

export class AirGate extends Node {
  get code(): string | null {
    return this.getColumn("AirGate", "code");
  }
  get airport(): AirAirport {
    return this.getColumnFK("AirGate", "airport", AirAirport)!;
  }
  get airline(): AirAirline | null {
    return this.getColumnFK("AirGate", "airline", AirAirline);
  }
  get width(): number | null {
    return this.getColumn("AirGate", "width");
  }
  get mode(): string | null {
    return this.getColumn("AirGate", "mode");
  }

  get flightsFromHere(): AirFlight[] {
    return this.getDerived(AirFlight, "air/gate_flights_from_here");
  }

  get flightsToHere(): AirFlight[] {
    return this.getDerived(AirFlight, "air/gate_flights_to_here");
  }
}

export class AirFlight extends Node {
  get airline(): AirAirline {
    return this.getColumnFK("AirFlight", "airline", AirAirline)!;
  }
  get code(): string {
    return this.getColumn("AirFlight", "code");
  }
  get from(): AirGate {
    return this.getColumnFK("AirFlight", "from", AirGate)!;
  }
  get to(): AirGate {
    return this.getColumnFK("AirFlight", "to", AirGate)!;
  }
  get aircraft(): Aircraft | null {
    const name = this.getColumn<string | null>("AirFlight", "aircraft");
    if (name === null) {
      return null;
    }
    return new Aircraft(name, this.gd);
  }
}

export class Aircraft {
  constructor(
    readonly name: string,
    protected readonly gd: GD,
  ) {}

  get manufacturer(): string {
    return this.gd.execGetOne<[string]>(
      `SELECT manufacturer FROM Aircraft WHERE name = ?`,
      [this.name],
    )[0]!;
  }

  get width(): number {
    return this.gd.execGetOne<[number]>(
      `SELECT width FROM Aircraft WHERE name = ?`,
      [this.name],
    )[0]!;
  }

  get height(): number {
    return this.gd.execGetOne<[number]>(
      `SELECT height FROM Aircraft WHERE name = ?`,
      [this.name],
    )[0]!;
  }

  get length(): number {
    return this.gd.execGetOne<[number]>(
      `SELECT length FROM Aircraft WHERE name = ?`,
      [this.name],
    )[0]!;
  }

  get mode(): AirMode {
    return this.gd.execGetOne<[AirMode]>(
      `SELECT mode FROM Aircraft WHERE name = ?`,
      [this.name],
    )[0]!;
  }
}
