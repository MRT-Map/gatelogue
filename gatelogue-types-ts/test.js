/* eslint-disable no-console,no-undef */
import { GD } from "./dist/lib.js";

const gd = await GD.get();
console.log(gd.timestamp, gd.version)
console.assert(!gd.hasSources)