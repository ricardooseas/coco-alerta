# Versões usadas na verificação

| Componente | Versão ou endereço | Observação |
| --- | --- | --- |
| Node.js | 26.0.0 | O Node-RED 4.0.9 também declara suporte a Node 18 e 20 |
| Node-RED | 4.0.9 | Iniciado com `node-red --userDir` |
| node-red-dashboard | 3.6.5 | Dashboard 1. O fluxo não importa no Dashboard 2 |
| Cliente MQTT do ensaio | mqtt 5.10.4, no diretório de verificação | Usado pelo Node-RED. O firmware no Wokwi usa `wokwi/umqtt_simple.py` |
| Broker | broker.hivemq.com:1883 | Sem usuário e sem senha. Alternativa, se os dois lados mudarem juntos: test.mosquitto.org:1883 |
| Firmware | MicroPython para ESP32 no editor web do Wokwi | Não há binário fixado. No VS Code, baixe `ESP32_GENERIC` e aponte em `wokwi.toml` |
| Python dos testes locais | 3.9.6 | Só para a regra, o gerador do fluxo e o publicador de teste |
| Fuso das leituras | America/Fortaleza, UTC−3 | Sem horário de verão |

O diretório `_verificacao` na raiz do trabalho é a instalação local usada para executar o Node-RED durante o desenvolvimento. A entrega do protótipo é a pasta `coco-alerta/`.
