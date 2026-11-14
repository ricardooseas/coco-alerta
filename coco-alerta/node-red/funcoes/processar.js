var dados = msg.payload;
if (typeof dados === "string") {
    try {
        dados = JSON.parse(dados);
    } catch (erro) {
        node.warn("Mensagem MQTT nao e JSON valido.");
        return null;
    }
}

function numero(valor, minimo, maximo, nome) {
    if (typeof valor !== "number" || !isFinite(valor) || valor < minimo || valor > maximo) {
        return nome + " fora da faixa esperada da simulacao";
    }
    return "";
}

if (!dados || typeof dados !== "object") {
    node.warn("Leitura vazia.");
    return null;
}
var campos = ["estacao_id", "temperatura_solo", "temperatura_ambiente", "umidade", "fumaca", "risco", "atuadores", "origem"];
for (var i = 0; i < campos.length; i++) {
    if (dados[campos[i]] === undefined || dados[campos[i]] === null || dados[campos[i]] === "") {
        node.warn("Campo obrigatorio ausente: " + campos[i]);
        return null;
    }
}
var erros = [
    numero(dados.temperatura_solo, -55, 125, "temperatura_solo"),
    numero(dados.temperatura_ambiente, -40, 80, "temperatura_ambiente"),
    numero(dados.umidade, 0, 100, "umidade"),
    numero(dados.fumaca, 0, 4095, "fumaca")
].filter(Boolean);
if (erros.length) {
    node.warn(erros.join("; "));
    return null;
}
var riscosValidos = { "NORMAL": 1, "ATENÇÃO": 1, "ALERTA": 1, "EMERGÊNCIA": 1 };
if (!riscosValidos[dados.risco]) {
    node.warn("Classificacao desconhecida: " + dados.risco);
    return null;
}
var atuadores = dados.atuadores;
if (!atuadores || typeof atuadores !== "object") {
    node.warn("Estado dos atuadores ausente.");
    return null;
}
["led_verde", "led_amarelo", "led_vermelho", "buzzer"].forEach(function (chave) {
    if (typeof atuadores[chave] !== "boolean") {
        erros.push(chave);
    }
});
if (erros.length) {
    node.warn("Atuadores devem ser verdadeiro ou falso.");
    return null;
}

var limites = flow.get("limites");
var persistencia = Number(flow.get("persistencia") || 2);
var estado = flow.get("estadoRisco") || { atual: "NORMAL", recentes: [] };
var calculado = avaliarEstado(
    estado,
    dados.temperatura_solo,
    dados.temperatura_ambiente,
    dados.umidade,
    dados.fumaca,
    limites,
    persistencia
);
flow.set("estadoRisco", { atual: calculado.atual, recentes: calculado.recentes });
if (calculado.atual !== dados.risco) {
    node.warn(
        "A estacao informou " + dados.risco +
        " e o calculo local resultou em " + calculado.atual +
        ". O painel mantem a classificacao da estacao, porque ela tambem comanda os atuadores."
    );
}

var registro = {
    estacao_id: String(dados.estacao_id),
    registrado_em: agoraLocal(),
    timestamp: dados.timestamp || "",
    temperatura_solo: dados.temperatura_solo,
    temperatura_ambiente: dados.temperatura_ambiente,
    umidade: dados.umidade,
    fumaca: dados.fumaca,
    risco: dados.risco,
    origem: String(dados.origem)
};
var leituras = flow.get("leituras") || [];
leituras.push(registro);
if (leituras.length > 500) {
    leituras = leituras.slice(leituras.length - 500);
}
flow.set("leituras", leituras);
flow.set("ultimaLeitura", dados);
flow.set("ultimaRegistro", registro);

var anterior = flow.get("ultimoRisco");
if (anterior !== registro.risco) {
    var alertas = flow.get("alertas") || [];
    alertas.push({
        registrado_em: registro.registrado_em,
        risco_anterior: anterior || "inicio",
        risco: registro.risco,
        temperatura_solo: registro.temperatura_solo,
        temperatura_ambiente: registro.temperatura_ambiente,
        umidade: registro.umidade,
        fumaca: registro.fumaca
    });
    if (alertas.length > 100) {
        alertas = alertas.slice(alertas.length - 100);
    }
    flow.set("alertas", alertas);
    flow.set("ultimoRisco", registro.risco);
}

var arquivo = flow.get("arquivo") || env.get("COCO_ALERTA_DATA") || "coco-alerta-readings.csv";
flow.set("arquivo", arquivo);
var saidaArquivo = { filename: arquivo, payload: linhaCsv(registro) };
if (!flow.get("temCabecalho")) {
    saidaArquivo = [
        { filename: arquivo, payload: CABECALHO_CSV },
        saidaArquivo
    ];
    flow.set("temCabecalho", true);
}

return [
    { payload: dados.temperatura_solo },
    { payload: dados.temperatura_ambiente },
    { payload: dados.umidade },
    { payload: dados.fumaca },
    { payload: dados.temperatura_solo, topic: "Temperatura do solo" },
    { payload: dados.temperatura_ambiente, topic: "Temperatura ambiente" },
    { payload: dados.umidade, topic: "Umidade" },
    { payload: dados.fumaca, topic: "Fumaca" },
    mensagemPainel(),
    mensagemHistorico(),
    mensagemOcorrencias(),
    saidaArquivo,
    mensagemContagem(),
    { payload: dados }
];
