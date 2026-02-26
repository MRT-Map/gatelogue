import {LocatedNode} from "./located.js";

export type WarpType = "premier" | "terminus" | "traincarts" | "portal" | "misc"

export class SpawnWarp extends LocatedNode {
  get name(): string {
    return this.getColumn("SpawnWarp", "name")
  }
  get warpType(): WarpType {
    return this.getColumn("SpawnWarp", "warpType")
  }
}