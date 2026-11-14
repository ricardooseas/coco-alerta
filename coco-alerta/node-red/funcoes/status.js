var dados = msg.payload;
if (typeof dados === "string") {
    try {
        dados = JSON.parse(dados);
    } catch (erro) {
        node.warn("Status MQTT nao esta em JSON.");
        return null;
    }
}
if (!dados || typeof dados.status !== "string") {
    node.warn("Status MQTT sem o campo status.");
    return null;
}
flow.set("statusEstacao", dados.estacao_id ? dados.estacao_id + " · " + dados.status : dados.status);
if (dados.intervalo_s) {
    flow.set("intervaloEstacao", dados.intervalo_s);
}
return mensagemPainel();
