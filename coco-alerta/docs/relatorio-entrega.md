# Relatório da entrega do protótipo

Pasta do protótipo: `coco-alerta/`. O PDF da atividade e o documento do projeto permanecem na raiz do trabalho e não foram alterados.

O protótipo é experimental. Ele apoia a demonstração do monitoramento. Não é um detector certificado de incêndio e não há instalação no Parque Estadual do Cocó. O DS18B20 da simulação acompanha a temperatura do solo. Ele não comprova detecção de combustão subterrânea. O MQ-2 da simulação é alimentado em 3,3 V e a fumaça usada na regra é a contagem do ADC, de 0 a 4095.

## A. Implementação

Arquivos principais:

- `wokwi/diagram.json` e `wokwi/wokwi.toml`: ESP32 DevKit C V4, DS18B20 no GPIO 4, DHT22 no GPIO 14, MQ-2 no GPIO 34, LEDs nos GPIO 25, 26 e 27, buzzer no GPIO 32.
- `wokwi/main.py`, `sensors.py`, `actuators.py`, `mqtt_client.py`, `risk_engine.py`, `config.py` e `umqtt_simple.py`: firmware MicroPython. O editor do Wokwi não cria pastas, então o cliente MQTT fica nesse arquivo único.
- `node-red/flows.json`: fluxo importável no Node-RED 4.0.9 com `node-red-dashboard` 3.6.5.
- `shared/limites.json`: limites experimentais usados pelo firmware e pelo fluxo.
- `data/readings.csv`: 24 leituras de teste.

Tecnologias: ESP32, MicroPython, Wokwi, MQTT no broker `broker.hivemq.com:1883`, JSON, Node-RED e CSV.

Arquitetura efetivamente montada: os sensores alimentam o ESP32; o firmware classifica o risco e aciona LED e buzzer; a mensagem segue por Wi-Fi e MQTT até o Node-RED, que valida, grava, desenha o painel e repete a regra só para conferência. O risco exibido é o enviado pela estação.

## B. Execução

1. Abrir o circuito já publicado em https://wokwi.com/projects/480798533237992449 e iniciar a simulação. O Wi-Fi do simulador é `Wokwi-GUEST`, sem senha.
2. Em outro terminal, na pasta `coco-alerta`, executar `zsh tools/iniciar-node-red.sh`.
3. Importar `node-red/flows.json` e implantar.
4. Abrir o painel em `http://127.0.0.1:1880/ui/`.
5. Mover os controles dos sensores. A subida de classificação aparece na segunda leitura igual. O intervalo padrão é 5 segundos.

O passo a passo completo está no `README.md`.

## C. Testes

| Cenário | Resultado nesta máquina | Situação |
| --- | --- | --- |
| Regra NORMAL, ATENÇÃO, ALERTA e EMERGÊNCIA, nas oito sequências de `tools/casos.json` | Python e JavaScript coincidiram | Aprovado |
| Cliente MQTT contra `broker.hivemq.com` | Publicou e recebeu a mensagem de ensaio | Aprovado |
| Node-RED recebe, classifica, desenha o painel e grava o CSV | 24 linhas `origem=teste`; reinício recuperou as 22 já gravadas | Aprovado |
| Testes 1 a 4 com os controles do Wokwi e com LED e buzzer | Circuito ainda não foi executado no simulador | Pendente |
| MQTT publicado pelo ESP32 | O recebimento pelo Node-RED foi aprovado com o publicador de teste | Pendente no ESP32 |
| Vinte leituras vindas do firmware | As 24 linhas atuais são de teste | Pendente |
| Queda e retomada de Wi-Fi ou MQTT | O código tenta reconectar e segue lendo sensores; a queda não foi provocada | Pendente |

O detalhe de cada teste está em `docs/roteiro-testes.md`.

## D. Evidências

Capturas reais do fluxo e do painel, em `evidencias/`:

