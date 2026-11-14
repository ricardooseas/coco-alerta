import sys
import time

import config
from actuators import Atuadores
from mqtt_client import ClienteMQTT
from risk_engine import MotorRisco
from sensors import Sensores


def esperar(mqtt, atuadores, milissegundos):
    limite = time.ticks_add(time.ticks_ms(), milissegundos)
    while time.ticks_diff(limite, time.ticks_ms()) > 0:
        mqtt.manter()
        atuadores.atualizar()
        time.sleep_ms(20)


def montar_leitura(mqtt, sensores, motor, atuadores):
    sensores.iniciar_conversao()
    esperar(mqtt, atuadores, 750)
    solo = sensores.ler_solo()
    ambiente, umidade = sensores.ler_ambiente()
    fumaca = sensores.ler_fumaca()
    if None in (solo, ambiente, umidade, fumaca):
        print(
            "[leitura] incompleta solo=%s ambiente=%s umidade=%s fumaca=%s"
            % (solo, ambiente, umidade, fumaca)
        )
        return None
    risco = motor.avaliar(solo, ambiente, umidade, fumaca)
    atuadores_estado = atuadores.aplicar(risco)
    return {
        "estacao_id": config.ESTACAO_ID,
        "timestamp": mqtt.timestamp(),
        "temperatura_solo": solo,
        "temperatura_ambiente": ambiente,
        "umidade": umidade,
        "fumaca": fumaca,
        "risco": risco,
        "atuadores": atuadores_estado,
        "origem": "firmware",
        "intervalo_s": int(mqtt.intervalo_ms / 1000),
    }


def publicar(mqtt, leitura, risco_anterior):
    import json

    print("[leitura]", json.dumps(leitura))
    mqtt.publicar_dados(leitura)
    if leitura["risco"] != risco_anterior:
        evento = dict(leitura)
        evento["risco_anterior"] = risco_anterior
        evento["evento"] = "mudanca_de_risco"
        mqtt.publicar_alerta(evento)


def principal():
    print("Coco Alerta - prototipo experimental de monitoramento")
    print("Estacao", config.ESTACAO_ID, "broker", config.MQTT_BROKER)
    sensores = Sensores()
    atuadores = Atuadores()
    motor = MotorRisco(config.LIMITES, config.PERSISTENCIA)
    mqtt = ClienteMQTT()
    risco_anterior = None
    proxima = time.ticks_ms()

    while True:
        try:
            mqtt.manter()
            atuadores.atualizar()
            if time.ticks_diff(time.ticks_ms(), proxima) >= 0:
                inicio_ciclo = time.ticks_ms()
                leitura = montar_leitura(mqtt, sensores, motor, atuadores)
                proxima = time.ticks_add(inicio_ciclo, mqtt.intervalo_ms)
                if leitura is not None:
                    publicar(mqtt, leitura, risco_anterior)
                    risco_anterior = leitura["risco"]
            time.sleep_ms(20)
        except Exception as erro:
            sys.print_exception(erro)
            print("[sistema] falha no ciclo; nova tentativa")
            time.sleep_ms(1000)


principal()
