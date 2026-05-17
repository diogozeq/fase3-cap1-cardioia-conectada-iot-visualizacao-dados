from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    level: str
    reason: str
    should_alert: bool


def classify_vitals(bpm: int, temperature_c: float, movement: bool) -> RiskResult:
    """Classificacao inspirada na triagem de risco da Fase 2.

    A Fase 2 classificava frases clinicas como baixo/alto risco. Aqui a mesma
    ideia e aplicada a sinais vitais continuos recebidos do IoT.
    """
    reasons: list[str] = []

    if bpm > 120:
        reasons.append("possivel taquicardia: bpm acima de 120")
    if bpm < 50:
        reasons.append("possivel bradicardia: bpm abaixo de 50")
    if temperature_c > 38.0:
        reasons.append("possivel febre: temperatura acima de 38 C")
    if not movement:
        reasons.append("ausencia de movimento detectada")

    if len(reasons) >= 2:
        return RiskResult("alto", "; ".join(reasons), True)
    if reasons:
        return RiskResult("atencao", "; ".join(reasons), True)
    return RiskResult("normal", "sem alerta", False)
