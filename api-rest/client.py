from __future__ import annotations

import argparse

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente REST CardioIA Fase 3")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--simulate-risk", action="store_true")
    args = parser.parse_args()

    if args.simulate_risk:
        payload = {
            "patient_id": "cardioia-paciente-001",
            "temperature_c": 38.8,
            "humidity_pct": 57.0,
            "bpm": 128,
            "movement": False,
            "source": "client.py",
        }
    else:
        payload = {
            "patient_id": "cardioia-paciente-001",
            "temperature_c": 36.7,
            "humidity_pct": 55.0,
            "bpm": 76,
            "movement": True,
            "source": "client.py",
        }

    response = requests.post(f"{args.base_url}/vitals", json=payload, timeout=10)
    response.raise_for_status()
    print(response.json())

    alerts = requests.get(f"{args.base_url}/alerts", timeout=10)
    alerts.raise_for_status()
    print({"alerts": alerts.json()})


if __name__ == "__main__":
    main()
