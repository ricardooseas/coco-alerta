var embutido = __LIMITES__;
flow.set("limites", embutido.limites);
flow.set("persistencia", embutido.persistencia_leituras);
flow.set("leituras", flow.get("leituras") || []);
flow.set("alertas", flow.get("alertas") || []);
flow.set("estadoRisco", flow.get("estadoRisco") || { atual: "NORMAL", recentes: [] });
var arquivo = env.get("COCO_ALERTA_DATA") || "coco-alerta-readings.csv";
flow.set("arquivo", arquivo);
flow.set("temCabecalho", false);
var caminhoLimites = env.get("COCO_ALERTA_LIMITES");
if (!caminhoLimites) {
    node.warn("COCO_ALERTA_LIMITES nao definido. O fluxo usa os limites embutidos, iguais ao arquivo shared/limites.json desta versao.");
}
return [
    { filename: arquivo, tipo: "csv" },
    caminhoLimites ? { filename: caminhoLimites, tipo: "limites" } : null
];
