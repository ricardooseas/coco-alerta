import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUNCOES = RAIZ / "node-red" / "funcoes"
DESTINO = RAIZ / "node-red" / "flows.json"


def nid(numero):
    return "c0c0a1e%09x" % numero


def ler(nome):
    return (FUNCOES / nome).read_text(encoding="utf-8")


def funcao(numero, nome, codigo, saidas, x, y, fios):
    return {
        "id": nid(numero),
        "type": "function",
        "z": nid(1),
        "name": nome,
        "func": codigo,
        "outputs": saidas,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "timeout": 0,
        "x": x,
        "y": y,
        "wires": fios,
    }


def main():
    limites = json.dumps(
        json.loads((RAIZ / "shared" / "limites.json").read_text(encoding="utf-8")),
        ensure_ascii=False,
    )
    motor = (RAIZ / "shared" / "risk_engine.js").read_text(encoding="utf-8")
    painel = ler("painel.js")
    processar = motor + "\n" + painel + "\n" + (
        "var embutido = %s;\n"
        "if (!flow.get('limites')) {\n"
        "  flow.set('limites', embutido.limites);\n"
        "  flow.set('persistencia', embutido.persistencia_leituras);\n"
        "}\n" % limites
    ) + ler("processar.js")
    restaurar = painel + "\n" + ler("restaurar.js")
    status = painel + "\n" + ler("status.js")
    exportar = painel + "\n" + ler("exportar.js")
    configurar = ler("configurar.js").replace("__LIMITES__", limites)

    tab = nid(1)
    broker = nid(2)
    grupo_situacao = nid(11)
    grupo_indicadores = nid(12)
    grupo_graficos = nid(13)
    grupo_historico = nid(14)
    grupo_ocorrencias = nid(15)

    medidores = [nid(40), nid(41), nid(42), nid(43)]
    graficos = [nid(50), nid(51), nid(52), nid(53)]
    tpl_situacao = nid(60)
    tpl_historico = nid(61)
    tpl_ocorrencias = nid(62)
    texto_contagem = nid(63)
    arquivo = nid(70)
    depuracao = nid(71)
    depuracao_erros = nid(72)

    nos = [
        {
            "id": tab,
            "type": "tab",
            "label": "Cocó Alerta",
            "disabled": False,
            "info": "Recepcao MQTT, validacao, classificacao, armazenamento e painel do prototipo Coco Alerta.",
        },
        {
            "id": broker,
            "type": "mqtt-broker",
            "name": "Broker Cocó Alerta",
            "broker": "broker.hivemq.com",
            "port": "1883",
            "clientid": "",
            "autoConnect": True,
            "usetls": False,
            "protocolVersion": "4",
            "keepalive": "60",
            "cleansession": True,
            "autoUnsubscribe": True,
            "birthTopic": "",
            "birthQos": "0",
            "birthRetain": "false",
            "birthPayload": "",
            "birthMsg": {},
            "closeTopic": "",
            "closeQos": "0",
            "closeRetain": "false",
            "closePayload": "",
            "closeMsg": {},
            "willTopic": "",
            "willQos": "0",
            "willRetain": "false",
            "willPayload": "",
            "willMsg": {},
            "sessionExpiry": "",
        },
        {
            "id": nid(3),
            "type": "ui_base",
            "theme": {
                "name": "theme-custom",
                "lightTheme": {"default": "#0f3d2e", "baseColor": "#0f3d2e", "baseFont": "Segoe UI, sans-serif"},
                "darkTheme": {"default": "#0f3d2e", "baseColor": "#0f3d2e", "baseFont": "Segoe UI, sans-serif"},
                "customTheme": {"name": "Cocó Alerta", "baseColor": "#0f3d2e", "baseFont": "Segoe UI, sans-serif"},
                "angularTheme": {"primary": "green", "accents": "teal", "warn": "red", "background": "grey", "palette": "light"},
                "themeState": {
                    "base-color": {"value": "#0f3d2e", "edited": True},
                    "base-font": {"value": "Segoe UI, sans-serif", "edited": True},
                    "page-titlebar-backgroundColor": {"value": "#0f3d2e", "edited": True},
                    "page-backgroundColor": {"value": "#e7f2ea", "edited": True},
                    "page-sidebar-backgroundColor": {"value": "#0f3d2e", "edited": True},
                    "group-backgroundColor": {"value": "#ffffff", "edited": True},
                    "group-textColor": {"value": "#143028", "edited": True},
                    "group-borderColor": {"value": "#d5e4da", "edited": True},
                    "widget-textColor": {"value": "#143028", "edited": True},
                    "widget-backgroundColor": {"value": "#f7faf8", "edited": True},
                    "widget-borderColor": {"value": "#d5e4da", "edited": True},
                },
            },
            "site": {
                "name": "Cocó Alerta",
                "hideToolbar": "false",
                "allowSwipe": "false",
                "lockMenu": "false",
                "allowTempTheme": "true",
                "dateFormat": "DD/MM/YYYY",
                "sizes": {"sx": 72, "sy": 48, "gx": 8, "gy": 6, "cx": 8, "cy": 6, "px": 0, "py": 0},
            },
        },
        {"id": nid(10), "type": "ui_tab", "name": "Monitoramento", "icon": "eco", "order": 1, "disabled": False, "hidden": False},
        grupo(grupo_situacao, "Central", nid(10), 1),
        grupo(grupo_indicadores, "Indicadores", nid(10), 2),
        grupo(grupo_graficos, "Gráficos", nid(10), 3),
        grupo(grupo_historico, "Histórico de leituras", nid(10), 4),
        grupo(grupo_ocorrencias, "Ocorrências de risco", nid(10), 5),
    ]

    fios_processar = [[item] for item in medidores + graficos] + [
        [tpl_situacao],
        [tpl_historico],
        [tpl_ocorrencias],
        [arquivo],
        [texto_contagem],
        [depuracao],
    ]
    fios_restaurar = [[item] for item in medidores + graficos] + [
        [tpl_situacao],
        [tpl_historico],
        [tpl_ocorrencias],
        [texto_contagem],
    ]

    nos.append({
        "id": nid(20),
        "type": "mqtt in",
        "z": tab,
        "name": "Dados da estação",
        "topic": "cocoalerta/monitoramento/estacao01/dados",
        "qos": "0",
        "datatype": "utf8",
        "broker": broker,
        "nl": False,
        "rap": True,
        "rh": 0,
        "inputs": 0,
        "x": 170,
        "y": 160,
        "wires": [[nid(21)]],
    })
    nos.append({
        "id": nid(21),
        "type": "json",
        "z": tab,
        "name": "Decodificar leitura",
        "property": "payload",
        "action": "",
        "pretty": False,
        "x": 400,
        "y": 160,
        "wires": [[nid(22)]],
    })
    nos.append(funcao(22, "Validar, classificar e registrar", processar, 14, 680, 160, fios_processar))
    nos.append({
        "id": nid(23),
        "type": "mqtt in",
        "z": tab,
        "name": "Status da estação",
        "topic": "cocoalerta/monitoramento/estacao01/status",
        "qos": "0",
        "datatype": "utf8",
        "broker": broker,
        "nl": False,
        "rap": True,
        "rh": 0,
        "inputs": 0,
        "x": 170,
        "y": 260,
        "wires": [[nid(24)]],
    })
    nos.append({
        "id": nid(24),
        "type": "json",
        "z": tab,
        "name": "Decodificar status",
        "property": "payload",
        "action": "",
        "pretty": False,
        "x": 400,
        "y": 260,
        "wires": [[nid(25)]],
    })
    nos.append(funcao(25, "Atualizar estado da estação", status, 1, 680, 260, [[tpl_situacao]]))
    nos.append({
        "id": nid(26),
        "type": "mqtt in",
        "z": tab,
        "name": "Alertas da estação",
        "topic": "cocoalerta/monitoramento/estacao01/alertas",
        "qos": "0",
        "datatype": "utf8",
        "broker": broker,
        "nl": False,
        "rap": True,
        "rh": 0,
        "inputs": 0,
        "x": 170,
        "y": 340,
        "wires": [[nid(27)]],
    })
    nos.append({
        "id": nid(27),
        "type": "debug",
        "z": tab,
        "name": "Evento de alerta",
        "active": True,
        "tosidebar": True,
        "console": False,
        "tostatus": False,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 430,
        "y": 340,
        "wires": [],
    })
    nos.append({
        "id": nid(30),
        "type": "inject",
        "z": tab,
        "name": "Ao iniciar o fluxo",
        "props": [{"p": "payload"}],
        "repeat": "",
        "crontab": "",
        "once": True,
        "onceDelay": "0.4",
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": 180,
        "y": 480,
        "wires": [[nid(31)]],
    })
    nos.append(funcao(31, "Configurar armazenamento", configurar, 2, 430, 480, [[nid(32)], [nid(34)]]))
    nos.append({
        "id": nid(32),
        "type": "file in",
        "z": tab,
        "name": "Ler histórico CSV",
        "filename": "filename",
        "filenameType": "msg",
        "format": "utf8",
        "chunk": False,
        "sendError": False,
        "encoding": "utf8",
        "allProps": False,
        "x": 680,
        "y": 440,
        "wires": [[nid(33)]],
    })
    nos.append(funcao(33, "Restaurar histórico", restaurar, 12, 920, 440, fios_restaurar))
    nos.append({
        "id": nid(34),
        "type": "file in",
        "z": tab,
        "name": "Ler limites",
        "filename": "filename",
        "filenameType": "msg",
        "format": "utf8",
        "chunk": False,
        "sendError": False,
        "encoding": "utf8",
        "allProps": False,
        "x": 660,
        "y": 520,
        "wires": [[nid(35)]],
    })
    nos.append(funcao(35, "Aplicar limites experimentais", ler("aplicar-limites.js"), 1, 920, 520, [[]]))
    nos.append({
        "id": nid(36),
        "type": "http in",
        "z": tab,
        "name": "Exportar CSV",
        "url": "/coco-alerta/leituras.csv",
        "method": "get",
        "upload": False,
        "swaggerDoc": "",
        "x": 170,
        "y": 620,
        "wires": [[nid(37)]],
    })
    nos.append(funcao(37, "Montar CSV para download", exportar, 1, 430, 620, [[nid(38)]]))
    nos.append({
        "id": nid(38),
        "type": "http response",
        "z": tab,
        "name": "Responder CSV",
        "statusCode": "",
        "headers": {},
        "x": 680,
        "y": 620,
        "wires": [],
    })
    nos.append({
        "id": nid(39),
        "type": "catch",
        "z": tab,
        "name": "Erros do fluxo",
        "scope": None,
        "uncaught": False,
        "x": 160,
        "y": 720,
        "wires": [[depuracao_erros]],
    })

    nos.extend(medidor(identificador, titulo, unidade, minimo, maximo, grupo_indicadores, ordem, cores, seg1, seg2)
               for identificador, titulo, unidade, minimo, maximo, ordem, cores, seg1, seg2 in [
                   (40, "Solo", "°C", 0, 80, 1, ["#1b7a3a", "#b8860b", "#b71c1c"], 35, 50),
                   (41, "Ambiente", "°C", 0, 70, 2, ["#1b7a3a", "#b8860b", "#b71c1c"], 36, 45),
                   (42, "Umidade", "%", 0, 100, 3, ["#b71c1c", "#b8860b", "#1b7a3a"], 30, 45),
                   (43, "Fumaça", "ADC", 0, 4095, 4, ["#1b7a3a", "#b8860b", "#b71c1c"], 1000, 1800),
               ])
    nos.extend(grafico(identificador, titulo, grupo_graficos, ordem, cor)
               for identificador, titulo, ordem, cor in [
                   (50, "Evolução da temperatura do solo", 1, "#1b7a3a"),
                   (51, "Evolução da temperatura ambiente", 2, "#1565c0"),
                   (52, "Variação da umidade", 3, "#00838f"),
                   (53, "Evolução do indicador de fumaça", 4, "#e65100"),
               ])
    nos.append(modelo(tpl_situacao, "Central", grupo_situacao, 1, 12, 6, ler("painel-situacao.html"), 210, 860))
    nos.append(modelo(tpl_historico, "Histórico", grupo_historico, 1, 12, 8, ler("painel-historico.html"), 460, 860))
    nos.append(modelo(tpl_ocorrencias, "Ocorrências", grupo_ocorrencias, 1, 12, 6, ler("painel-ocorrencias.html"), 720, 860))
    nos.append({
        "id": texto_contagem,
        "type": "ui_text",
        "z": tab,
        "group": grupo_historico,
        "order": 2,
        "width": 12,
        "height": 1,
        "name": "Total de leituras",
        "label": "Leituras armazenadas",
        "format": "{{msg.payload}}",
        "layout": "row-spread",
        "className": "",
        "style": False,
        "font": "",
        "fontSize": 16,
        "color": "#143028",
        "x": 980,
        "y": 860,
        "wires": [],
    })
    nos.append({
        "id": arquivo,
        "type": "file",
        "z": tab,
        "name": "Acrescentar leitura ao CSV",
        "filename": "filename",
        "filenameType": "msg",
        "appendNewline": True,
        "createDir": True,
        "overwriteFile": "false",
        "encoding": "utf8",
        "x": 1120,
        "y": 640,
        "wires": [[]],
    })
    nos.append(debug(depuracao, "Leitura validada", 1120, 720))
    nos.append(debug(depuracao_erros, "Falha no fluxo", 400, 720))
    nos.append({
        "id": nid(80),
        "type": "comment",
        "z": tab,
        "name": "Entrada MQTT",
        "info": "Os tres topicos de entrada usam o mesmo broker configurado em config.py do firmware.",
        "x": 150,
        "y": 80,
        "wires": [],
    })
    nos.append({
        "id": nid(81),
        "type": "comment",
        "z": tab,
        "name": "Regras e registro",
        "info": "A classificacao local usa a mesma regra do firmware. O painel mostra o risco enviado pela estacao, que e o risco que aciona LED e buzzer.",
        "x": 700,
        "y": 80,
        "wires": [],
    })

    DESTINO.write_text(json.dumps(nos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(DESTINO, "nos", len(nos))


def grupo(identificador, nome, aba, ordem):
    return {
        "id": identificador,
        "type": "ui_group",
        "name": nome,
        "tab": aba,
        "order": ordem,
        "disp": True,
        "width": 12,
        "collapse": False,
        "className": "",
    }


def medidor(numero, titulo, unidade, minimo, maximo, grupo_id, ordem, cores, seg1, seg2):
    return {
        "id": nid(numero),
        "type": "ui_gauge",
        "z": nid(1),
        "name": titulo,
        "group": grupo_id,
        "order": ordem,
        "width": 3,
        "height": 3,
        "gtype": "gage",
        "title": titulo,
        "label": unidade,
        "format": "{{value | number:0}}" if unidade == "ADC" else "{{value | number:1}}",
        "min": minimo,
        "max": maximo,
        "colors": cores,
        "seg1": seg1,
        "seg2": seg2,
        "diff": False,
        "className": "",
        "x": 980,
        "y": 80 + (ordem * 40),
        "wires": [],
    }


def grafico(numero, titulo, grupo_id, ordem, cor):
    return {
        "id": nid(numero),
        "type": "ui_chart",
        "z": nid(1),
        "name": titulo,
        "group": grupo_id,
        "order": ordem,
        "width": 6,
        "height": 6,
        "label": titulo,
        "chartType": "line",
        "legend": "false",
        "xformat": "HH:mm:ss",
        "interpolate": "linear",
        "nodata": "Aguardando leituras da simulação",
        "dot": False,
        "ymin": "",
        "ymax": "",
        "removeOlder": 1,
        "removeOlderPoints": "40",
        "removeOlderUnit": "3600",
        "cutout": 0,
        "useOneColor": True,
        "useUTC": False,
        "colors": [cor, "#AEC7E8", "#FF7F0E", "#2CA02C", "#98DF8A", "#D62728", "#FF9896", "#9467BD", "#C5B0D5"],
        "outputs": 1,
        "useDifferentColor": False,
        "className": "",
        "x": 1180,
        "y": 80 + (ordem * 40),
        "wires": [[]],
    }


def modelo(identificador, nome, grupo_id, ordem, largura, altura, html, x, y):
    return {
        "id": identificador,
        "type": "ui_template",
        "z": nid(1),
        "group": grupo_id,
        "name": nome,
        "order": ordem,
        "width": largura,
        "height": altura,
        "format": html,
        "storeOutMessages": True,
        "fwdInMessages": True,
        "resendOnRefresh": True,
        "templateScope": "local",
        "className": "",
        "x": x,
        "y": y,
        "wires": [[]],
    }


def debug(identificador, nome, x, y):
    return {
        "id": identificador,
        "type": "debug",
        "z": nid(1),
        "name": nome,
        "active": True,
        "tosidebar": True,
        "console": False,
        "tostatus": False,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": x,
        "y": y,
        "wires": [],
    }


if __name__ == "__main__":
    main()
