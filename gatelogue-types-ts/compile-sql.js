import * as fs from "node:fs";

const out = {};

const readFolder = (folder) => {
  for (let path of fs.readdirSync(folder)) {
    if (path === ".DO_NOT_EDIT") continue;
    path = `${folder}/${path}`;
    if (fs.statSync(path).isDirectory()) {
      readFolder(path);
    } else {
      out[path.replace(/^\.\/sql\/|\.sql$/gu, "")] = fs.readFileSync(
        path,
        "utf-8",
      );
    }
  }
};

readFolder("./sql", out);

const outFile = `export default ${JSON.stringify(out, null, 2)} as const;`;
fs.writeFileSync("src/sql.ts", outFile);
