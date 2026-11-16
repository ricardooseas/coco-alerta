import time

import config


class _FioUnico:
    """Protocolo 1-Wire em Python. O simulador enxerga estes pulsos."""

    def __init__(self, pino):
        from machine import Pin

        self._pin_cls = Pin
        self.pino = Pin(pino, Pin.OUT)
        self.pino.value(1)

    def _baixo(self):
        self.pino.init(self._pin_cls.OUT)
        self.pino.value(0)

    def _soltar(self):
        self.pino.init(self._pin_cls.IN, self._pin_cls.PULL_UP)

    def reset(self):
        self._baixo()
        time.sleep_us(480)
        self._soltar()
        time.sleep_us(70)
        presente = self.pino.value() == 0
        time.sleep_us(410)
        return presente

    def escrever_bit(self, bit):
        self._baixo()
        if bit:
            time.sleep_us(6)
            self._soltar()
            time.sleep_us(64)
        else:
            time.sleep_us(60)
            self._soltar()
            time.sleep_us(10)

    def ler_bit(self):
        self._baixo()
        time.sleep_us(6)
        self._soltar()
        time.sleep_us(9)
        valor = self.pino.value()
        time.sleep_us(55)
        return 1 if valor else 0

    def escrever_byte(self, valor):
        for _ in range(8):
            self.escrever_bit(valor & 1)
            valor >>= 1

    def ler_byte(self):
        valor = 0
        for indice in range(8):
            valor |= self.ler_bit() << indice
        return valor


class Sensores:
    def __init__(self):
        from machine import ADC, Pin
        import dht

        self._pin_cls = Pin
        self._dht = dht.DHT22(Pin(config.PINO_DHT))
        self._fio = _FioUnico(config.PINO_DS18)
        self._ds_biblioteca = None
        self._rom = None
        self._usar_fio_python = False
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
            import ds18x20
            import onewire

            barramento = onewire.OneWire(self._pin_cls(config.PINO_DS18))
            sensor = ds18x20.DS18X20(barramento)
            roms = sensor.scan()
        except Exception as erro:
            print("[sensor] falha ao procurar DS18B20:", erro)
            roms = []
            sensor = None
        if roms:
            self._ds_biblioteca = sensor
            self._rom = roms[0]
            self._usar_fio_python = False
            print("[sensor] DS18B20 localizado")
            return
        if self._fio.reset():
            self._usar_fio_python = True
            self._rom = True
            print("[sensor] DS18B20 localizado pelo protocolo do simulador")
            return
        print("[sensor] nenhum DS18B20 respondeu no GPIO", config.PINO_DS18)
        self._rom = None

    def iniciar_conversao(self):
        if self._rom is None:
            self._localizar_ds18()
        if self._rom is None:
            self._conversao_pendente = False
            return False
        try:
            if self._usar_fio_python:
                if not self._fio.reset():
                    raise OSError("sem presenca")
                self._fio.escrever_byte(0xCC)
                self._fio.escrever_byte(0x44)
            else:
                self._ds_biblioteca.convert_temp()
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
            if self._usar_fio_python:
                if not self._fio.reset():
                    raise OSError("sem presenca")
                self._fio.escrever_byte(0xCC)
                self._fio.escrever_byte(0xBE)
                bruto = self._fio.ler_byte() | (self._fio.ler_byte() << 8)
                if bruto & 0x8000:
                    bruto -= 65536
                return round(bruto / 16.0, 1)
            return round(self._ds_biblioteca.read_temp(self._rom), 1)
        except Exception as erro:
            print("[sensor] leitura do DS18B20 falhou:", erro)
            self._rom = None
            return None
        finally:
            self._conversao_pendente = False

    def _ler_dht_pulso(self):
        from machine import time_pulse_us

        pino = self._pin_cls(config.PINO_DHT, self._pin_cls.OUT)
        pino.value(0)
        time.sleep_ms(20)
        pino.value(1)
        time.sleep_us(30)
        pino.init(self._pin_cls.IN, self._pin_cls.PULL_UP)
        if time_pulse_us(pino, 0, 250) < 0 or time_pulse_us(pino, 1, 250) < 0:
            return None
        valor = 0
        for _ in range(40):
            if time_pulse_us(pino, 0, 200) < 0:
                return None
            alto = time_pulse_us(pino, 1, 200)
            if alto < 0:
                return None
            valor = (valor << 1) | (1 if alto > 50 else 0)
        dados = [(valor >> deslocamento) & 0xFF for deslocamento in (32, 24, 16, 8, 0)]
        if ((dados[0] + dados[1] + dados[2] + dados[3]) & 0xFF) != dados[4]:
            return None
        umidade = ((dados[0] << 8) | dados[1]) / 10.0
        temperatura = (((dados[2] & 0x7F) << 8) | dados[3]) / 10.0
        if dados[2] & 0x80:
            temperatura = -temperatura
        return round(temperatura, 1), round(umidade, 1)

    def ler_ambiente(self):
        try:
            self._dht.measure()
            return round(self._dht.temperature(), 1), round(self._dht.humidity(), 1)
        except Exception:
            pass
        try:
            leitura = self._ler_dht_pulso()
        except Exception as erro:
            print("[sensor] DHT22 indisponivel:", erro)
            return None, None
        if leitura is None:
            print("[sensor] DHT22 indisponivel: sem resposta do simulador")
            return None, None
        return leitura

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
