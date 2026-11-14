var texto = typeof msg.payload === "string" ? msg.payload : "";
var linhas = texto.split(/\r?\n/).filter(function (linha) { return linha.trim() !== ""; });
var leituras = [];
if (linhas.length > 0 && linhas[0].indexOf("estacao_id") === 0) {
    flow.set("temCabecalho", true);
    linhas = linhas.slice(1);
}
linhas.forEach(function (linha) {
    var campos = dividirCsv(linha);
    if (campos.length < 9) {
        return;
    }
    leituras.push({
        estacao_id: campos[0],
        registrado_em: campos[1],
        timestamp: campos[2],
        temperatura_solo: Number(campos[3]),
        temperatura_ambiente: Number(campos[4]),
        umidade: Number(campos[5]),
        fumaca: Number(campos[6]),
        risco: campos[7],
        origem: campos[8]
    });
});
flow.set("leituras", leituras);
var alertas = [];
var riscoAnterior = null;
leituras.forEach(function (item) {
    if (riscoAnterior !== item.risco) {
        alertas.push({
            registrado_em: item.registrado_em,
            risco_anterior: riscoAnterior || "inicio",
            risco: item.risco,
            temperatura_solo: item.temperatura_solo,
            temperatura_ambiente: item.temperatura_ambiente,
            umidade: item.umidade,
            fumaca: item.fumaca
        });
        riscoAnterior = item.risco;
    }
});
flow.set("alertas", alertas);
if (leituras.length) {
    flow.set("ultimaRegistro", leituras[leituras.length - 1]);
    flow.set("ultimoRisco", leituras[leituras.length - 1].risco);
}
var ultima = leituras.length ? leituras[leituras.length - 1] : null;
var graficos = mensagensGraficos(leituras);
var medidores = ultima ? [
    { payload: ultima.temperatura_solo },
    { payload: ultima.temperatura_ambiente },
    { payload: ultima.umidade },
    { payload: ultima.fumaca }
] : [null, null, null, null];
node.log("Historico restaurado: " + leituras.length + " leituras.");
return medidores.concat(graficos).concat([
    mensagemPainel(),
    mensagemHistorico(),
    mensagemOcorrencias(),
    mensagemContagem()
]);
