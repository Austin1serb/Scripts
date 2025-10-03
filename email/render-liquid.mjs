import { Liquid } from "liquidjs";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Allow CLI arg: node render-liquid.mjs [templatePath] [dataPath]
const templatePath = process.argv[2] || path.join(__dirname, "template.liquid");
const dataPath = process.argv[3] || path.join(__dirname, "data.json");

// Helpful error if files are missing
function mustRead(p) {
  if (!fs.existsSync(p)) {
    console.error(`File not found: ${p}`);
    process.exit(1);
  }
  return fs.readFileSync(p, "utf8");
}

const tpl = mustRead(templatePath);
const dataRaw = fs.existsSync(dataPath) ? mustRead(dataPath) : "{}";
const data = JSON.parse(dataRaw);

const engine = new Liquid({ strictFilters: false, strictVariables: false });

const cases = [
  { name: "TEST", data: { car: "maserati", ...data } },

];

for (const c of cases) {
  const html = await engine.parseAndRender(tpl, c.data);
  const out = path.join(__dirname, `out-${c.name}.html`);
  fs.writeFileSync(out, html);
  console.log("Wrote", out);
}
