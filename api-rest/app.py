from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from emailer import send_alert_email
from risk import classify_vitals

app = FastAPI(
    title="CardioIA Fase 3 - API REST",
    description="Recebe sinais vitais, classifica risco e dispara e-mail em caso de alerta.",
    version="1.0.0",
)


class VitalPayload(BaseModel):
    patient_id: str = Field(default="cardioia-paciente-001")
    temperature_c: float
    humidity_pct: float = Field(default=55.0)
    bpm: int
    movement: bool = True
    source: str = Field(default="api-rest")


class StoredVital(VitalPayload):
    received_at: str
    risk_level: str
    alert_reason: str


vitals: list[StoredVital] = []
alerts: list[dict[str, Any]] = []


@app.get("/")
def health() -> dict[str, str]:
    return {"service": "CardioIA Fase 3 API", "status": "online"}


@app.post("/vitals", response_model=StoredVital)
def create_vital(payload: VitalPayload) -> StoredVital:
    risk = classify_vitals(payload.bpm, payload.temperature_c, payload.movement)
    stored = StoredVital(
        **payload.model_dump(),
        received_at=datetime.now(timezone.utc).isoformat(),
        risk_level=risk.level,
        alert_reason=risk.reason,
    )
    vitals.append(stored)

    if risk.should_alert:
        alert = {
            "patient_id": payload.patient_id,
            "received_at": stored.received_at,
            "risk_level": risk.level,
            "reason": risk.reason,
            "vitals": payload.model_dump(),
            "email_sent": False,
        }
        try:
            alert["email_sent"] = send_alert_email(
                subject=f"CardioIA alerta {risk.level} - {payload.patient_id}",
                body=(
                    f"Paciente: {payload.patient_id}\n"
                    f"Risco: {risk.level}\n"
                    f"Motivo: {risk.reason}\n"
                    f"BPM: {payload.bpm}\n"
                    f"Temperatura: {payload.temperature_c} C\n"
                    f"Movimento: {payload.movement}\n"
                    f"Recebido em: {stored.received_at}\n"
                ),
            )
        except Exception as exc:  # Mantem a API funcional e registra a falha.
            alert["email_error"] = str(exc)
        alerts.append(alert)

    return stored


@app.get("/vitals/latest", response_model=StoredVital)
def latest_vital() -> StoredVital:
    if not vitals:
        raise HTTPException(status_code=404, detail="Nenhuma leitura recebida")
    return vitals[-1]


@app.get("/alerts")
def list_alerts() -> list[dict[str, Any]]:
    return alerts


@app.post("/simulate", response_model=StoredVital)
def simulate_risk() -> StoredVital:
    return create_vital(
        VitalPayload(
            patient_id="cardioia-paciente-001",
            temperature_c=38.7,
            humidity_pct=58.0,
            bpm=132,
            movement=False,
            source="simulador-api",
        )
    )
