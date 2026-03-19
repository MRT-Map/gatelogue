import { Node } from "./node.js";
import { LocatedNode } from "./located.js";

export type RailMode = "warp" | "cart" | "traincarts" | "vehicles";

export class RailCompany extends Node {
  get name(): string {
    return this.getColumn("RailCompany", "name");
  }
  get link(): string | null {
    return this.getColumn("RailCompany", "link");
  }

  get lines(): RailLine[] {
    return this.getDerived(RailLine, "rail/company_lines");
  }
  get stations(): RailStation[] {
    return this.getDerived(RailStation, "rail/company_stations");
  }
  get platforms(): RailPlatform[] {
    return this.getDerived(RailPlatform, "rail/company_platforms");
  }
}

export class RailLine extends Node {
  get code(): string {
    return this.getColumn("RailLine", "code");
  }
  get company(): RailCompany {
    return this.getColumnFK("RailLine", "company", RailCompany)!;
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
    return this.getDerived(RailPlatform, "rail/line_platforms");
  }
  get stations(): RailStation[] {
    return this.getDerived(RailStation, "rail/line_stations");
  }
}

export class RailStation extends LocatedNode {
  get codes(): string[] {
    return this.getSet("RailStationCodes", "code");
  }
  get company(): RailCompany {
    return this.getColumnFK("RailStation", "company", RailCompany)!;
  }
  get name(): string | null {
    return this.getColumn("RailStation", "name");
  }

  get platforms(): RailPlatform[] {
    return this.getDerived(RailPlatform, "rail/station_platforms");
  }
  get connectionsFromHere(): RailConnection[] {
    return this.getDerived(
      RailConnection,
      "rail/station_connections_from_here",
    );
  }
  get connectionsToHere(): RailConnection[] {
    return this.getDerived(RailConnection, "rail/station_connections_to_here");
  }
  get lines(): RailLine[] {
    return this.getDerived(RailLine, "rail/station_lines");
  }
}

export class RailPlatform extends Node {
  get code(): string | null {
    return this.getColumn("RailPlatform", "code");
  }
  get station(): RailStation {
    return this.getColumnFK("RailPlatform", "station", RailStation)!;
  }

  get connectionsFromHere(): RailConnection[] {
    return this.getDerived(
      RailConnection,
      "rail/platform_connections_from_here",
    );
  }
  get connectionsToHere(): RailConnection[] {
    return this.getDerived(RailConnection, "rail/platform_connections_to_here");
  }
  get lines(): RailLine[] {
    return this.getDerived(RailLine, "rail/platform_lines");
  }
}

export class RailConnection extends Node {
  get line(): RailLine {
    return this.getColumnFK("RailConnection", "line", RailLine)!;
  }
  get from(): RailPlatform {
    return this.getColumnFK("RailConnection", "from", RailPlatform)!;
  }
  get to(): RailPlatform {
    return this.getColumnFK("RailConnection", "to", RailPlatform)!;
  }
  get direction(): string | null {
    return this.getColumn("RailConnection", "direction");
  }
  get duration(): number | null {
    return this.getColumn("RailConnection", "duration");
  }
}
