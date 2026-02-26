import {LocatedNode} from "./located.js";

export type Rank = "Unranked" | "Councillor" | "Mayor" | "Senator" | "Governor" | "Premier" | "Community"

export class Town extends LocatedNode {
  get name(): string {
    return this.getColumn("SpawnWarp", "name")
  }
  get rank(): Rank {
    return this.getColumn("SpawnWarp", "rank")
  }
  get mayor(): string {
    return this.getColumn("SpawnWarp", "mayor")
  }
  get deputyMayor(): string | null {
    return this.getColumn("SpawnWarp", "deputyMayor")
  }
}