import type { GD } from "./lib.js";
import { type ID, Node } from "./node.js";

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
      .execGetMany<
        [number, number]
      >("SELECT node1, node2 FROM Proximity WHERE node1 = ?1 OR node2 = ?1", [this.i])
      .map(([node1, node2]) => [
        this.i === node1
          ? LocatedNode.fromId(node2, this.gd)
          : LocatedNode.fromId(node1, this.gd),
        new Proximity(node1, node2, this.gd),
      ]);
  }

  get sharedFacilities(): LocatedNode[] {
    return this.gd
      .execGetMany<
        [number, number]
      >("SELECT node1, node2 FROM SharedFacility WHERE node1 = ?1 OR node2 = ?1", [this.i])
      .map(([node1, node2]) =>
        this.i === node1
          ? LocatedNode.fromId(node2, this.gd)
          : LocatedNode.fromId(node1, this.gd),
      );
  }
}

export class Proximity {
  readonly i1: ID;
  readonly i2: ID;
  protected readonly gd: GD;

  constructor(i1: ID, i2: ID, gd: GD) {
    this.i1 = Math.min(i1, i2);
    this.i2 = Math.max(i1, i2);
    this.gd = gd;
  }

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
