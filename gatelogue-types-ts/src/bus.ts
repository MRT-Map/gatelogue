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
    return this.getDerived(BusLine, "bus/company_lines");
  }
  get stops(): BusStop[] {
    return this.getDerived(BusStop, "bus/company_stops");
  }
  get berths(): BusBerth[] {
    return this.getDerived(BusBerth, "bus/company_berths");
  }
}

export class BusLine extends Node {
  get code(): string {
    return this.getColumn("BusLine", "code");
  }
  get company(): BusCompany {
    return this.getColumnFK("BusLine", "company", BusCompany)!;
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
    return this.getDerived(BusBerth, "bus/line_berths");
  }
  get stops(): BusStop[] {
    return this.getDerived(BusStop, "bus/line_stops");
  }
}

export class BusStop extends LocatedNode {
  get codes(): string[] {
    return this.getSet("BusStopCodes", "code");
  }
  get company(): BusCompany {
    return this.getColumnFK("BusStop", "company", BusCompany)!;
  }
  get name(): string | null {
    return this.getColumn("BusStop", "name");
  }

  get berths(): BusBerth[] {
    return this.getDerived(BusBerth, "bus/stop_berths");
  }
  get connectionsFromHere(): BusConnection[] {
    return this.getDerived(BusConnection, "bus/stop_connections_from_here");
  }
  get connectionsToHere(): BusConnection[] {
    return this.getDerived(BusConnection, "bus/stop_connections_to_here");
  }
  get lines(): BusLine[] {
    return this.getDerived(BusLine, "bus/stop_lines");
  }
}

export class BusBerth extends Node {
  get code(): string | null {
    return this.getColumn("BusBerth", "code");
  }
  get stop(): BusStop {
    return this.getColumnFK("BusBerth", "stop", BusStop)!;
  }

  get connectionsFromHere(): BusConnection[] {
    return this.getDerived(BusConnection, "bus/berth_connections_from_here");
  }
  get connectionsToHere(): BusConnection[] {
    return this.getDerived(BusConnection, "bus/berth_connections_to_here");
  }
  get lines(): BusLine[] {
    return this.getDerived(BusLine, "bus/berth_lines");
  }
}

export class BusConnection extends Node {
  get line(): BusLine {
    return this.getColumnFK("BusConnection", "line", BusLine)!;
  }
  get from(): BusBerth {
    return this.getColumnFK("BusConnection", "from", BusBerth)!;
  }
  get to(): BusBerth {
    return this.getColumnFK("BusConnection", "to", BusBerth)!;
  }
  get direction(): string | null {
    return this.getColumn("BusConnection", "direction");
  }
  get duration(): number | null {
    return this.getColumn("BusConnection", "duration");
  }
}
