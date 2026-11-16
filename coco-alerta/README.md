# Cocó Alerta

Protótipo experimental de monitoramento ambiental para a disciplina F054 — Fundamentos de Internet das Coisas. O sistema acompanha temperatura do solo, temperatura e umidade do ar e um indicador de fumaça, classifica o risco e aciona LED e buzzer. Não é um detector certificado de incêndio e não representa uma instalação real no Parque Estadual do Cocó.

## Objetivo

Demonstrar, em simulação, como uma estação com ESP32 pode ler sensores, publicar os dados em MQTT e permitir que o Node-RED registre, exiba e acompanhe a classificação de risco.

A proposta original, no documento do projeto, define o problema do parque, a solução e a arquitetura: DS18B20, DHT22, MQ-2, ESP32, Wi-Fi/MQTT, Node-RED, dashboard, LED e buzzer. Este diretório implementa essa arquitetura.

## Tecnologias

| Parte | Tecnologia |
| --- | --- |
| Simulação | Wokwi, placa `board-esp32-devkit-c-v4` |
| Firmware | MicroPython |
| Sensores | DS18B20, DHT22 e MQ-2 (`wokwi-gas-sensor`) |
| Atuadores | LED verde, amarelo e vermelho, buzzer |
| Comunicação | MQTT 3.1.1, mensagens JSON |
| Broker usado nos testes | `broker.hivemq.com`, porta 1883, sem usuário nem senha |
| Processamento e painel | Node-RED 4.0.9 e `node-red-dashboard` 3.6.5 |
| Armazenamento | CSV em `data/readings.csv` |

O pacote `node-red-dashboard` 3.6.5 é o Dashboard 1. O fluxo não funciona no Dashboard 2 (`@flowfuse/node-red-dashboard`).

## Pré-requisitos

