import json
import time

import config
from umqtt.simple import MQTTClient


def _id_cliente():
    try:
        import machine
        import ubinascii

        sufixo = ubinascii.hexlify(machine.unique_id()).decode()
    except Exception:
        sufixo = "local"
    return "cocoalerta-" + config.ESTACAO_ID + "-" + sufixo


class ClienteMQTT:
    def __init__(self):
        self.wifi = None
        self.cliente = None
        self.wifi_ok = False
        self.conectado = False
        self.relogio_ok = False
        self.intervalo_ms = config.INTERVALO_MS
        self._proxima_rede = 0
        self._ultimo_ping = time.ticks_ms()
        self._id = _id_cliente()

    def conectar_wifi(self):
        agora = time.ticks_ms()
        if self.wifi_ok and time.ticks_diff(agora, self._proxima_rede) < 0:
            return True
        if time.ticks_diff(agora, self._proxima_rede) < 0:
            return False
        import network

        if self.wifi is None:
            self.wifi = network.WLAN(network.STA_IF)
            self.wifi.active(True)
        if self.wifi.isconnected():
            self.wifi_ok = True
            return True
        print("[wifi] conectando a", config.WIFI_SSID)
        self.wifi.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        inicio = time.ticks_ms()
        while not self.wifi.isconnected() and time.ticks_diff(time.ticks_ms(), inicio) < 8000:
            time.sleep_ms(200)
        self.wifi_ok = self.wifi.isconnected()
        self._proxima_rede = time.ticks_add(time.ticks_ms(), 10000)
        if self.wifi_ok:
            print("[wifi] conectado", self.wifi.ifconfig()[0])
            self.sincronizar_relogio()
        else:
            print("[wifi] sem conexao; a leitura local continua")
        return self.wifi_ok

    def sincronizar_relogio(self):
        if self.relogio_ok or not self.wifi_ok:
            return
        try:
            import ntptime

            if hasattr(ntptime, "timeout"):
                ntptime.timeout = 5
            ntptime.host = "pool.ntp.org"
            ntptime.settime()
            self.relogio_ok = True
            print("[relogio] sincronizado, fuso America/Fortaleza")
        except Exception as erro:
            print("[relogio] NTP indisponivel:", erro)

    def timestamp(self):
        if not self.relogio_ok:
            return None
        try:
            instante = time.time() + config.FUSO_SEGUNDOS
            ano, mes, dia, hora, minuto, segundo, *_resto = time.localtime(instante)
            return "%04d-%02d-%02dT%02d:%02d:%02d-03:00" % (ano, mes, dia, hora, minuto, segundo)
        except Exception as erro:
            print("[relogio] falha ao formatar horario:", erro)
            return None

    def conectar(self):
        if self.conectado:
            return True
        if not self.conectar_wifi():
            return False
        try:
            cliente = MQTTClient(
                self._id,
                config.MQTT_BROKER,
                port=config.MQTT_PORT,
                user=config.MQTT_USUARIO or None,
                password=config.MQTT_SENHA or None,
                keepalive=30,
            )
            cliente.set_callback(self._ao_receber)
            cliente.set_last_will(
                config.TOPICO_STATUS,
                json.dumps({"estacao_id": config.ESTACAO_ID, "status": "offline"}),
                retain=True,
            )
            cliente.connect()
            cliente.subscribe(config.TOPICO_COMANDOS)
            self.cliente = cliente
            self.conectado = True
            self._ultimo_ping = time.ticks_ms()
            print("[mqtt] conectado a", config.MQTT_BROKER)
            self.publicar_status()
            return True
        except Exception as erro:
            print("[mqtt] falha na conexao:", erro)
            self.conectado = False
            self.cliente = None
            return False

    def manter(self):
        if not self.wifi_ok or (self.wifi and not self.wifi.isconnected()):
            self.wifi_ok = False
            self.conectado = False
            self.conectar_wifi()
        if not self.conectado:
            self.conectar()
            return
        try:
            self.cliente.check_msg()
            if time.ticks_diff(time.ticks_ms(), self._ultimo_ping) > 15000:
                self.cliente.ping()
                self._ultimo_ping = time.ticks_ms()
        except Exception as erro:
            print("[mqtt] conexao interrompida:", erro)
            self.conectado = False
            self.cliente = None

    def _publicar(self, topico, carga, reter=False):
        if not self.conectado or self.cliente is None:
            return False
        try:
            self.cliente.publish(topico, json.dumps(carga), retain=reter)
            return True
        except Exception as erro:
            print("[mqtt] falha ao publicar em", topico, ":", erro)
            self.conectado = False
            self.cliente = None
            return False

    def publicar_dados(self, carga):
        ok = self._publicar(config.TOPICO_DADOS, carga)
        if ok:
            print("[mqtt] dados publicados")
        return ok

    def publicar_alerta(self, carga):
        ok = self._publicar(config.TOPICO_ALERTAS, carga)
        if ok:
            print("[mqtt] alerta publicado")
        return ok

    def publicar_status(self):
        carga = {
            "estacao_id": config.ESTACAO_ID,
            "status": "online",
            "intervalo_s": int(self.intervalo_ms / 1000),
            "timestamp": self.timestamp(),
        }
        return self._publicar(config.TOPICO_STATUS, carga, reter=True)

    def _ao_receber(self, topico, mensagem):
        try:
            texto = mensagem.decode() if isinstance(mensagem, bytes) else mensagem
            dados = json.loads(texto)
        except Exception:
            print("[mqtt] comando ignorado: JSON invalido")
            return
        if dados.get("comando") != "intervalo":
            print("[mqtt] comando nao reconhecido")
            return
        try:
            valor = int(dados.get("valor"))
        except Exception:
            print("[mqtt] intervalo invalido")
            return
        if valor < 3:
            valor = 3
        if valor > 60:
            valor = 60
        self.intervalo_ms = valor * 1000
        print("[mqtt] intervalo alterado para", valor, "s")
        self.publicar_status()
