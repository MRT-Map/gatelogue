/**
 * JS utility library for using Gatelogue data in JS/TS projects. It will load the database for you to access via ORM or raw SQL.
 *
 * # Installation
 * The data can be imported into your JavaScript/TypeScript project with classes and type definitions.
 * * retrieving from npmjs.com:
 *   * npm: `npm i gatelogue-types`
 *   * yarn: `yarn add gatelogue-types`
 *   * pnpm: `pnpm add gatelogue-types`
 *   * denoL `deno add npm:gatelogue-types`
 *   * bun: `bun add gatelogue-types`
 * * retrieving from jsr.io:
 *   * npm: `npx jsr add @mrt-map/gatelogue-types`
 *   * yarn: `yarn add jsr:@mrt-map/gatelogue-types`
 *   * pnpm: `pnpm i jsr:@mrt-map/gatelogue-types`
 *   * deno: `deno add jsr:@mrt-map/gatelogue-types`
 *   * bun: `bunx jsr add @mrt-map/gatelogue-types`
 *
 * To import directly from the repository:
 * * npm: `npm i 'https://gitpkg.vercel.app/mrt-map/gatelogue/gatelogue-types-ts?main'`
 * * yarn: `yarn add 'https://gitpkg.vercel.app/mrt-map/gatelogue/gatelogue-types-ts?main'`
 * * pnpm: `pnpm add mrt-map/gatelogue#path:/gatelogue-types-ts`
 * * bun: `bun add 'git+https://gitpkg.vercel.app/mrt-map/gatelogue/gatelogue-types-ts?main'`
 *
 * # Usage
 * To retrieve the data:
 * @example
 * ```ts
 * // if on a browser:
 * import { BrowserGD } from "gatelogue-types";
 * import sqlite3InitModule from '@sqlite.org/sqlite-wasm';
 * const sqlite3 = await sqlite3InitModule();
 * const gd = await BrowserGD.get(sqlite3); // retrieve data, no sources
 * const gd = await BrowserGD.get(sqlite3, true); // retrieve data, with sources
 *
 * // if on node:
 * import { NodeGD } from "gatelogue-types";
 * import Database from "better-sqlite3";
 * const gd = await NodeGD.get(Database); // retrieve data, no sources
 * const gd = await NodeGD.get(Database, true); // retrieve data, with sources
 * ```
 *
 * Using the ORM does not require SQL and makes for generally clean code.
 * However, doing this is very inefficient as each attribute access is one SQL query.
 * ```ts
 * for (const airport of gd.airAirports) {
 *   for (const gate of airport.gates) {
 *     console.log(`Airport ${airport.code} has gate ${gate.code}`);
 *   }
 * }
 * ```
 *
 * Querying the underlying SQLite database directly with `sql.js` is generally more efficient and faster.
 * It is also the only way to access the `*Source` tables, if you retrieved the database with those.
 * ```ts
 * for (const [airportCode, gateCode] of gd.execGetMany<[string, string]>(
 *   "SELECT A.code, G.code FROM AirGate G INNER JOIN AirAirport A ON G.airport = A.i")
 * ) {
 *   console.log(`Airport ${airportCode} has gate ${gateCode}`);
 * }
 * ```
 * @packageDocumentation
 */

import { type ID, Node } from "./node.js";
import {
  AirAirline,
  AirAirport,
  AirFlight,
  AirGate,
  Aircraft,
  type AirMode,
} from "./air.js";
import { LocatedNode, Proximity, type World } from "./located.js";
import {
  BusBerth,
  BusCompany,
  BusConnection,
  BusLine,
  BusStop,
  type BusMode,
} from "./bus.js";
import {
  RailCompany,
  RailConnection,
  RailLine,
  RailPlatform,
  RailStation,
  type RailMode,
} from "./rail.js";
import {
  SeaCompany,
  SeaConnection,
  SeaDock,
  SeaLine,
  SeaStop,
  type SeaMode,
} from "./sea.js";
import { SpawnWarp, type WarpType } from "./spawnWarp.js";
import { Town, type Rank } from "./town.js";
export {
  type ID,
  Node,
  LocatedNode,
  AirAirline,
  AirAirport,
  AirFlight,
  AirGate,
  Aircraft,
  type AirMode,
  BusBerth,
  BusCompany,
  BusConnection,
  BusLine,
  BusStop,
  type BusMode,
  RailCompany,
  RailConnection,
  RailLine,
  RailPlatform,
  RailStation,
  type RailMode,
  SeaCompany,
  SeaConnection,
  SeaDock,
  SeaLine,
  SeaStop,
  type SeaMode,
  SpawnWarp,
  type WarpType,
  Town,
  type Rank,
  Proximity,
  type World,
};
import type NodeDatabase from "better-sqlite3";
import type {
  Sqlite3Static,
  Database as BrowserDatabase,
  BindingSpec,
} from "@sqlite.org/sqlite-wasm";

