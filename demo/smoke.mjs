// Load the demo in Pyodide as the browser does, before it is deployed:
// the wheel, app.py and one calculation of the hero example.
// Usage: node demo/smoke.mjs <path to the wheel> <path to app.py>
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { loadPyodide } from "pyodide";

const [wheel, app] = process.argv.slice(2);
const pyodide = await loadPyodide();
await pyodide.loadPackage(["pydantic", "micropip"]);
const target = `/tmp/${basename(wheel)}`;
pyodide.FS.writeFile(target, readFileSync(wheel));
await pyodide.pyimport("micropip").install(`emfs:${target}`);
pyodide.runPython(readFileSync(app, "utf8"));
const contracts = JSON.parse(pyodide.runPython("list_ccnls()"));
if (contracts.length === 0) throw new Error("no CCNL listed");
const params = JSON.stringify({
  ccnl: "commercio-confcommercio", level: "4", contract: "permanent", headcount: 20,
});
const result = JSON.parse(pyodide.runPython(`compute_salary(${JSON.stringify(params)})`));
if (result.error) throw new Error(result.error);
if (!(result.annual_net > 0)) throw new Error("no net computed");
console.log(`demo ok: ${contracts.length} CCNLs, net ${result.annual_net}`);
