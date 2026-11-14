import json

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_USUARIO = ""
MQTT_SENHA = ""

ESTACAO_ID = "estacao01"
TOPICO_BASE = "cocoalerta/monitoramento/" + ESTACAO_ID
TOPICO_DADOS = TOPICO_BASE + "/dados"
TOPICO_STATUS = TOPICO_BASE + "/status"
TOPICO_ALERTAS = TOPICO_BASE + "/alertas"
TOPICO_COMANDOS = TOPICO_BASE + "/comandos"

FUSO_SEGUNDOS = -3 * 3600
INTERVALO_MS = 5000

PINO_DHT = 14
PINO_DS18 = 4
PINO_MQ2 = 34
PINO_LED_VERDE = 25
PINO_LED_AMARELO = 26
PINO_LED_VERMELHO = 27
PINO_BUZZER = 32


def carregar_limites(caminho=None):
    if caminho is None:
        try:
            base = __file__
        except NameError:
            base = ""
        if "/" in base:
            caminho = base.rsplit("/", 1)[0] + "/limites.json"
        else:
            caminho = "limites.json"
    with open(caminho, "r") as arquivo:
        dados = json.load(arquivo)
    return dados["limites"], int(dados["persistencia_leituras"])


LIMITES, PERSISTENCIA = carregar_limites()
