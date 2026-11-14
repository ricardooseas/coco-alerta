# Fluxo Node-RED do Cocó Alerta

O arquivo `flows.json` é um fluxo completo para importar no Node-RED 4.0.9 com `node-red-dashboard` 3.6.5. Não use o Dashboard 2: os nós `ui_gauge`, `ui_chart` e `ui_template` deste arquivo pertencem ao pacote clássico.

## Importar

1. Instale o dashboard no diretório do Node-RED: `npm install node-red-dashboard@3.6.5`.
2. Inicie o Node-RED com `../tools/iniciar-node-red.sh`, para definir o CSV e o arquivo de limites.
3. Em `http://127.0.0.1:1880/`, abra o menu, escolha **Importar** e selecione `flows.json`.
4. Implante o fluxo.
5. Abra o painel em `http://127.0.0.1:1880/ui/`.

Se o Node-RED já tiver outro dashboard, a importação pode criar um segundo nó de configuração da interface. Nesse caso, mantenha um único `ui_base` e volte a implantar.

## O que o fluxo faz

- Assina `cocoalerta/monitoramento/estacao01/dados`, `.../status` e `.../alertas` no broker `broker.hivemq.com:1883`.
- Converte o payload em JSON e rejeita mensagem sem os campos obrigatórios ou com número fora da faixa física do sensor.
- Recalcula o risco com a mesma função de `shared/risk_engine.js`. O painel continua mostrando o risco enviado pela estação, que é o risco usado nos atuadores. Uma divergência aparece como aviso no painel de depuração.
- Acrescenta a leitura em `data/readings.csv` quando `COCO_ALERTA_DATA` está definido.
- Na inicialização, relê o CSV e reconstrói o histórico, os gráficos e as mudanças de classificação.
- Atualiza medidores, gráficos, os quatro estados e a tabela de ocorrências.
- Publica o CSV em `GET /coco-alerta/leituras.csv`.

Os grupos do fluxo são: entrada MQTT, validação e registro, armazenamento, exportação e painel.

## Atualizar a regra

A regra editável está em `shared/limites.json` e é copiada para `wokwi/limites.json`. O fluxo embute uma cópia para funcionar mesmo sem a variável de ambiente. Depois de alterar os números, rode:

```bash
python3 ../tools/gerar_fluxo.py
```

e importe o `flows.json` novamente. O firmware lê `wokwi/limites.json` diretamente, sem esse passo.
