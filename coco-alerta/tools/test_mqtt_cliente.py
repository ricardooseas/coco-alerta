import json
import sys
import time
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "wokwi"))

from umqtt.simple import MQTTClient


def exercitar(broker):
    sufixo = uuid.uuid4().hex[:8]
    topico = "cocoalerta/teste/conexao/" + sufixo
    recebido = {}

    def ao_receber(topic, mensagem):
        recebido["topico"] = topic.decode() if isinstance(topic, bytes) else topic
        recebido["mensagem"] = mensagem.decode() if isinstance(mensagem, bytes) else mensagem

    assinante = MQTTClient("cocoalerta-teste-sub-" + sufixo, broker, keepalive=30)
    publicador = MQTTClient("cocoalerta-teste-pub-" + sufixo, broker, keepalive=30)
    assinante.set_callback(ao_receber)
    assinante.connect()
    assinante.subscribe(topico)
    publicador.connect()
    carga = {"ok": True, "origem": "teste-cliente"}
    publicador.publish(topico, json.dumps(carga))
    limite = time.time() + 8
    while time.time() < limite and "mensagem" not in recebido:
        assinante.check_msg()
        time.sleep(0.2)
    publicador.disconnect()
    assinante.disconnect()
    if recebido.get("topico") != topico:
        raise RuntimeError("topico nao recebido: %s" % recebido)
    if json.loads(recebido["mensagem"]) != carga:
        raise RuntimeError("carga diferente: %s" % recebido["mensagem"])
    return topico


def main():
    broker = sys.argv[1] if len(sys.argv) > 1 else "broker.hivemq.com"
    topico = exercitar(broker)
    print("MQTT aprovado no broker", broker, "topico", topico)


if __name__ == "__main__":
    main()
