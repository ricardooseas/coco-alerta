try {
    var dados = typeof msg.payload === "string" ? JSON.parse(msg.payload) : msg.payload;
    if (!dados.limites || !dados.persistencia_leituras) {
        node.warn("Arquivo de limites incompleto. Mantendo os limites ja carregados.");
        return null;
    }
    flow.set("limites", dados.limites);
    flow.set("persistencia", Number(dados.persistencia_leituras));
    node.log("Limites experimentais carregados de " + msg.filename);
} catch (erro) {
    node.warn("Nao foi possivel ler os limites: " + erro.message);
}
return null;
