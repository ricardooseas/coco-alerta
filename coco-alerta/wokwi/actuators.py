import time

from machine import PWM, Pin

import config


class Atuadores:
    def __init__(self):
        self.led_verde = Pin(config.PINO_LED_VERDE, Pin.OUT)
        self.led_amarelo = Pin(config.PINO_LED_AMARELO, Pin.OUT)
        self.led_vermelho = Pin(config.PINO_LED_VERMELHO, Pin.OUT)
        self.buzzer = PWM(Pin(config.PINO_BUZZER))
        self.buzzer.freq(2000)
        self._duty(0)
        self.risco = "NORMAL"
        self._inicio = time.ticks_ms()
        self._aplicar_leds(False, False, False)
        self.estado = {
            "led_verde": False,
            "led_amarelo": False,
            "led_vermelho": False,
            "buzzer": False,
        }

    def _duty(self, valor):
        try:
            self.buzzer.duty(valor)
        except AttributeError:
            self.buzzer.duty_u16(int(valor) * 64)

    def _aplicar_leds(self, verde, amarelo, vermelho):
        self.led_verde.value(1 if verde else 0)
        self.led_amarelo.value(1 if amarelo else 0)
        self.led_vermelho.value(1 if vermelho else 0)

    def aplicar(self, risco):
        self.risco = risco
        self._inicio = time.ticks_ms()
        if risco == "ATENÇÃO":
            self._aplicar_leds(False, True, False)
            self._duty(0)
            self.estado = {
                "led_verde": False,
                "led_amarelo": True,
                "led_vermelho": False,
                "buzzer": False,
            }
        elif risco == "ALERTA":
            self._aplicar_leds(False, False, True)
            self.estado = {
                "led_verde": False,
                "led_amarelo": False,
                "led_vermelho": True,
                "buzzer": True,
            }
        elif risco == "EMERGÊNCIA":
            self._aplicar_leds(False, False, True)
            self.estado = {
                "led_verde": False,
                "led_amarelo": False,
                "led_vermelho": True,
                "buzzer": True,
            }
        else:
            self._aplicar_leds(True, False, False)
            self._duty(0)
            self.estado = {
                "led_verde": True,
                "led_amarelo": False,
                "led_vermelho": False,
                "buzzer": False,
            }
        return self.estado

    def atualizar(self):
        if self.risco not in ("ALERTA", "EMERGÊNCIA"):
            return
        periodo = 400 if self.risco == "EMERGÊNCIA" else 1000
        fase = time.ticks_diff(time.ticks_ms(), self._inicio) % periodo
        if fase < 180:
            self._duty(512)
            self.led_vermelho.value(1)
        else:
            self._duty(0)
            self.led_vermelho.value(0 if self.risco == "EMERGÊNCIA" else 1)