- Conta no [Wokwi](https://wokwi.com) para executar o ESP32 simulado.
- Node.js 18 ou superior. A verificação deste protótipo usou Node.js 26.0.0.
- Node-RED 4.0.9:

```bash
npm install -g node-red@4.0.9
```

- No diretório de usuário do Node-RED, instalar o dashboard testado:

```bash
cd ~/.node-red
npm install node-red-dashboard@3.6.5
```

## Estrutura

```text
coco-alerta/
├── README.md
├── wokwi/                 firmware, circuito e limites usados pelo ESP32
├── node-red/flows.json    fluxo pronto para importar
├── shared/                limites e regra usados também pelo Node-RED
├── data/readings.csv      histórico gravado pelo Node-RED
├── docs/                  arquitetura, MQTT, regras, testes e roteiro do vídeo
├── evidencias/            capturas reais do painel e do fluxo
├── requirements/versoes.md
└── tools/                 testes da regra, publicação MQTT e geração do fluxo
```

## Abrir o circuito no Wokwi

1. Crie um projeto ESP32 com MicroPython em [wokwi.com/projects/new/micropython-esp32](https://wokwi.com/projects/new/micropython-esp32).
2. Substitua o conteúdo de `diagram.json` pelo arquivo `wokwi/diagram.json`.
3. No editor de arquivos do Wokwi, crie e cole, com os mesmos nomes:
   - `main.py`
   - `config.py`
   - `sensors.py`
   - `actuators.py`
   - `risk_engine.py`
   - `mqtt_client.py`
   - `limites.json`
   - `umqtt_simple.py`
4. Inicie a simulação. O monitor serial precisa estar ligado. As mensagens `print` aparecem nesse console.
5. A rede simulada já oferece o Wi-Fi `Wokwi-GUEST`, sem senha. Esse nome só existe dentro do Wokwi. Está em `wokwi/config.py`.
6. O firmware publica em `broker.hivemq.com`. O Node-RED precisa usar o mesmo broker, como já está em `node-red/flows.json`.

Solo 27 °C, ar 31 °C e umidade 68% começam na faixa normal. No MQ-2, baixe o ppm até o serial mostrar `fumaca` abaixo de 1000. Clique em cada sensor durante a simulação para mover o controle e mudar a leitura.

Se for usar a extensão Wokwi no VS Code ou o `wokwi-cli`, baixe o firmware `ESP32_GENERIC` em [micropython.org/download/ESP32_GENERIC](https://micropython.org/download/ESP32_GENERIC/) e acrescente em `wokwi/wokwi.toml`:

```toml
firmware = "firmware/micropython.bin"
```

O editor web do Wokwi não precisa desse arquivo: ele próprio carrega o MicroPython.

## Executar o Node-RED

Na primeira vez:

```bash
cd ~/.node-red
npm install node-red-dashboard@3.6.5
cd /caminho/para/coco-alerta
zsh tools/iniciar-node-red.sh
```

Abra `http://127.0.0.1:1880/`. No menu, importe `node-red/flows.json` e implante o fluxo. O script exporta duas variáveis antes de iniciar o processo:

- `COCO_ALERTA_DATA`: caminho de `data/readings.csv`
- `COCO_ALERTA_LIMITES`: caminho de `shared/limites.json`

Sem essas variáveis, o fluxo continua funcional, com os limites embutidos e com o CSV gravado em `coco-alerta-readings.csv` dentro do diretório do Node-RED.

O painel fica em `http://127.0.0.1:1880/ui/`.

A exportação CSV fica em `http://127.0.0.1:1880/coco-alerta/leituras.csv`.

## Como os dados circulam

1. O ESP32 lê DS18B20, DHT22 e MQ-2.
2. `risk_engine.py` classifica a leitura. A escala só sobe depois de duas leituras iguais. A volta para um nível menor acontece na leitura seguinte.
3. Os LEDs e o buzzer seguem essa classificação.
4. O firmware publica o JSON em `cocoalerta/monitoramento/estacao01/dados`.
5. O Node-RED valida o JSON, repete a mesma regra e registra a classificação enviada pela estação, porque é ela que comanda os atuadores.
6. O CSV, os medidores, os gráficos e o histórico são atualizados.

Os nomes dos campos são os mesmos no firmware, no teste e no CSV. A descrição dos tópicos está em `docs/topicos-mqtt.md`. A regra está em `docs/regras-de-risco.md`.

## Cenários no simulador

Aguarde duas coletas depois de mudar os controles. O intervalo padrão é 5 segundos, então a confirmação de uma subida de risco leva cerca de 10 segundos. O console mostra a linha `[leitura]` com o JSON.

| Situação | Ajuste sugerido | Classificação esperada |
| --- | --- | --- |
| Normal | solo 27 °C, ar 31 °C, umidade 68%, fumaça abaixo de 1000 no console | NORMAL, LED verde |
| Atenção | ar em 38 °C, ou umidade em 35%, com o restante normal | ATENÇÃO, LED amarelo |
| Alerta | solo em 45 °C e fumaça em 1800 ou mais no console | ALERTA, LED vermelho e buzzer intercalado |
| Emergência | solo 55 °C, ar 46 °C, umidade 20% e fumaça em 2800 ou mais | EMERGÊNCIA, LED vermelho piscando e buzzer rápido |

O número de fumaça exibido no console é a leitura analógica de 0 a 4095, não o ppm do controle do Wokwi. Se o valor inicial já passar de 1000, reduza o ppm do MQ-2 até a linha serial ficar abaixo desse limite antes de validar o estado normal.

Para encurtar o intervalo, publique em `cocoalerta/monitoramento/estacao01/comandos`:

```json
{"comando":"intervalo","valor":3}
```

O mínimo aceito é 3 segundos, por causa da conversão do DS18B20 e do intervalo do DHT22.

## Conferir as 20 leituras

Deixe a simulação rodar por pelo menos dois minutos com o Node-RED aberto. Cada ciclo grava uma linha em `data/readings.csv`. O painel mostra a quantidade em **Leituras armazenadas** e as 20 mais recentes na tabela.

Também é possível gerar 22 leituras de teste, sem o Wokwi, marcadas com `"origem": "teste"`:

```bash
python3 tools/publicar_cenarios.py
```

Essas linhas não são medições do parque nem leituras dos sensores simulados. Elas servem para exercitar MQTT, painel e CSV. O arquivo `evidencias/leituras-teste-mqtt.csv` é o resultado desse ensaio, já realizado.

## Problemas comuns

| O que aparece | O que fazer |
| --- | --- |
| `[wifi] sem conexao` | Confirme o SSID `Wokwi-GUEST` em `config.py`. Fora do Wokwi, troque para a rede real. |
| `[mqtt] falha na conexao` | Confira se o Node-RED usa o mesmo broker e a porta 1883. Se o broker público falhar, troque os dois lados ao mesmo tempo para `test.mosquitto.org`. |
| `[sensor] DHT22 indisponivel` | Reinicie a simulação. O pino de dados é o GPIO 14. |
| `[sensor] nenhum DS18B20` | Confira o fio DQ no GPIO 4 e o resistor de 4,7 kΩ até 3V3. |
| Painel sem widgets | Instale `node-red-dashboard@3.6.5` e importe o fluxo de novo. Dashboard 2 não serve. |
| CSV não cresce | Inicie o Node-RED com `tools/iniciar-node-red.sh`, para a variável `COCO_ALERTA_DATA` apontar para `data/readings.csv`. |
| Classificação não muda na hora | A subida de nível exige duas leituras consecutivas. A descida é imediata. |
| Fumaça alta com o controle ainda baixo | Observe o valor `fumaca` no console e use os limites de `shared/limites.json`, não o número de ppm isoladamente. |

## Documentação de apoio

- `docs/arquitetura.md` — confronto entre a atividade, o projeto e o que foi implementado
- `docs/topicos-mqtt.md` — tópicos e formato JSON
- `docs/regras-de-risco.md` — parâmetros experimentais
- `docs/roteiro-testes.md` — o que foi executado e o que depende do Wokwi
- `docs/roteiro-video.md` — roteiro de 3 a 5 minutos
- `docs/relatorio-entrega.md` — relatório da implementação e a matriz da atividade
