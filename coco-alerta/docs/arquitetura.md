# Arquitetura implementada

## O que a atividade exige

A proposta de F054 pede uma solução de IoT para um problema real, com:

- arquitetura identificando sensor, controlador, comunicação, nuvem e usuário;
- MQTT, tópicos e mensagens preferencialmente em JSON, com teste de publicação e recebimento;
- circuito simulado no Wokwi, ESP32, pelo menos um sensor e um atuador, leitura e ação automática;
- fluxo Node-RED, dashboard com pelo menos um indicador e um gráfico, e pelo menos 20 leituras;
- relatório em PDF de 4 a 7 páginas e vídeo de 3 a 5 minutos.

A pontuação separa problema e arquitetura (1,0), MQTT (1,0), protótipo com sensor e atuador (1,0), dashboard, registro e automação (1,5) e relatório com demonstração (0,5).

## O que o projeto Cocó Alerta já definia

O documento do projeto descreve o Parque Estadual do Cocó, o incêndio de janeiro de 2024, a solução de monitoramento e a arquitetura em etapas: sensores, ESP32, Wi-Fi/MQTT, broker, Node-RED, dashboard e alerta por LED e buzzer.

Os sensores definidos são:

- DS18B20, temperatura do solo;
- DHT22, temperatura e umidade do ar;
- MQ-2, fumaça e gases.

O texto do projeto não fixava tópicos MQTT, formato JSON, limites numéricos nem o desenho do painel. Esses itens foram especificados na etapa de desenvolvimento e estão documentados aqui, sem trocar os componentes da arquitetura.

O documento também não trazia uma seção própria de segurança e privacidade. Essa seção foi acrescentada abaixo para atender a atividade. Ela não fazia parte do texto original.

## Adaptações necessárias

| Ponto | Decisão |
| --- | --- |
| O ESP32 do Wokwi alcança a internet, mas não um broker em `localhost` | Broker público `broker.hivemq.com:1883`, sem usuário e sem senha. O mesmo endereço está no firmware e no fluxo. |
| O MQ-2 real costuma ser alimentado em 5 V | Na simulação, VCC está em 3,3 V para a saída analógica permanecer na faixa do ADC do ESP32. O indicador usado é a contagem de 0 a 4095, não uma concentração calibrada. |
| O DS18B20 no Wokwi muda por um controle deslizante | A leitura demonstra acompanhamento térmico. Não demonstra detecção de combustão subterrânea. |
| Limites numéricos não existiam no projeto | Foram definidos como parâmetros experimentais em `shared/limites.json`. Não são limites oficiais. |
| Dashboard | Foi usado o `node-red-dashboard` 3.6.5, compatível com o fluxo entregue. |

Nenhuma credencial pessoal foi colocada no código. O Wi-Fi `Wokwi-GUEST` é a rede fictícia do simulador.

## Segurança e privacidade

O protótipo publica em um broker público. Qualquer pessoa que conheça o tópico pode ler as mensagens. Por isso o JSON não leva nome, matrícula, localização precisa nem outro dado pessoal. Só identifica a estação simulada `estacao01`.

O sistema não aciona serviço de emergência e não deve ser apresentado como alarme certificado. Há risco de falso alerta, quando calor e ar seco aparecem sem combustão, e de omissão, quando o sensor não é alcançado pela fumaça ou o limiar experimental não é atingido. O MQ-2 da simulação não distingue o gás e não está calibrado para o parque.

## Fluxo de dados

```text
DS18B20, DHT22, MQ-2
        │
        ▼
      ESP32  —— classificação e atuadores (LED e buzzer)
        │ Wi-Fi / MQTT / JSON
        ▼
broker.hivemq.com
        │
        ▼
    Node-RED —— validação, CSV, gráficos e painel
        │
        ▼
      usuário no dashboard
```

A classificação que acende o LED e o buzzer é calculada no ESP32. O Node-RED repete a regra para conferência e registra o risco recebido, de modo que o painel e os atuadores contem a mesma história.
