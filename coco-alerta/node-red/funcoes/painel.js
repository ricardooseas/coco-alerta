var CORES = {
    "NORMAL": "#1b7a3a",
    "ATENÇÃO": "#b8860b",
    "ALERTA": "#e65100",
    "EMERGÊNCIA": "#b71c1c"
};

function agoraLocal() {
    var formatador = new Intl.DateTimeFormat("sv-SE", {
        timeZone: "America/Fortaleza",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
    });
    return formatador.format(new Date()).replace(" ", "T") + "-03:00";
}

function csvCampo(valor) {
    var texto = valor === null || valor === undefined ? "" : String(valor);
    return '"' + texto.replace(/"/g, '""') + '"';
}

function linhaCsv(registro) {
    return [
        registro.estacao_id,
        registro.registrado_em,
        registro.timestamp,
        registro.temperatura_solo,
        registro.temperatura_ambiente,
        registro.umidade,
        registro.fumaca,
        registro.risco,
        registro.origem
    ].map(csvCampo).join(",");
}

var CABECALHO_CSV = "estacao_id,registrado_em,timestamp,temperatura_solo,temperatura_ambiente,umidade,fumaca,risco,origem";

function dividirCsv(linha) {
    var campos = [];
    var atual = "";
    var aspas = false;
    for (var i = 0; i < linha.length; i++) {
        var caractere = linha[i];
        if (aspas) {
            if (caractere === '"' && linha[i + 1] === '"') {
                atual += '"';
                i += 1;
            } else if (caractere === '"') {
                aspas = false;
            } else {
                atual += caractere;
            }
        } else if (caractere === '"') {
            aspas = true;
        } else if (caractere === ",") {
            campos.push(atual);
            atual = "";
        } else {
            atual += caractere;
        }
    }
    campos.push(atual);
    return campos;
}

function atuadoresDoRisco(risco) {
    if (!risco || risco === "aguardando") {
        return null;
    }
    return {
        led_verde: risco === "NORMAL",
        led_amarelo: risco === "ATENÇÃO",
        led_vermelho: risco === "ALERTA" || risco === "EMERGÊNCIA",
        buzzer: risco === "ALERTA" || risco === "EMERGÊNCIA"
    };
}

function textoAtuadores(atuadores) {
    if (!atuadores) {
        return "aguardando leitura ao vivo";
    }
    var partes = [];
    partes.push(atuadores.led_verde ? "LED verde ligado" : "LED verde desligado");
    partes.push(atuadores.led_amarelo ? "LED amarelo ligado" : "LED amarelo desligado");
    partes.push(atuadores.led_vermelho ? "LED vermelho ligado" : "LED vermelho desligado");
    partes.push(atuadores.buzzer ? "buzzer ativo" : "buzzer desligado");
    return partes.join(" · ");
}

function mensagemPainel() {
    var leitura = flow.get("ultimaLeitura") || {};
    var registro = flow.get("ultimaRegistro") || {};
    var risco = leitura.risco || registro.risco || "aguardando";
    var atuadores = leitura.atuadores || atuadoresDoRisco(risco);
    var nomes = ["NORMAL", "ATENÇÃO", "ALERTA", "EMERGÊNCIA"];
    var estados = nomes.map(function (nome) {
        var ativo = nome === risco;
        return {
            nome: nome,
            rotulo: ativo ? "estado atual" : "estado",
            fundo: ativo ? CORES[nome] : "#f4f7f5",
            texto: ativo ? "#ffffff" : "#3d5248",
            borda: CORES[nome]
        };
    });
    return {
        payload: risco,
        estacao: leitura.estacao_id || registro.estacao_id || "estacao01",
        status: flow.get("statusEstacao") || "aguardando contato",
        risco: risco,
        cor: CORES[risco] || "#0f3d2e",
        horario: registro.registrado_em || "sem leitura",
        atuadoresTexto: textoAtuadores(atuadores),
        estados: estados,
        aviso: "Protótipo experimental de apoio ao monitoramento. Não é um detector certificado de incêndio e não representa medições reais nem uma instalação no Parque Estadual do Cocó."
    };
}

function mensagemHistorico() {
    var lista = flow.get("leituras") || [];
    var linhas = lista.slice(-20).reverse().map(function (item) {
        return {
            registrado_em: item.registrado_em,
            hora: String(item.registrado_em || "").slice(11, 19),
            temperatura_solo: item.temperatura_solo,
            temperatura_ambiente: item.temperatura_ambiente,
            umidade: item.umidade,
            fumaca: item.fumaca,
            risco: item.risco,
            origem: item.origem,
            cor: CORES[item.risco] || "#143028"
        };
    });
    return { payload: lista.length, total: lista.length, linhas: linhas };
}

function mensagemOcorrencias() {
    var alertas = flow.get("alertas") || [];
    var linhas = alertas.slice(-20).reverse().map(function (item) {
        return {
            registrado_em: item.registrado_em,
            hora: String(item.registrado_em || "").slice(11, 19),
            risco_anterior: item.risco_anterior,
            risco: item.risco,
            temperatura_solo: item.temperatura_solo,
            temperatura_ambiente: item.temperatura_ambiente,
            umidade: item.umidade,
            fumaca: item.fumaca,
            cor: CORES[item.risco] || "#143028"
        };
    });
    return { payload: alertas.length, total: alertas.length, linhas: linhas };
}

function mensagemContagem() {
    return { payload: (flow.get("leituras") || []).length };
}

function mensagensGraficos(lista) {
    function pontos(campo) {
        return lista.map(function (item) {
            var instante = Date.parse(item.registrado_em);
            return { x: isNaN(instante) ? Date.now() : instante, y: Number(item[campo]) };
        });
    }
    if (!lista.length) {
        return [null, null, null, null];
    }
    return [
        { payload: [{ series: ["Temperatura do solo"], data: [pontos("temperatura_solo")], labels: [""] }] },
        { payload: [{ series: ["Temperatura ambiente"], data: [pontos("temperatura_ambiente")], labels: [""] }] },
        { payload: [{ series: ["Umidade"], data: [pontos("umidade")], labels: [""] }] },
        { payload: [{ series: ["Fumaça"], data: [pontos("fumaca")], labels: [""] }] }
    ];
}
