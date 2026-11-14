# Evidências

As imagens desta pasta foram capturadas do Node-RED em execução, em 14 de novembro de 2026, depois que `tools/publicar_cenarios.py` publicou leituras com `origem=teste`. Não são medições do Parque Estadual do Cocó e não mostram o ESP32 no Wokwi.

| Arquivo | O que mostra |
| --- | --- |
| `fluxo-node-red.png` | Fluxo importado, com os três nós MQTT em “conectado” |
| `dashboard-normal.png` | Estado NORMAL, LED verde e os quatro indicadores |
| `dashboard-alerta.png` | Estado ALERTA, LED vermelho e buzzer habilitado |
| `dashboard-emergencia.png` | Estado EMERGÊNCIA e indicadores na faixa crítica |
| `dashboard-historico.png` | Gráficos e tabela com as leituras de teste |
| `dashboard-ocorrencias.png` | Transições NORMAL, ATENÇÃO, ALERTA, EMERGÊNCIA e a volta para NORMAL |
| `leituras-teste-mqtt.csv` | Cópia do CSV usado nessas telas |

A captura do circuito, do monitor serial e dos LEDs acesos no Wokwi ainda precisa ser feita manualmente. O procedimento está em `docs/roteiro-testes.md`.
