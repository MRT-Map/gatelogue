/* eslint-disable no-console,no-undef */
import {NodeGD} from "./dist/lib.js";
import Database from "better-sqlite3"

const gd = await NodeGD.get(Database);
console.log(gd.timestamp, gd.version);
console.assert(!gd.hasSources);
console.log(gd.getNode(1).type);
