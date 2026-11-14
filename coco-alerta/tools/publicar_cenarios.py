import json
import sys
import time
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "wokwi"))

import config
from risk_engine import MotorRisco
from umqtt.simple import MQTTClient

# Cada item precisa se repetir para a persistencia confirmar a classificacao.
# origem=teste identifica que estas leituras nao vieram dos sensores do Wokwi.
CENARIO = [
    ("normal", 27, 31, 68, 350),
    ("normal", 27.5, 31.2, 67, 360),
    ("normal", 28, 31.4, 66, 340),
    ("normal", 27.8, 31, 68, 355),
    ("atencao", 28, 38, 60, 400),
    ("atencao", 28.2, 38.5, 58, 420),
    ("atencao", 28, 39, 55, 450),
    ("atencao", 29, 38.2, 57, 410),
    ("alerta", 45, 33, 55, 2000),
    ("alerta", 46, 34, 52, 2100),
    ("alerta", 45.5, 33.5, 50, 2200),
    ("alerta", 47, 34, 48, 2050),
    ("emergencia", 55, 46, 20, 3000),
    ("emergencia", 56, 47, 18, 3200),
    ("emergencia", 55.5, 46.5, 19, 3100),
    ("emergencia", 57, 48, 17, 3300),
    ("retorno", 27, 31, 68, 350),
    ("retorno", 27.2, 31.1, 69, 340),
    ("retorno", 27, 30.8, 70, 330),
    ("retorno", 27.4, 31, 68, 345),
    ("retorno", 27.1, 31.3, 67, 350),
    ("retorno", 27, 31, 68, 348),
]


def atuadores(risco):
    return {
        "led_verde": risco == "NORMAL",
        "led_amarelo": risco == "ATENÇÃO",
        "led_vermelho": risco in ("ALERTA", "EMERGÊNCIA"),
        "buzzer": risco in ("ALERTA", "EMERGÊNCIA"),
    }


def main():
    broker = sys.argv[1] if len(sys.argv) > 1 else config.MQTT_BROKER
    motor = MotorRisco(config.LIMITES, config.PERSISTENCIA)
    cliente = MQTTClient("cocoalerta-teste-" + uuid.uuid4().hex[:8], broker, keepalive=30)
    cliente.connect()
    cliente.publish(
        config.TOPICO_STATUS,
        json.dumps({"estacao_id": config.ESTACAO_ID, "status": "online", "intervalo_s": 5}),
        retain=True,
    )
    print("Publicando", len(CENARIO), "leituras de teste em", broker)
    for indice, (nome, solo, ambiente, umidade, fumaca) in enumerate(CENARIO, start=1):
        risco = motor.avaliar(solo, ambiente, umidade, fumaca)
        carga = {
            "estacao_id": config.ESTACAO_ID,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S-03:00", time.gmtime(time.time() - 3 * 3600)),
            "temperatura_solo": solo,
            "temperatura_ambiente": ambiente,
            "umidade": umidade,
            "fumaca": fumaca,
            "risco": risco,
            "atuadores": atuadores(risco),
            "origem": "teste",
            "intervalo_s": 5,
            "cenario": nome,
        }
        cliente.publish(config.TOPICO_DADOS, json.dumps(carga, ensure_ascii=False))
        print("%02d %-12s risco=%s" % (indice, nome, risco))
        time.sleep(0.25)
    cliente.disconnect()
    print("Publicacao encerrada. Estas leituras sao dados de teste, nao medicoes do parque.")


if __name__ == "__main__":
    main()
