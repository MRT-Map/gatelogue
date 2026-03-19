import type { GD } from "./lib.js";
import { type ID, Node } from "./node.js";
import SQLQueries from "./sql.js";

export type World = "Old" | "New" | "Space";

export abstract class LocatedNode extends Node {
  static override fromId(i: ID, gd: GD): LocatedNode {
    const node = gd.getNode(i);
    if (!(node instanceof LocatedNode)) {
      throw new Error(`${i} not LocatedNode`);
    }
    return node;
  }

  get world(): World | null {
    return this.getColumn("NodeLocation", "world");
  }

  get coordinates(): [number, number] | null {
    const [x, y] = this.gd.execGetOne<[number | null, number | null]>(
      "SELECT x, y FROM NodeLocation WHERE i = ?",
      [this.i],
    );
    if (x === null || y === null) return null;
    return [x, y];
  }

  get nodesInProximity(): [LocatedNode, Proximity][] {
    return this.gd
      .execGetMany<[number]>(SQLQueries["located/nodes_in_proximity"])
      .map(([other]) => [
        LocatedNode.fromId(other, this.gd),
        new Proximity(
          Math.min(other, this.i),
          Math.max(other, this.i),
          this.gd,
        ),
      ]);
  }

  get sharedFacilities(): LocatedNode[] {
    return this.gd
      .execGetMany<[number]>(SQLQueries["located/shared_facilities"])
      .map(([other]) => LocatedNode.fromId(other, this.gd));
  }
}

export class Proximity {
  constructor(
    readonly i1: ID,
    readonly i2: ID,
    protected readonly gd: GD,
  ) {}

  get distance(): number {
    return this.gd.execGetOne<[number]>(
      "SELECT distance FROM Proximity WHERE node1 = ? AND node2 = ?",
      [this.i1, this.i2],
    )[0]!;
  }

  get explicit(): boolean {
    return (
      this.gd.execGetOne<[number]>(
        "SELECT explicit FROM Proximity WHERE node1 = ? AND node2 = ?",
        [this.i1, this.i2],
      )[0] === 1
    );
  }
}
