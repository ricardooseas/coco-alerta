# Regras de classificação

Os números abaixo são parâmetros experimentais da simulação. Não são limites oficiais de segurança ambiental, não vêm de norma de detecção de incêndio e não foram medidos no Parque Estadual do Cocó.

A mesma tabela está em `shared/limites.json` e em `wokwi/limites.json`. O firmware lê o arquivo ao iniciar. O Node-RED lê `COCO_ALERTA_LIMITES` e, se a variável não existir, usa a cópia embutida no fluxo.

## Faixas

Temperatura do solo, em °C, pelo DS18B20:

| Abaixo de 35 | 35 a 41,9 | 42 a 49,9 | 50 ou mais |
| --- | --- | --- | --- |
| normal | atenção | alerta | crítico |

Temperatura do ar, em °C, pelo DHT22:

| Abaixo de 36 | 36 a 39,9 | 40 a 44,9 | 45 ou mais |
| --- | --- | --- | --- |
| normal | atenção | alerta | crítico |

Umidade relativa, em %. Quanto menor, pior:

| Acima de 40 | 31 a 40 | 26 a 30 | 25 ou menos |
| --- | --- | --- | --- |
| normal | atenção | alerta | crítico |

Fumaça, contagem do ADC de 0 a 4095:

| Abaixo de 1000 | 1000 a 1799 | 1800 a 2799 | 2800 ou mais |
| --- | --- | --- | --- |
| normal | atenção | alerta | crítico |

## Decisão

Uma leitura isolada não vira incêndio confirmado.

- **EMERGÊNCIA:** solo em nível crítico, fumaça em nível crítico e, ao mesmo tempo, ar ou umidade também em nível crítico.
- **ALERTA:** a temperatura do solo ou a do ar está pelo menos na faixa de alerta e a fumaça também está pelo menos nessa faixa.
- **ATENÇÃO:** qualquer indicador saiu do normal, mas a combinação acima não se formou. Calor sozinho, ar seco sozinho ou fumaça sozinha permanecem em atenção.
- **NORMAL:** todos os indicadores estão na primeira coluna.

Para reduzir um pico falso, a classificação só sobe quando duas leituras consecutivas pedem o mesmo nível. A volta a um nível menor acontece na primeira leitura que já pede esse nível, para a demonstração mostrar a recuperação sem espera extra.

O LED verde acompanha NORMAL. O amarelo acompanha ATENÇÃO. O vermelho e o buzzer acompanham ALERTA e EMERGÊNCIA. Na emergência o vermelho pisca e o buzzer pulsa mais rápido.

## Onde a regra está no código

- Firmware: `wokwi/risk_engine.py`
- Node-RED: `shared/risk_engine.js`, copiado para dentro de `node-red/flows.json`
- Casos usados no teste automático: `tools/casos.json`

`python3 tools/test_risk_engine.py` e `node tools/verificar_paridade.mjs` conferem se as duas implementações devolvem a mesma sequência.
