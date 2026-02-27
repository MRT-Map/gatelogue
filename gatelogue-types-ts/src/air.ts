import { Node } from "./node.js";
import { LocatedNode } from "./located.js";

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
    return this.gd
      .execGetMany<
        [number]
      >("SELECT i FROM AirFlight WHERE airline = ?", [this.i])
      .map(([i]) => new AirFlight(i, this.gd));
  }
  get gates(): AirGate[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT i FROM AirGate WHERE airline = ? 
      UNION SELECT "from" AS i FROM AirFlight WHERE airline = ? 
      UNION SELECT "to" AS i FROM AirFlight WHERE airline = ?`,
        [this.i],
      )
      .map(([i]) => new AirGate(i, this.gd));
  }
  get airports(): AirAirport[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT airport FROM AirGate WHERE airline = ? 
      UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = "from" WHERE AirFlight.airline = ? 
      UNION SELECT DISTINCT airport FROM AirFlight LEFT JOIN AirGate on AirGate.i = "to" WHERE AirFlight.airline = ?`,
      )
      .map(([i]) => new AirAirport(i, this.gd));
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
    return this.gd
      .execGetMany<
        [number]
      >("SELECT i FROM AirGate WHERE airport = ?", [this.i])
      .map(([i]) => new AirGate(i, this.gd));
  }
}

export class AirGate extends Node {
  get code(): string | null {
    return this.getColumn("AirGate", "code");
  }
  get airport(): AirAirport {
    return new AirAirport(this.getColumn("AirGate", "airport"), this.gd);
  }
  get airline(): AirAirline | null {
    const id = this.getColumn<number | null>("AirGate", "airline");
    return id === null ? null : new AirAirline(id, this.gd);
  }
  get size(): string | null {
    return this.getColumn("AirGate", "size");
  }
  get mode(): string | null {
    return this.getColumn("AirGate", "mode");
  }

  get flightsFromHere(): AirFlight[] {
    return this.gd
      .execGetMany<
        [number]
      >('SELECT i FROM AirFlight WHERE "from" = ?', [this.i])
      .map(([i]) => new AirFlight(i, this.gd));
  }

  get flightsToHere(): AirFlight[] {
    return this.gd
      .execGetMany<[number]>('SELECT i FROM AirFlight WHERE "to" = ?', [this.i])
      .map(([i]) => new AirFlight(i, this.gd));
  }
}

export class AirFlight extends Node {
  get airline(): AirAirline {
    return new AirAirline(this.getColumn("AirFlight", "airline"), this.gd);
  }
  get code(): string {
    return this.getColumn("AirFlight", "code");
  }
  get from(): AirGate {
    return new AirGate(this.getColumn("AirFlight", "from"), this.gd);
  }
  get to(): AirGate {
    return new AirGate(this.getColumn("AirFlight", "to"), this.gd);
  }
  get mode(): string | null {
    return this.getColumn("AirFlight", "mode");
  }
}