- fluxo com os três nós MQTT conectados;
- painel em NORMAL, ALERTA e EMERGÊNCIA;
- gráficos, histórico e ocorrências;
- CSV com as 24 leituras de teste.

Ainda faltam as telas do circuito em execução, do console serial e dos LEDs no Wokwi. O procedimento está no mesmo roteiro. Não há imagem ilustrativa no lugar dessas telas.

## E. Pendências

- Executar o circuito no Wokwi e completar os testes 1, 2, 3, 4, 5, 6, 7 e 8 na coluna do ESP32.
- Conferir, na primeira simulação, se o valor serial de `fumaca` fica abaixo de 1000 com o controle inicial de 200 ppm. Se não ficar, baixar o ppm antes de validar o estado normal.
- Instalar localmente o Node-RED 4.0.9 e o `node-red-dashboard` 3.6.5. O Dashboard 2 não abre este fluxo.
- Gravar o vídeo de 3 a 5 minutos com o roteiro `docs/roteiro-video.md` e montar o PDF de 4 a 7 páginas pedido pela disciplina.
- Colocar na capa do PDF os integrantes reais da equipe. O documento do projeto traz Ricardo Oseas do Nascimento, matrícula 2425262. Este protótipo não acrescenta outros nomes.
- O broker é público. O JSON não leva dado pessoal, mas qualquer pessoa que conheça o tópico pode ler as mensagens da demonstração.
- O NTP pode falhar. Nesse caso `timestamp` fica nulo e o Node-RED ainda grava `registrado_em`.

## F. Matriz da atividade

A atividade vale 5,0 pontos e tem prazo em 27/11/2026. A matriz abaixo liga cada exigência ao que já existe. O PDF acadêmico e o vídeo continuam por conta da equipe.

| Exigência da proposta | Onde está atendida | Evidência já obtida |
| --- | --- | --- |
| Problema real, ambiente, público e solução | Documento do projeto, resumido em `docs/arquitetura.md` | Texto do projeto Cocó Alerta |
| Diagrama com sensor, controlador, comunicação, nuvem e usuário | `docs/arquitetura.md` e `wokwi/diagram.json` | Arquivos. A tela do simulador ligado ainda falta |
| Riscos de segurança e privacidade | Seção própria em `docs/arquitetura.md`. Não estava no texto original do projeto | Texto da seção |
| MQTT, tópicos e JSON | `wokwi/config.py`, `docs/topicos-mqtt.md` | Tópicos `.../dados`, `.../status`, `.../alertas` e `.../comandos` |
| Teste de publicação e recebimento | `tools/test_mqtt_cliente.py` e `tools/publicar_cenarios.py` | Cliente recebeu a mensagem; Node-RED mostrou “conectado” e gravou as leituras |
| Wokwi, ESP32, sensor e atuador | `wokwi/diagram.json`, `sensors.py`, `actuators.py` | Circuito descrito. Execução no simulador pendente |
| Leitura, transmissão e ação no atuador | `wokwi/main.py` | Código e regra testados. Acionamento visual no Wokwi pendente |
| Fluxo Node-RED | `node-red/flows.json` | `evidencias/fluxo-node-red.png` |
| Dashboard com indicador e gráfico | Painel do fluxo | `evidencias/dashboard-normal.png` e `dashboard-historico.png` |
| Pelo menos 20 leituras | `data/readings.csv` | 24 linhas, todas com `origem=teste` |
| Regra automática a partir dos dados | `wokwi/risk_engine.py` e `shared/risk_engine.js` | Oito sequências aprovadas; painel mudou para ALERTA e EMERGÊNCIA |
| Relatório de 4 a 7 páginas e vídeo de 3 a 5 minutos | `docs/roteiro-video.md` e as capturas em `evidencias/` | Roteiro e capturas prontos. PDF e vídeo ainda serão produzidos pela equipe |
| Demonstração integrada | README e este relatório | Integrado até o Node-RED com publicador de teste. Falta fechar o ciclo com o ESP32 no Wokwi |
