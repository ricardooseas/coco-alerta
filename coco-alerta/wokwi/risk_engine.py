# Mesma regra de shared/limites.json, shared/risk_engine.js e docs/regras-de-risco.md.

ORDEM_RISCO = {"NORMAL": 0, "ATENÇÃO": 1, "ALERTA": 2, "EMERGÊNCIA": 3}


def faixa_alto(valor, atencao, alerta, emergencia):
    if valor >= emergencia:
        return 3
    if valor >= alerta:
        return 2
    if valor >= atencao:
        return 1
    return 0


def faixa_baixo(valor, atencao, alerta, emergencia):
    if valor <= emergencia:
        return 3
    if valor <= alerta:
        return 2
    if valor <= atencao:
        return 1
    return 0


def classificar_instantaneo(solo, ambiente, umidade, fumaca, limites):
    n_solo = faixa_alto(
        solo,
        limites["temperatura_solo_atencao"],
        limites["temperatura_solo_alerta"],
        limites["temperatura_solo_emergencia"],
    )
    n_ambiente = faixa_alto(
        ambiente,
        limites["temperatura_ambiente_atencao"],
        limites["temperatura_ambiente_alerta"],
        limites["temperatura_ambiente_emergencia"],
    )
    n_umidade = faixa_baixo(
        umidade,
        limites["umidade_atencao"],
        limites["umidade_alerta"],
        limites["umidade_emergencia"],
    )
    n_fumaca = faixa_alto(
        fumaca,
        limites["fumaca_atencao"],
        limites["fumaca_alerta"],
        limites["fumaca_emergencia"],
    )
    termico = n_solo if n_solo > n_ambiente else n_ambiente

    if n_solo >= 3 and n_fumaca >= 3 and (n_ambiente >= 3 or n_umidade >= 3):
        return "EMERGÊNCIA"
    if termico >= 2 and n_fumaca >= 2:
        return "ALERTA"
    if n_solo >= 1 or n_ambiente >= 1 or n_umidade >= 1 or n_fumaca >= 1:
        return "ATENÇÃO"
    return "NORMAL"


def avaliar_estado(estado, solo, ambiente, umidade, fumaca, limites, persistencia):
    candidato = classificar_instantaneo(solo, ambiente, umidade, fumaca, limites)
    recentes = list(estado.get("recentes", []))
    recentes.append(candidato)
    if len(recentes) > persistencia:
        recentes = recentes[-persistencia:]
    atual = estado.get("atual", "NORMAL")
    if len(recentes) == persistencia and all(item == candidato for item in recentes):
        atual = candidato
    elif ORDEM_RISCO[candidato] < ORDEM_RISCO[atual]:
        atual = candidato
        recentes = [candidato] * persistencia
    return {"atual": atual, "recentes": recentes, "instantaneo": candidato}


def simular_sequencia(sequencia, limites, persistencia):
    estado = {"atual": "NORMAL", "recentes": []}
    saidas = []
    for solo, ambiente, umidade, fumaca in sequencia:
        estado = avaliar_estado(estado, solo, ambiente, umidade, fumaca, limites, persistencia)
        saidas.append(estado["atual"])
    return saidas


class MotorRisco:
    """Estado de persistencia usado pelo firmware."""

    def __init__(self, limites, persistencia):
        self.limites = limites
        self.persistencia = persistencia
        self.estado = {"atual": "NORMAL", "recentes": []}

    def avaliar(self, solo, ambiente, umidade, fumaca):
        self.estado = avaliar_estado(
            self.estado, solo, ambiente, umidade, fumaca, self.limites, self.persistencia
        )
        return self.estado["atual"]
