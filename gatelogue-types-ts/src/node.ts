import { type GD } from "./lib.js";
import type { SqlValue } from "sql.js";
import SQLQueries from "./sql.js";

export type ID = number;

export abstract class Node {
  constructor(
    readonly i: ID,
    protected readonly gd: GD,
  ) {}

  static fromId(i: ID, gd: GD): Node | null {
    return gd.getNode(i);
  }

  get type(): string {
    return this.getColumn("Node", "type");
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
  protected getColumnFK<T extends Node>(
    tableName: string,
    columnName: string,
    Ty: new (i: ID, gd: GD) => T,
  ): T | null {
    const result = this.getColumn<number | null>(tableName, columnName);
    if (result === null) return null;
    return new Ty(result, this.gd);
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
  protected getDerived<T extends Node>(
    Ty: new (i: ID, gd: GD) => T,
    key: keyof typeof SQLQueries,
  ): T[] {
    return this.gd
      .execGetMany<[number]>(SQLQueries[key], [this.i])
      .map(([i]) => new Ty(i, this.gd));
  }
}
