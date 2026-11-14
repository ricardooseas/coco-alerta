import fs from "fs";
import path from "path";
import vm from "vm";
import { fileURLToPath } from "url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const codigo = fs.readFileSync(path.join(raiz, "shared", "risk_engine.js"), "utf8");
const limites = JSON.parse(fs.readFileSync(path.join(raiz, "shared", "limites.json"), "utf8"));
const casos = JSON.parse(fs.readFileSync(path.join(raiz, "tools", "casos.json"), "utf8"));
const contexto = {};
vm.createContext(contexto);
vm.runInContext(codigo, contexto);

let falhas = 0;
for (const caso of casos.casos) {
  const obtido = contexto.simularSequencia(caso.sequencia, limites.limites, limites.persistencia_leituras);
  const ok = JSON.stringify(obtido) === JSON.stringify(caso.esperado);
  if (!ok) {
    falhas += 1;
    console.error("FALHA", caso.nome, obtido, "esperado", caso.esperado);
  }
}
if (falhas) {
  process.exit(1);
}
console.log("Paridade JavaScript aprovada em", casos.casos.length, "cenarios");
