import type { GD } from "./lib.js";
import type { SqlValue } from "sql.js";

export type ID = number;

export abstract class Node {
  readonly i: ID;
  protected readonly gd: GD;

  constructor(i: ID, gd: GD) {
    this.i = i;
    this.gd = gd;
  }

  static fromId(i: ID, gd: GD): Node | null {
    return gd.getNode(i);
  }

  protected getColumn<T extends SqlValue>(
    tableName: string,
    columnName: string,
  ): T {
    return this.gd.execGetOne<[T]>(
      `SELECT "${columnName}" FROM ${tableName} WHERE i = ?`,
      [this.i],
    )[0]!;
  }
  protected getSet<T extends SqlValue>(
    tableName: string,
    columnName: string,
  ): T[] {
    return this.gd
      .execGetMany<
        [T]
      >(`SELECT DISTINCT "${columnName}" FROM ${tableName} WHERE i = ?`, [this.i])
      .map(([a]) => a);
  }
}
