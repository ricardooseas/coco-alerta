try:
    import usocket as socket
except ImportError:
    import socket

try:
    import ustruct as struct
except ImportError:
    import struct


def _bytes(valor):
    if valor is None:
        return b""
    if isinstance(valor, bytes):
        return valor
    return str(valor).encode("utf-8")


def _restante(tamanho):
    saida = bytearray()
    while True:
        byte = tamanho & 0x7F
        tamanho >>= 7
        if tamanho:
            byte |= 0x80
        saida.append(byte)
        if not tamanho:
            return saida


def _temporario(erro):
    numero = erro.args[0] if erro.args else None
    if isinstance(numero, int) and numero in (11, 35, 60, 110, 116):
        return True
    nome = erro.__class__.__name__
    return nome in ("timeout", "TimeoutError")


class _SocketPadrao:
    """Adapta o socket da CPython para a interface read/write do MicroPython."""

    def __init__(self, bruto):
        self._bruto = bruto

    def write(self, dados, tamanho=None):
        if tamanho is not None:
            dados = dados[:tamanho]
        self._bruto.sendall(dados)

    def read(self, quantidade):
        blocos = []
        faltam = quantidade
        while faltam:
            try:
                parte = self._bruto.recv(faltam)
            except (TimeoutError, socket.timeout):
                if not blocos:
                    return None
                raise
            except OSError as erro:
                if _temporario(erro) and not blocos:
                    return None
                raise
            if not parte:
                break
            blocos.append(parte)
            faltam -= len(parte)
        return b"".join(blocos)

    def settimeout(self, segundos):
        self._bruto.settimeout(segundos)

    def close(self):
        self._bruto.close()


class MQTTException(Exception):
    pass


class MQTTClient:
    def __init__(self, client_id, server, port=1883, user=None, password=None, keepalive=30):
        self.client_id = _bytes(client_id)
        self.server = server
        self.port = port
        self.user = _bytes(user) if user else b""
        self.password = _bytes(password) if password else b""
        self.keepalive = keepalive
        self.sock = None
        self.cb = None
        self.pid = 0
        self.lw_topic = None
        self.lw_msg = None
        self.lw_retain = False

    def _timeout(self, segundos):
        try:
            self.sock.settimeout(segundos)
        except Exception:
            try:
                self.sock.setblocking(segundos != 0)
            except Exception:
                pass

    def set_callback(self, callback):
        self.cb = callback

    def set_last_will(self, topic, msg, retain=False, qos=0):
        if qos != 0:
            raise MQTTException("este cliente suporta somente QoS 0")
        self.lw_topic = _bytes(topic)
        self.lw_msg = _bytes(msg)
        self.lw_retain = retain

    def _enviar(self, dados):
        self.sock.write(dados)

    def _ler(self, quantidade):
        blocos = []
        faltam = quantidade
        while faltam:
            try:
                parte = self.sock.read(faltam)
            except OSError as erro:
                if _temporario(erro) and not blocos:
                    return None
                raise
            if parte is None:
                if not blocos:
                    return None
                raise OSError("leitura MQTT incompleta")
            if parte == b"":
                raise OSError("conexao MQTT encerrada")
            blocos.append(parte)
            faltam -= len(parte)
        return b"".join(blocos)

    def _texto(self, valor):
        codificado = _bytes(valor)
        self._enviar(struct.pack("!H", len(codificado)) + codificado)

    def connect(self, clean_session=True):
        bruto = socket.socket()
        try:
            bruto.settimeout(10)
        except Exception:
            pass
        endereco = socket.getaddrinfo(self.server, self.port)[0][-1]
        bruto.connect(endereco)
        if hasattr(bruto, "read") and hasattr(bruto, "write"):
            self.sock = bruto
        else:
            self.sock = _SocketPadrao(bruto)

        flags = 0x02 if clean_session else 0x00
        carga = struct.pack("!H", len(self.client_id)) + self.client_id
        if self.lw_topic:
            flags |= 0x04
            if self.lw_retain:
                flags |= 0x20
            carga += struct.pack("!H", len(self.lw_topic)) + self.lw_topic
            carga += struct.pack("!H", len(self.lw_msg)) + self.lw_msg
        if self.user:
            flags |= 0x80
            carga += struct.pack("!H", len(self.user)) + self.user
            if self.password:
                flags |= 0x40
                carga += struct.pack("!H", len(self.password)) + self.password

        variavel = b"\x00\x04MQTT\x04" + struct.pack("!BH", flags, self.keepalive)
        pacote = variavel + carga
        self._enviar(b"\x10" + _restante(len(pacote)) + pacote)

        resposta = self._ler(4)
        if resposta is None or resposta[0] != 0x20 or resposta[1] != 0x02:
            raise MQTTException("CONNACK invalido")
        if resposta[3] != 0:
            raise MQTTException("broker recusou a conexao: %s" % resposta[3])
        return resposta[2] & 1

    def disconnect(self):
        try:
            self._enviar(b"\xe0\x00")
        finally:
            if self.sock:
                self.sock.close()
                self.sock = None

    def ping(self):
        self._enviar(b"\xc0\x00")

    def publish(self, topic, msg, retain=False, qos=0):
        if qos != 0:
            raise MQTTException("este cliente suporta somente QoS 0")
        topico = _bytes(topic)
        mensagem = _bytes(msg)
        corpo = struct.pack("!H", len(topico)) + topico + mensagem
        cabecalho = 0x31 if retain else 0x30
        self._enviar(bytes([cabecalho]) + _restante(len(corpo)) + corpo)

    def subscribe(self, topic, qos=0):
        if qos != 0:
            raise MQTTException("este cliente suporta somente QoS 0")
        if self.cb is None:
            raise MQTTException("callback de assinatura nao definido")
        topico = _bytes(topic)
        self.pid = (self.pid + 1) & 0xFFFF
        if self.pid == 0:
            self.pid = 1
        corpo = struct.pack("!H", self.pid) + struct.pack("!H", len(topico)) + topico + b"\x00"
        self._enviar(b"\x82" + _restante(len(corpo)) + corpo)
        self._timeout(5)
        resposta = self._ler(1)
        if resposta != b"\x90":
            raise MQTTException("SUBACK invalido")
        tamanho = self._ler_restante()
        carga = self._ler(tamanho)
        if carga[:2] != struct.pack("!H", self.pid) or carga[-1] == 0x80:
            raise MQTTException("assinatura recusada")

    def _ler_restante(self):
        multiplicador = 1
        valor = 0
        for _ in range(4):
            byte = self._ler(1)[0]
            valor += (byte & 0x7F) * multiplicador
            if not byte & 0x80:
                return valor
            multiplicador *= 128
        raise MQTTException("tamanho restante invalido")

    def check_msg(self):
        self._timeout(0)
        try:
            primeiro = self.sock.read(1)
        except OSError as erro:
            if _temporario(erro):
                return None
            raise
        if primeiro is None:
            return None
        if primeiro == b"":
            raise OSError("conexao MQTT encerrada")
        self._timeout(5)
        tipo = primeiro[0] & 0xF0
        tamanho = self._ler_restante()
        if tipo == 0xD0:
            return None
        if tipo != 0x30:
            if tamanho:
                self._ler(tamanho)
            return None
        carga = self._ler(tamanho)
        tamanho_topico = struct.unpack("!H", carga[:2])[0]
        topico = carga[2:2 + tamanho_topico]
        mensagem = carga[2 + tamanho_topico:]
        if self.cb:
            self.cb(topico, mensagem)
        return 0x30
