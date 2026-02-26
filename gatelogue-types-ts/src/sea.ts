import {Node} from "./node.js";
import {LocatedNode} from "./located.js";

export type SeaMode = "cruise" | "warp ferry" | "traincarts ferry";

export class SeaCompany extends Node {
  get name(): string {
    return this.getColumn("SeaCompany", "name")
  }

  get lines(): SeaLine[] {
    return this.gd.execGetMany<[number]>("SELECT i FROM SeaLine WHERE company = ?", [this.i]).map(([i]) => new SeaLine(i, this.gd))
  }
  get stops(): SeaStop[] {
    return this.gd.execGetMany<[number]>("SELECT i FROM SeaStop WHERE company = ?", [this.i]).map(([i]) => new SeaStop(i, this.gd))
  }
  get docks(): SeaDock[] {
    return this.gd.execGetMany<[number]>(`SELECT DISTINCT SeaDock.i 
      FROM (SELECT i FROM SeaStop WHERE company = ?) A 
      INNER JOIN SeaDock on A.i = SeaDock.stop`, [this.i]).map(([i]) => new SeaDock(i, this.gd))
  }
}

export class SeaLine extends Node {
  get code(): string {
    return this.getColumn("SeaLine", "code")
  }
  get company(): SeaCompany {
    return new SeaCompany(this.getColumn("SeaLine", "company"), this.gd)
  }
  get name(): string | null {
    return this.getColumn("SeaLine", "name")
  }
  get colour(): string | null {
    return this.getColumn("SeaLine", "colour")
  }
  get mode(): SeaMode | null {
    return this.getColumn("SeaLine", "name")
  }
  get local(): boolean | null {
    const result = this.getColumn<number>("SeaLine", "name");
    return result === null ? null : result === 1
  }

  get docks(): SeaDock[] {
    return this.gd.execGetMany<[number]>(`SELECT DISTINCT SeaDock.i 
      FROM (SELECT "from", "to" FROM SeaConnection WHERE line = ?) A 
      LEFT JOIN SeaDock ON A."from" = SeaDock.i OR A."to" = SeaDock.i`, [this.i]).map(([i]) => new SeaDock(i, this.gd))
  }
  get stops(): SeaStop[] {
    return this.gd.execGetMany<[number]>(`SELECT DISTINCT SeaDock.stop 
      FROM (SELECT "from", "to" FROM SeaConnection WHERE line = ?) A 
      LEFT JOIN SeaDock ON A."from" = SeaDock.i OR A."to" = SeaDock.i`, [this.i]).map(([i]) => new SeaStop(i, this.gd))
  }
}

export class SeaStop extends LocatedNode {
  get codes(): string[] {
    return this.getSet("SeaStopCodes", "code");
  }
  get company(): SeaCompany {
    return new SeaCompany(this.getColumn("SeaStop", "company"), this.gd)
  }
  get name(): string | null {
    return this.getColumn("SeaStop", "name");
  }

  get docks(): SeaDock[] {
    return this.gd.execGetMany<[number]>("SELECT i FROM SeaDock WHERE stop = ?", [this.i]).map(([i]) => new SeaDock(i, this.gd))
  }
  get connectionsFromHere(): SeaConnection[] {
    return this.gd.execGetMany<[number]>(  `SELECT DISTINCT SeaConnection.i 
      FROM (SELECT i FROM SeaDock WHERE stop = ?) A 
      INNER JOIN SeaConnection ON A.i = SeaConnection."from"`, [this.i]).map(([i]) => new SeaConnection(i, this.gd))
  }
  get connectionsToHere(): SeaConnection[] {
    return this.gd.execGetMany<[number]>(  `SELECT DISTINCT SeaConnection.i
                                  FROM (SELECT i FROM SeaDock WHERE stop = ?) A
                                           INNER JOIN SeaConnection ON A.i = SeaConnection."to"`, [this.i]).map(([i]) => new SeaConnection(i, this.gd))
  }
  get lines(): SeaLine[] {
    return this.gd.execGetMany<[number]>(`SELECT DISTINCT SeaConnection.line 
      FROM (SELECT i FROM SeaDock WHERE stop = ?) A 
      LEFT JOIN SeaConnection ON A.i = SeaConnection."from" OR A.i = SeaConnection."to"`, [this.i]).map(([i]) => new SeaLine(i, this.gd))
  }
}

export class SeaDock extends Node {
  get code(): string | null {
    return this.getColumn("SeaDock", "code")
  }
  get stop(): SeaStop {
    return new SeaStop(this.getColumn("SeaDock", "code"), this.gd)
  }

  get connectionsFromHere(): SeaConnection[] {
    return this.gd.execGetMany<[number]>(  "SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection.\"from\" = ?", [this.i]).map(([i]) => new SeaConnection(i, this.gd))
  }
  get connectionsToHere(): SeaConnection[] {
    return this.gd.execGetMany<[number]>(  "SELECT SeaConnection.i FROM SeaConnection WHERE SeaConnection.\"to\" = ?", [this.i]).map(([i]) => new SeaConnection(i, this.gd))
  }
  get lines(): SeaLine[] {
    return this.gd.execGetMany<[number]>(`SELECT DISTINCT SeaConnection.line FROM SeaConnection 
      WHERE SeaConnection."from" = ? OR SeaConnection."to" = ?`, [this.i]).map(([i]) => new SeaLine(i, this.gd))
  }
}

export class SeaConnection extends Node {
  get line(): SeaLine {
    return new SeaLine(this.getColumn("SeaConnection", "line"), this.gd)
  }
  get from(): SeaDock {
    return new SeaDock(this.getColumn("SeaConnection", "from"), this.gd)
  }
  get to(): SeaDock {
    return new SeaDock(this.getColumn("SeaConnection", "to"), this.gd)
  }
  get direction(): string | null {
    return this.getColumn("SeaConnection", "direction")
  }
}