var lista = flow.get("leituras") || [];
var corpo = lista.map(linhaCsv).join("\n");
msg.payload = CABECALHO_CSV + (corpo ? "\n" + corpo : "") + "\n";
msg.headers = {
    "Content-Type": "text/csv; charset=utf-8",
    "Content-Disposition": "attachment; filename=leituras-coco-alerta.csv"
};
return msg;