export abstract class GD {
  static async getData(sources = false): Promise<Uint8Array> {
    return await fetch(sources ? URL : URL_NO_SOURCES).then((res) =>
      res.bytes(),
    );
  }

  abstract execGetZeroOrOne<T extends unknown[]>(
    sql: string,
    params?: unknown[],
  ): T | null;
  abstract execGetOne<T extends unknown[]>(sql: string, params?: unknown[]): T;
  abstract execGetMany<T extends unknown[]>(
    sql: string,
    params?: unknown[],
  ): T[];

  get timestamp(): string {
    return this.execGetOne<[string]>("SELECT timestamp FROM Metadata")[0]!;
  }

  get version(): number {
    return this.execGetOne<[number]>("SELECT version FROM Metadata")[0]!;
  }

  get hasSources(): boolean {
    return (
      this.execGetOne<[number]>("SELECT has_sources FROM Metadata")[0] === 1
    );
  }

  // eslint-disable-next-line complexity,max-lines-per-function
  getNode(i: ID, ty?: string): Node | null {
    const tyOrNull = this.execGetZeroOrOne<[string]>(
      "SELECT type FROM Node WHERE i = ?",
      [i],
    );
    if (tyOrNull === null) return null;
    const [actualTy] = tyOrNull;
    if (ty !== undefined && ty !== actualTy) return null;

    switch (actualTy) {
      case "AirAirline":
        return new AirAirline(i, this);
      case "AirAirport":
        return new AirAirport(i, this);
      case "AirGate":
        return new AirGate(i, this);
      case "AirFlight":
        return new AirFlight(i, this);
      case "BusCompany":
        return new BusCompany(i, this);
      case "BusLine":
        return new BusLine(i, this);
      case "BusStop":
        return new BusStop(i, this);
      case "BusBerth":
        return new BusBerth(i, this);
      case "BusConnection":
        return new BusConnection(i, this);
      case "SeaCompany":
        return new SeaCompany(i, this);
      case "SeaLine":
        return new SeaLine(i, this);
      case "SeaStop":
        return new SeaStop(i, this);
      case "SeaDock":
        return new SeaDock(i, this);
      case "SeaConnection":
        return new SeaConnection(i, this);
      case "RailCompany":
        return new RailCompany(i, this);
      case "RailLine":
        return new RailLine(i, this);
      case "RailStation":
        return new RailStation(i, this);
      case "RailPlatform":
        return new RailPlatform(i, this);
      case "RailConnection":
        return new RailConnection(i, this);
      case "SpawnWarp":
        return new SpawnWarp(i, this);
      case "Town":
        return new Town(i, this);
      default:
        throw new Error(`Unknown type ${ty}`);
    }
  }
  get nodes(): Node[] {
    return this.execGetMany<[number]>("SELECT i FROM Node").map(([i]) =>
      Node.fromId(i, this)!,
    );
  }
  get locatedNodes(): LocatedNode[] {
    return this.execGetMany<[number]>("SELECT i FROM NodeLocation").map(([i]) =>
      LocatedNode.fromId(i, this)!,
    );
  }
  protected nodesByType(ty: string): ID[] {
    return this.execGetMany<[number]>("SELECT i FROM Node WHERE type = ?", [
      ty,
    ]).map(([i]) => i);
  }
  get airAirlines(): AirAirline[] {
    return this.nodesByType("AirAirline").map((i) => new AirAirline(i, this));
  }
  get airAirports(): AirAirport[] {
    return this.nodesByType("AirAirport").map((i) => new AirAirport(i, this));
  }
  get airGates(): AirGate[] {
    return this.nodesByType("AirGate").map((i) => new AirGate(i, this));
  }
  get airFlights(): AirFlight[] {
    return this.nodesByType("AirFlight").map((i) => new AirFlight(i, this));
  }
  get busCompanies(): BusCompany[] {
    return this.nodesByType("BusCompany").map((i) => new BusCompany(i, this));
  }
  get busLines(): BusLine[] {
    return this.nodesByType("BusLine").map((i) => new BusLine(i, this));
  }
  get busStops(): BusStop[] {
    return this.nodesByType("BusStop").map((i) => new BusStop(i, this));
  }
  get busBerths(): BusBerth[] {
    return this.nodesByType("BusBerth").map((i) => new BusBerth(i, this));
  }
  get busConnections(): BusConnection[] {
    return this.nodesByType("BusConnection").map(
      (i) => new BusConnection(i, this),
    );
  }
  get railCompanies(): RailCompany[] {
    return this.nodesByType("RailCompany").map((i) => new RailCompany(i, this));
  }
  get railLines(): RailLine[] {
    return this.nodesByType("RailLine").map((i) => new RailLine(i, this));
  }
  get railStations(): RailStation[] {
    return this.nodesByType("RailStation").map((i) => new RailStation(i, this));
  }
  get RailPlatforms(): RailPlatform[] {
    return this.nodesByType("RailPlatform").map(
      (i) => new RailPlatform(i, this),
    );
  }
  get railConnections(): RailConnection[] {
    return this.nodesByType("RailConnection").map(
      (i) => new RailConnection(i, this),
    );
  }
  get seaCompanies(): SeaCompany[] {
    return this.nodesByType("SeaCompany").map((i) => new SeaCompany(i, this));
  }
  get seaLines(): SeaLine[] {
    return this.nodesByType("SeaLine").map((i) => new SeaLine(i, this));
  }
  get seaStops(): SeaStop[] {
    return this.nodesByType("SeaStop").map((i) => new SeaStop(i, this));
  }
  get seaDocks(): SeaDock[] {
    return this.nodesByType("SeaDock").map((i) => new SeaDock(i, this));
  }
  get seaConnections(): SeaConnection[] {
    return this.nodesByType("SeaConnection").map(
      (i) => new SeaConnection(i, this),
    );
  }
  get spawnWarps(): SpawnWarp[] {
    return this.nodesByType("SpawnWarp").map((i) => new SpawnWarp(i, this));
  }
  get towns(): Town[] {
    return this.nodesByType("Town").map((i) => new Town(i, this));
  }
}

