import time

import config


class Sensores:
    def __init__(self):
        from machine import ADC, Pin
        import dht
        import ds18x20
        import onewire

        self._dht = dht.DHT22(Pin(config.PINO_DHT))
        self._barramento = onewire.OneWire(Pin(config.PINO_DS18))
        self._ds = ds18x20.DS18X20(self._barramento)
        self._rom = None
        self._conversao_pendente = False
        self._localizar_ds18()

        self._adc = ADC(Pin(config.PINO_MQ2))
        try:
            self._adc.atten(ADC.ATTN_11DB)
        except Exception as erro:
            print("[sensor] atenuacao do ADC indisponivel:", erro)
        try:
            self._adc.width(ADC.WIDTH_12BIT)
        except Exception:
            pass

    def _localizar_ds18(self):
        try:
            roms = self._ds.scan()
        except Exception as erro:
            print("[sensor] falha ao procurar DS18B20:", erro)
            self._rom = None
            return
        if not roms:
            print("[sensor] nenhum DS18B20 respondeu no GPIO", config.PINO_DS18)
            self._rom = None
            return
        self._rom = roms[0]
        print("[sensor] DS18B20 localizado")

    def iniciar_conversao(self):
        if self._rom is None:
            self._localizar_ds18()
        if self._rom is None:
            self._conversao_pendente = False
            return False
        try:
            self._ds.convert_temp()
            self._conversao_pendente = True
            return True
        except Exception as erro:
            print("[sensor] DS18B20 nao iniciou a conversao:", erro)
            self._rom = None
            self._conversao_pendente = False
            return False

    def ler_solo(self):
        if not self._conversao_pendente or self._rom is None:
            return None
        try:
            return round(self._ds.read_temp(self._rom), 1)
        except Exception as erro:
            print("[sensor] leitura do DS18B20 falhou:", erro)
            self._rom = None
            return None
        finally:
            self._conversao_pendente = False

    def ler_ambiente(self):
        ultimo_erro = None
        for tentativa in (1, 2):
            try:
                self._dht.measure()
                return round(self._dht.temperature(), 1), round(self._dht.humidity(), 1)
            except Exception as erro:
                ultimo_erro = erro
                time.sleep_ms(200)
        print("[sensor] DHT22 indisponivel:", ultimo_erro)
        return None, None

    def ler_fumaca(self):
        try:
            total = 0
            for _ in range(8):
                if hasattr(self._adc, "read"):
                    total += self._adc.read()
                else:
                    total += self._adc.read_u16() >> 4
                time.sleep_ms(2)
            return int(total / 8)
        except Exception as erro:
            print("[sensor] MQ-2 indisponivel:", erro)
            return None
