import { Node } from "./node.js";
import { LocatedNode } from "./located.js";

export type RailMode = "warp" | "cart" | "traincarts" | "vehicle";

export class RailCompany extends Node {
  get name(): string {
    return this.getColumn("RailCompany", "name");
  }
  get link(): string | null {
    return this.getColumn("RailCompany", "link");
  }

  get lines(): RailLine[] {
    return this.gd
      .execGetMany<
        [number]
      >("SELECT i FROM RailLine WHERE company = ?", [this.i])
      .map(([i]) => new RailLine(i, this.gd));
  }
  get stations(): RailStation[] {
    return this.gd
      .execGetMany<
        [number]
      >("SELECT i FROM RailStation WHERE company = ?", [this.i])
      .map(([i]) => new RailStation(i, this.gd));
  }
  get platforms(): RailPlatform[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT RailPlatform.i 
      FROM (SELECT i FROM RailStation WHERE company = ?) A 
      INNER JOIN RailPlatform on A.i = RailPlatform.station`,
        [this.i],
      )
      .map(([i]) => new RailPlatform(i, this.gd));
  }
}

export class RailLine extends Node {
  get code(): string {
    return this.getColumn("RailLine", "code");
  }
  get company(): RailCompany {
    return new RailCompany(this.getColumn("RailLine", "company"), this.gd);
  }
  get name(): string | null {
    return this.getColumn("RailLine", "name");
  }
  get colour(): string | null {
    return this.getColumn("RailLine", "colour");
  }
  get mode(): RailMode | null {
    return this.getColumn("RailLine", "name");
  }
  get local(): boolean | null {
    const result = this.getColumn<number>("RailLine", "name");
    return result === null ? null : result === 1;
  }

  get platforms(): RailPlatform[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT RailPlatform.i 
      FROM (SELECT "from", "to" FROM RailConnection WHERE line = ?) A 
      LEFT JOIN RailPlatform ON A."from" = RailPlatform.i OR A."to" = RailPlatform.i`,
        [this.i],
      )
      .map(([i]) => new RailPlatform(i, this.gd));
  }
  get stations(): RailStation[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT RailPlatform.station 
      FROM (SELECT "from", "to" FROM RailConnection WHERE line = ?) A 
      LEFT JOIN RailPlatform ON A."from" = RailPlatform.i OR A."to" = RailPlatform.i`,
        [this.i],
      )
      .map(([i]) => new RailStation(i, this.gd));
  }
}

export class RailStation extends LocatedNode {
  get codes(): string[] {
    return this.getSet("RailStationCodes", "code");
  }
  get company(): RailCompany {
    return new RailCompany(this.getColumn("RailStation", "company"), this.gd);
  }
  get name(): string | null {
    return this.getColumn("RailStation", "name");
  }

  get platforms(): RailPlatform[] {
    return this.gd
      .execGetMany<
        [number]
      >("SELECT i FROM RailPlatform WHERE station = ?", [this.i])
      .map(([i]) => new RailPlatform(i, this.gd));
  }
  get connectionsFromHere(): RailConnection[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT RailConnection.i 
      FROM (SELECT i FROM RailPlatform WHERE station = ?) A 
      INNER JOIN RailConnection ON A.i = RailConnection."from"`,
        [this.i],
      )
      .map(([i]) => new RailConnection(i, this.gd));
  }
  get connectionsToHere(): RailConnection[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT RailConnection.i
                                  FROM (SELECT i FROM RailPlatform WHERE station = ?) A
                                           INNER JOIN RailConnection ON A.i = RailConnection."to"`,
        [this.i],
      )
      .map(([i]) => new RailConnection(i, this.gd));
  }
  get lines(): RailLine[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT RailConnection.line 
      FROM (SELECT i FROM RailPlatform WHERE station = ?) A 
      LEFT JOIN RailConnection ON A.i = RailConnection."from" OR A.i = RailConnection."to"`,
        [this.i],
      )
      .map(([i]) => new RailLine(i, this.gd));
  }
}

export class RailPlatform extends Node {
  get code(): string | null {
    return this.getColumn("RailPlatform", "code");
  }
  get station(): RailStation {
    return new RailStation(this.getColumn("RailPlatform", "code"), this.gd);
  }

  get connectionsFromHere(): RailConnection[] {
    return this.gd
      .execGetMany<
        [number]
      >('SELECT RailConnection.i FROM RailConnection WHERE RailConnection."from" = ?', [this.i])
      .map(([i]) => new RailConnection(i, this.gd));
  }
  get connectionsToHere(): RailConnection[] {
    return this.gd
      .execGetMany<
        [number]
      >('SELECT RailConnection.i FROM RailConnection WHERE RailConnection."to" = ?', [this.i])
      .map(([i]) => new RailConnection(i, this.gd));
  }
  get lines(): RailLine[] {
    return this.gd
      .execGetMany<[number]>(
        `SELECT DISTINCT RailConnection.line FROM RailConnection 
      WHERE RailConnection."from" = ? OR RailConnection."to" = ?`,
        [this.i],
      )
      .map(([i]) => new RailLine(i, this.gd));
  }
}

export class RailConnection extends Node {
  get line(): RailLine {
    return new RailLine(this.getColumn("RailConnection", "line"), this.gd);
  }
  get from(): RailPlatform {
    return new RailPlatform(this.getColumn("RailConnection", "from"), this.gd);
  }
  get to(): RailPlatform {
    return new RailPlatform(this.getColumn("RailConnection", "to"), this.gd);
  }
  get direction(): string | null {
    return this.getColumn("RailConnection", "direction");
  }
  get duration(): number | null {
    return this.getColumn("RailConnection", "duration");
  }
}
