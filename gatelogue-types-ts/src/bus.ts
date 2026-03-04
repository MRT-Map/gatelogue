import { Node } from "./node.js";
import { LocatedNode } from "./located.js";

export type BusMode = "warp" | "traincarts";

export class BusCompany extends Node {
  get name(): string {
    return this.getColumn("BusCompany", "name");
  }
  get link(): string | null {
    return this.getColumn("BusCompany", "link");
  }

  get lines(): BusLine[] {
    return this.gd
      .execGetMany<
        [number]
      >("SELECT i FROM BusLine WHERE company = ?", [this.i])
      .map(([i]) => new BusLine(i, this.gd));
  }
  get stops(): BusStop[] {
    return this.gd
      .execGetMany<
        [number]
      >("SELECT i FROM BusStop WHERE company = ?", [this.i])
      .map(([i]) => new BusStop(i, this.gd));
  }
  get berths(): BusBerth[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT BusBerth.i 
      FROM (SELECT i FROM BusStop WHERE company = ?) A 
      INNER JOIN BusBerth on A.i = BusBerth.stop`,
        [this.i],
      )
      .map(([i]) => new BusBerth(i, this.gd));
  }
}

export class BusLine extends Node {
  get code(): string {
    return this.getColumn("BusLine", "code");
  }
  get company(): BusCompany {
    return new BusCompany(this.getColumn("BusLine", "company"), this.gd);
  }
  get name(): string | null {
    return this.getColumn("BusLine", "name");
  }
  get colour(): string | null {
    return this.getColumn("BusLine", "colour");
  }
  get mode(): BusMode | null {
    return this.getColumn("BusLine", "name");
  }
  get local(): boolean | null {
    const result = this.getColumn<number>("BusLine", "name");
    return result === null ? null : result === 1;
  }

  get berths(): BusBerth[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT BusBerth.i 
      FROM (SELECT "from", "to" FROM BusConnection WHERE line = ?) A 
      LEFT JOIN BusBerth ON A."from" = BusBerth.i OR A."to" = BusBerth.i`,
        [this.i],
      )
      .map(([i]) => new BusBerth(i, this.gd));
  }
  get stops(): BusStop[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT BusBerth.stop 
      FROM (SELECT "from", "to" FROM BusConnection WHERE line = ?) A 
      LEFT JOIN BusBerth ON A."from" = BusBerth.i OR A."to" = BusBerth.i`,
        [this.i],
      )
      .map(([i]) => new BusStop(i, this.gd));
  }
}

export class BusStop extends LocatedNode {
  get codes(): string[] {
    return this.getSet("BusStopCodes", "code");
  }
  get company(): BusCompany {
    return new BusCompany(this.getColumn("BusStop", "company"), this.gd);
  }
  get name(): string | null {
    return this.getColumn("BusStop", "name");
  }

  get berths(): BusBerth[] {
    return this.gd
      .execGetMany<[number]>("SELECT i FROM BusBerth WHERE stop = ?", [this.i])
      .map(([i]) => new BusBerth(i, this.gd));
  }
  get connectionsFromHere(): BusConnection[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT BusConnection.i 
      FROM (SELECT i FROM BusBerth WHERE stop = ?) A 
      INNER JOIN BusConnection ON A.i = BusConnection."from"`,
        [this.i],
      )
      .map(([i]) => new BusConnection(i, this.gd));
  }
  get connectionsToHere(): BusConnection[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT BusConnection.i
                                  FROM (SELECT i FROM BusBerth WHERE stop = ?) A
                                           INNER JOIN BusConnection ON A.i = BusConnection."to"`,
        [this.i],
      )
      .map(([i]) => new BusConnection(i, this.gd));
  }
  get lines(): BusLine[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT BusConnection.line 
      FROM (SELECT i FROM BusBerth WHERE stop = ?) A 
      LEFT JOIN BusConnection ON A.i = BusConnection."from" OR A.i = BusConnection."to"`,
        [this.i],
      )
      .map(([i]) => new BusLine(i, this.gd));
  }
}

export class BusBerth extends Node {
  get code(): string | null {
    return this.getColumn("BusBerth", "code");
  }
  get stop(): BusStop {
    return new BusStop(this.getColumn("BusBerth", "code"), this.gd);
  }

  get connectionsFromHere(): BusConnection[] {
    return this.gd
      .execGetMany<
        [number]
      >('SELECT BusConnection.i FROM BusConnection WHERE BusConnection."from" = ?', [this.i])
      .map(([i]) => new BusConnection(i, this.gd));
  }
  get connectionsToHere(): BusConnection[] {
    return this.gd
      .execGetMany<
        [number]
      >('SELECT BusConnection.i FROM BusConnection WHERE BusConnection."to" = ?', [this.i])
      .map(([i]) => new BusConnection(i, this.gd));
  }
  get lines(): BusLine[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT BusConnection.line FROM BusConnection 
      WHERE BusConnection."from" = ? OR BusConnection."to" = ?`,
        [this.i],
      )
      .map(([i]) => new BusLine(i, this.gd));
  }
}

export class BusConnection extends Node {
  get line(): BusLine {
    return new BusLine(this.getColumn("BusConnection", "line"), this.gd);
  }
  get from(): BusBerth {
    return new BusBerth(this.getColumn("BusConnection", "from"), this.gd);
  }
  get to(): BusBerth {
    return new BusBerth(this.getColumn("BusConnection", "to"), this.gd);
  }
  get direction(): string | null {
    return this.getColumn("BusConnection", "direction");
  }
  get duration(): number | null {
    return this.getColumn("BusConnection", "duration");
  }
}
