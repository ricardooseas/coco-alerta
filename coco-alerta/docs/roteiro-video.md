# Roteiro do vídeo de 3 a 5 minutos

Grave depois de abrir o circuito no Wokwi e o painel em `http://127.0.0.1:1880/ui/`. Fale apenas o que estiver acontecendo na tela. O protótipo é experimental e não há estação instalada no Parque Estadual do Cocó.

| Tempo | O que mostrar | O que dizer |
| --- | --- | --- |
| 0:00–0:30 | Capa ou a primeira página do projeto | O Cocó Alerta acompanha indicadores ambientais do Parque Estadual do Cocó para apoiar a identificação antecipada de risco de incêndio. É um protótipo de simulação, com limites experimentais. |
| 0:30–1:00 | `diagram.json` em execução no Wokwi | A estação simulada usa ESP32, DS18B20 no solo, DHT22 no ar, MQ-2 como indicador de fumaça, três LEDs e um buzzer. |
| 1:00–1:40 | Monitor serial com a linha `[leitura]` | O firmware lê os sensores a cada 5 segundos, monta um JSON e publica em `cocoalerta/monitoramento/estacao01/dados`, no broker `broker.hivemq.com`. |
| 1:40–2:20 | Node-RED com os nós MQTT em “conectado” e o painel em NORMAL | O Node-RED recebe a mensagem, valida os campos, grava o CSV e atualiza medidores e gráficos. O LED verde acompanha o estado normal. |
| 2:20–3:20 | Mover os controles do DHT22, do DS18B20 e do MQ-2 | Primeiro, temperatura alta ou umidade baixa: depois de duas leituras, o estado vai para ATENÇÃO e o LED amarelo acende. Depois, solo quente junto com fumaça: ALERTA, LED vermelho e buzzer. Por fim, solo, ar, umidade e fumaça em faixa crítica ao mesmo tempo: EMERGÊNCIA. Um indicador sozinho não é tratado como incêndio confirmado. |
| 3:20–4:00 | Tabela de histórico e arquivo CSV | Cada leitura fica registrada com estação, horário, quatro medidas e classificação. O arquivo já pode ser exportado em `http://127.0.0.1:1880/coco-alerta/leituras.csv`. |
| 4:00–4:30 | Voltar os controles para os valores normais | A classificação desce na leitura seguinte. O protótipo mostra como a combinação dos sensores pode apoiar uma decisão. Ele não substitui um sistema certificado de detecção de incêndio. |

Se o relógio passar de 5 minutos, encurte a abertura e mostre só a passagem de NORMAL para EMERGÊNCIA, sem repetir cada nível intermediário na fala.

Antes de gravar, confira no console se `fumaca` está abaixo de 1000 no cenário normal. A subida de nível só aparece na segunda leitura igual.
