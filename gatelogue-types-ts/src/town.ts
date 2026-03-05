import { LocatedNode } from "./located.js";

export type Rank =
  | "Unranked"
  | "Councillor"
  | "Mayor"
  | "Senator"
  | "Governor"
  | "Premier"
  | "Community";

export class Town extends LocatedNode {
  get name(): string {
    return this.getColumn("Town", "name");
  }
  get rank(): Rank {
    return this.getColumn("Town", "rank");
  }
  get mayor(): string {
    return this.getColumn("Town", "mayor");
  }
  get deputyMayor(): string | null {
    return this.getColumn("Town", "deputyMayor");
  }
}
