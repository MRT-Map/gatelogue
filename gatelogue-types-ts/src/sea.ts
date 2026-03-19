import { Node } from "./node.js";
import { LocatedNode } from "./located.js";

export type SeaMode = "cruise" | "warp ferry" | "traincarts ferry";

export class SeaCompany extends Node {
  get name(): string {
    return this.getColumn("SeaCompany", "name");
  }
  get link(): string | null {
    return this.getColumn("SeaCompany", "link");
  }

  get lines(): SeaLine[] {
    return this.getDerived(SeaLine, "sea/company_lines");
  }
  get stops(): SeaStop[] {
    return this.getDerived(SeaStop, "sea/company_stops");
  }
  get docks(): SeaDock[] {
    return this.getDerived(SeaDock, "sea/company_docks");
  }
}

export class SeaLine extends Node {
  get code(): string {
    return this.getColumn("SeaLine", "code");
  }
  get company(): SeaCompany {
    return this.getColumnFK("SeaLine", "company", SeaCompany)!;
  }
  get name(): string | null {
    return this.getColumn("SeaLine", "name");
  }
  get colour(): string | null {
    return this.getColumn("SeaLine", "colour");
  }
  get mode(): SeaMode | null {
    return this.getColumn("SeaLine", "name");
  }
  get local(): boolean | null {
    const result = this.getColumn<number>("SeaLine", "name");
    return result === null ? null : result === 1;
  }

  get docks(): SeaDock[] {
    return this.getDerived(SeaDock, "sea/line_docks");
  }
  get stops(): SeaStop[] {
    return this.getDerived(SeaStop, "sea/line_stops");
  }
}

export class SeaStop extends LocatedNode {
  get codes(): string[] {
    return this.getSet("SeaStopCodes", "code");
  }
  get company(): SeaCompany {
    return this.getColumnFK("SeaStop", "company", SeaCompany)!;
  }
  get name(): string | null {
    return this.getColumn("SeaStop", "name");
  }

  get docks(): SeaDock[] {
    return this.getDerived(SeaDock, "sea/stop_docks");
  }
  get connectionsFromHere(): SeaConnection[] {
    return this.getDerived(SeaConnection, "sea/stop_connections_from_here");
  }
  get connectionsToHere(): SeaConnection[] {
    return this.getDerived(SeaConnection, "sea/stop_connections_to_here");
  }
  get lines(): SeaLine[] {
    return this.getDerived(SeaLine, "sea/stop_lines");
  }
}

export class SeaDock extends Node {
  get code(): string | null {
    return this.getColumn("SeaDock", "code");
  }
  get stop(): SeaStop {
    return this.getColumnFK("SeaDock", "stop", SeaStop)!;
  }

  get connectionsFromHere(): SeaConnection[] {
    return this.getDerived(SeaConnection, "sea/dock_connections_from_here");
  }
  get connectionsToHere(): SeaConnection[] {
    return this.getDerived(SeaConnection, "sea/dock_connections_to_here");
  }
  get lines(): SeaLine[] {
    return this.getDerived(SeaLine, "sea/dock_lines");
  }
}

export class SeaConnection extends Node {
  get line(): SeaLine {
    return this.getColumnFK("SeaConnection", "line", SeaLine)!;
  }
  get from(): SeaDock {
    return this.getColumnFK("SeaConnection", "from", SeaDock)!;
  }
  get to(): SeaDock {
    return this.getColumnFK("SeaConnection", "to", SeaDock)!;
  }
  get direction(): string | null {
    return this.getColumn("SeaConnection", "direction");
  }
  get duration(): number | null {
    return this.getColumn("SeaConnection", "duration");
  }
}
