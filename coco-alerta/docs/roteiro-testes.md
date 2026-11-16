# Roteiro de testes

Data da verificação automática: 13 e 14 de novembro de 2026.

Há dois níveis de evidência. O primeiro foi executado nesta máquina: regra de risco, cliente MQTT, Node-RED, painel e CSV. O segundo depende do simulador Wokwi, que precisa ser aberto no navegador com a conta do estudante. Os testes desse segundo nível ficam pendentes até essa execução.

Nenhum valor deste roteiro é medição real do Parque Estadual do Cocó. As 24 linhas já gravadas têm `origem=teste`.

## O que já foi executado

### Regra de risco

Procedimento: `python3 tools/test_risk_engine.py` e `node tools/verificar_paridade.mjs`.

Resultado esperado: as oito sequências de `tools/casos.json` produzem a mesma classificação em Python e em JavaScript, incluindo a espera de duas leituras para subir de nível e a volta imediata para NORMAL.

Resultado obtido: as duas execuções terminaram sem falha.

Situação: aprovado.

Evidência: saída dos dois comandos no terminal de desenvolvimento. A regra está em `docs/regras-de-risco.md`.

### Cliente MQTT

Procedimento: `python3 tools/test_mqtt_cliente.py broker.hivemq.com`.

Resultado esperado: conectar, assinar, publicar e receber uma mensagem no broker público. O tópico desse ensaio foi `cocoalerta/teste/conexao/<identificador>`, para não misturar com a estação.

Resultado obtido: a mensagem publicada foi recebida pelo mesmo cliente.

Situação: aprovado para o cliente `wokwi/umqtt/simple.py` em CPython. No editor do Wokwi a estação usa `wokwi/umqtt_simple.py` e publicou no broker.

Evidência: saída do comando, com o broker `broker.hivemq.com`.

### Publicação, painel e armazenamento

Procedimento: Node-RED 4.0.9 com o fluxo importado e conectado a `broker.hivemq.com:1883`. Em seguida, `python3 tools/publicar_cenarios.py` enviou 22 leituras. Depois, duas mensagens avulsas pediram as telas de ALERTA e EMERGÊNCIA. O processo foi reiniciado depois das 22 primeiras linhas.

Resultado esperado: o painel muda de classificação, os gráficos acompanham a série, o CSV guarda cada linha e o histórico volta depois do reinício.

Resultado obtido:

- Os três nós MQTT do fluxo ficaram com o estado conectado.
- O painel mostrou NORMAL, ATENÇÃO, ALERTA e EMERGÊNCIA, com o texto dos LEDs e do buzzer correspondente.
- O CSV `data/readings.csv` ficou com 24 linhas de dados: 11 NORMAL, 4 ATENÇÃO, 5 ALERTA e 4 EMERGÊNCIA. Todas têm `origem=teste` e `estacao_id=estacao01`.
- A exportação `http://127.0.0.1:1880/coco-alerta/leituras.csv` devolveu o mesmo conteúdo.
- Depois do reinício, o log registrou a restauração das 22 leituras que já estavam no arquivo. As duas mensagens seguintes foram acrescentadas ao mesmo CSV.

Situação: aprovado para o caminho publicador de teste → broker → Node-RED → painel → CSV. A primeira leitura de cada subida de risco permanece no nível anterior, como a regra exige. Por isso a sequência de 22 mensagens não coloca todas as amostras novas já no nível destino.

Evidência:

- `evidencias/fluxo-node-red.png`
- `evidencias/dashboard-normal.png`
- `evidencias/dashboard-historico.png`
- `evidencias/dashboard-ocorrencias.png`
- `evidencias/dashboard-alerta.png`
- `evidencias/dashboard-emergencia.png`
- `evidencias/leituras-teste-mqtt.csv` e `data/readings.csv`

## O que ainda precisa ser feito no Wokwi

Abra o circuito como está descrito no `README.md`. Confirme no monitor serial que `fumaca` está abaixo de 1000 antes do primeiro teste. Se não estiver, abaixe o controle de ppm do MQ-2. Cada subida de classificação exige duas coletas; com o intervalo de 5 segundos, espere cerca de 10 segundos.

| Teste | Procedimento | Resultado esperado | Situação |
| --- | --- | --- | --- |
| 1. Normal | Manter solo 27 °C, ar 31 °C, umidade 68% e fumaça serial abaixo de 1000 | JSON com `risco` NORMAL, LED verde aceso, mensagem no Node-RED com `origem` firmware | Pendente |
| 2. Atenção | Subir o ar para 38 °C ou baixar a umidade para 35% e aguardar duas leituras | ATENÇÃO e LED amarelo | Pendente |
| 3. Alerta | Solo em 45 °C e fumaça serial em 1800 ou mais, por duas leituras | ALERTA, LED vermelho e buzzer em pulsos | Pendente |
| 4. Emergência | Solo 55 °C, ar 46 °C, umidade 20% e fumaça serial em 2800 ou mais, por duas leituras | EMERGÊNCIA, LED vermelho piscando e buzzer mais rápido | Pendente |
| 5. MQTT a partir do ESP32 | Observar o tópico `cocoalerta/monitoramento/estacao01/dados` no Node-RED | JSON com os mesmos campos de `docs/topicos-mqtt.md` | Pendente no ESP32. O recebimento pelo Node-RED já foi aprovado com o publicador de teste |
| 6. Painel com o ESP32 | Deixar o firmware publicando | Medidores e gráficos mudam com `origem` firmware | Pendente para o firmware. O painel já reagiu às mensagens de teste |
| 7. Vinte leituras do firmware | Deixar a simulação por pelo menos dois minutos | Novas linhas `origem=firmware` no CSV, além das 24 de teste | Pendente. As 24 linhas de teste já existem |
| 8. Reconexão | No código, o laço continua lendo sensores quando o broker falha e tenta Wi-Fi e MQTT de novo | Retomada sem reiniciar a simulação | Pendente. O comportamento está escrito em `mqtt_client.py` e `main.py`, mas a queda de rede não foi provocada |

## Capturas que o relatório acadêmico ainda precisa

O PDF da disciplina pede tela do circuito simulado e do dashboard. As telas do dashboard e do fluxo já estão em `evidencias/`. Faltam, feitas dentro do Wokwi em execução:

1. O circuito inteiro, com ESP32, DS18B20, DHT22, MQ-2, três LEDs e buzzer.
2. O monitor serial com uma linha `[leitura]` em JSON.
3. O LED verde no estado normal e o LED vermelho com o buzzer no alerta ou na emergência.
4. O painel no mesmo momento, para mostrar a mensagem que saiu do ESP32.

Não substitua essas telas por ilustração gerada. Se um sensor não responder, registre a mensagem de erro do console e a limitação no relatório.
