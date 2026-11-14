# Tópicos MQTT

Broker: `broker.hivemq.com`  
Porta: `1883`  
Protocolo: MQTT 3.1.1  
Usuário e senha: vazios  

A base `cocoalerta/monitoramento/estacao01` permite outra estação no futuro, trocando apenas o identificador. Exemplo: `cocoalerta/monitoramento/estacao02/dados`.

| Tópico | Direção | Retido | Função |
| --- | --- | --- | --- |
| `cocoalerta/monitoramento/estacao01/dados` | ESP32 publica, Node-RED assina | não | Leitura periódica |
| `cocoalerta/monitoramento/estacao01/status` | ESP32 publica, Node-RED assina | sim | `online` ao conectar; `offline` no testamento MQTT |
| `cocoalerta/monitoramento/estacao01/alertas` | ESP32 publica, Node-RED assina | não | Publicado só quando a classificação muda |
| `cocoalerta/monitoramento/estacao01/comandos` | Node-RED ou ferramenta externa publica, ESP32 assina | não | Hoje aceita a troca do intervalo |

## Leitura

```json
{
  "estacao_id": "estacao01",
  "timestamp": "2026-11-13T23:59:29-03:00",
  "temperatura_solo": 27.0,
  "temperatura_ambiente": 31.0,
  "umidade": 68.0,
  "fumaca": 348,
  "risco": "NORMAL",
  "atuadores": {
    "led_verde": true,
    "led_amarelo": false,
    "led_vermelho": false,
    "buzzer": false
  },
  "origem": "firmware",
  "intervalo_s": 5
}
```

`timestamp` pode ser `null` se o NTP não responder. O Node-RED grava também `registrado_em`, com o horário de Fortaleza no momento em que a mensagem chega.

`fumaca` é a média de oito leituras do ADC, de 0 a 4095. Não é ppm.

`origem` vale `firmware` na simulação do ESP32 e `teste` quando a mensagem vem de `tools/publicar_cenarios.py`.

`buzzer: true` significa que o alarme daquele nível está habilitado. No hardware simulado o piezo toca em pulsos, então o pino não fica ligado o tempo todo.

Os riscos possíveis são exatamente `NORMAL`, `ATENÇÃO`, `ALERTA` e `EMERGÊNCIA`.

## Status

```json
{"estacao_id":"estacao01","status":"online","intervalo_s":5,"timestamp":"2026-11-13T23:59:20-03:00"}
```

O testamento, publicado pelo broker se a estação cair, é:

```json
{"estacao_id":"estacao01","status":"offline"}
```

## Alerta

O mesmo objeto da leitura, com `evento` em `mudanca_de_risco` e `risco_anterior`.

## Comando

```json
{"comando":"intervalo","valor":3}
```

O firmware limita o valor entre 3 e 60 segundos e republica o status.