const URL =
  "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data.db";
const URL_NO_SOURCES =
  "https://raw.githubusercontent.com/MRT-Map/gatelogue/refs/heads/dist/data-ns.db";

export class NodeGD extends GD {
  db: NodeDatabase.Database;

  private constructor(
    data: Uint8Array,
    DatabaseConstructor: typeof NodeDatabase,
  ) {
    super();
    this.db = new DatabaseConstructor(Buffer.from(data));
  }

  static async get(dc: typeof NodeDatabase, sources = false): Promise<NodeGD> {
    return new NodeGD(await GD.getData(sources), dc);
  }

  override execGetZeroOrOne<T extends unknown[]>(
    sql: string,
    params?: unknown[],
  ): T | null {
    return (
      this.db
        .prepare<unknown[], T>(sql)
        .raw(true)
        .get(...(params ?? [])) ?? null
    );
  }

  override execGetOne<T extends unknown[]>(sql: string, params?: unknown[]): T {
    return this.execGetZeroOrOne<T>(sql, params)!;
  }

  override execGetMany<T extends unknown[]>(
    sql: string,
    params?: unknown[],
  ): T[] {
    return this.db
      .prepare<unknown[], T>(sql)
      .raw(true)
      .all(...(params ?? []));
  }
}

export class BrowserGD extends GD {
  db: BrowserDatabase;

  private constructor(data: Uint8Array, sqlite3: Sqlite3Static) {
    super();
    const p = sqlite3.wasm.allocFromTypedArray(data);
    this.db = new sqlite3.oo1.DB(":memory:", "ct");
    const rc = sqlite3.capi.sqlite3_deserialize(
      this.db.pointer!,
      "main",
      p,
      data.byteLength,
      data.byteLength,
      // eslint-disable-next-line no-bitwise
      sqlite3.capi.SQLITE_DESERIALIZE_FREEONCLOSE |
        sqlite3.capi.SQLITE_DESERIALIZE_RESIZEABLE,
    );
    this.db.checkRc(rc);
  }

  static async get(
    sqlite3: Sqlite3Static,
    sources = false,
  ): Promise<BrowserGD> {
    return new BrowserGD(await GD.getData(sources), sqlite3);
  }

  override execGetZeroOrOne<T extends unknown[]>(
    sql: string,
    params?: unknown[],
  ): T | null {
    const result = this.db.selectArray(sql, params as BindingSpec);
    if (result === undefined) return null;
    return result as T;
  }

  override execGetOne<T extends unknown[]>(sql: string, params?: unknown[]): T {
    return this.execGetZeroOrOne<T>(sql, params)!;
  }

  override execGetMany<T extends unknown[]>(
    sql: string,
    params?: unknown[],
  ): T[] {
    return this.db.selectArrays(sql, params as BindingSpec) as T[];
  }
}
