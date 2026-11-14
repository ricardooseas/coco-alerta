// Mesma regra de shared/limites.json e de wokwi/risk_engine.py.
// A especificacao esta em docs/regras-de-risco.md.

var ORDEM_RISCO = { "NORMAL": 0, "ATENÇÃO": 1, "ALERTA": 2, "EMERGÊNCIA": 3 };

function faixaAlto(valor, atencao, alerta, emergencia) {
    if (valor >= emergencia) { return 3; }
    if (valor >= alerta) { return 2; }
    if (valor >= atencao) { return 1; }
    return 0;
}

function faixaBaixo(valor, atencao, alerta, emergencia) {
    if (valor <= emergencia) { return 3; }
    if (valor <= alerta) { return 2; }
    if (valor <= atencao) { return 1; }
    return 0;
}

function classificarInstantaneo(solo, ambiente, umidade, fumaca, limites) {
    var nSolo = faixaAlto(solo, limites.temperatura_solo_atencao, limites.temperatura_solo_alerta, limites.temperatura_solo_emergencia);
    var nAmbiente = faixaAlto(ambiente, limites.temperatura_ambiente_atencao, limites.temperatura_ambiente_alerta, limites.temperatura_ambiente_emergencia);
    var nUmidade = faixaBaixo(umidade, limites.umidade_atencao, limites.umidade_alerta, limites.umidade_emergencia);
    var nFumaca = faixaAlto(fumaca, limites.fumaca_atencao, limites.fumaca_alerta, limites.fumaca_emergencia);
    var termico = nSolo > nAmbiente ? nSolo : nAmbiente;

    if (nSolo >= 3 && nFumaca >= 3 && (nAmbiente >= 3 || nUmidade >= 3)) {
        return "EMERGÊNCIA";
    }
    if (termico >= 2 && nFumaca >= 2) {
        return "ALERTA";
    }
    if (nSolo >= 1 || nAmbiente >= 1 || nUmidade >= 1 || nFumaca >= 1) {
        return "ATENÇÃO";
    }
    return "NORMAL";
}

function avaliarEstado(estado, solo, ambiente, umidade, fumaca, limites, persistencia) {
    var candidato = classificarInstantaneo(solo, ambiente, umidade, fumaca, limites);
    var recentes = (estado.recentes || []).concat([candidato]);
    if (recentes.length > persistencia) {
        recentes = recentes.slice(recentes.length - persistencia);
    }
    var atual = estado.atual || "NORMAL";
    if (recentes.length === persistencia && recentes.every(function (item) { return item === candidato; })) {
        atual = candidato;
    } else if (ORDEM_RISCO[candidato] < ORDEM_RISCO[atual]) {
        atual = candidato;
        recentes = [];
        for (var i = 0; i < persistencia; i++) { recentes.push(candidato); }
    }
    return { atual: atual, recentes: recentes, instantaneo: candidato };
}

function simularSequencia(sequencia, limites, persistencia) {
    var estado = { atual: "NORMAL", recentes: [] };
    var saidas = [];
    for (var i = 0; i < sequencia.length; i++) {
        var item = sequencia[i];
        estado = avaliarEstado(estado, item[0], item[1], item[2], item[3], limites, persistencia);
        saidas.push(estado.atual);
    }
    return saidas;
}
