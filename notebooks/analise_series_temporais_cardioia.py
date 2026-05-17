from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


RANDOM_SEED = 42
WINDOW_SIZE = 60
N_WINDOWS = 360


def generate_window(rng: np.random.Generator, risk: bool) -> dict[str, np.ndarray | int]:
    time = np.arange(WINDOW_SIZE)

    if risk:
        bpm_base = rng.choice([125, 135, 48])
        temperature_base = rng.choice([36.8, 38.4, 39.0])
        movement_prob = rng.choice([0.05, 0.2, 0.8])
        label = 1
    else:
        bpm_base = rng.normal(76, 8)
        temperature_base = rng.normal(36.6, 0.25)
        movement_prob = rng.uniform(0.65, 0.95)
        label = 0

    bpm = bpm_base + 4 * np.sin(time / 8) + rng.normal(0, 4, WINDOW_SIZE)
    temperature = temperature_base + rng.normal(0, 0.12, WINDOW_SIZE)
    movement = rng.binomial(1, movement_prob, WINDOW_SIZE)

    return {
        "bpm": bpm,
        "temperature": temperature,
        "movement": movement,
        "label": label,
    }


def build_dataset() -> tuple[list[dict[str, np.ndarray | int]], np.ndarray, np.ndarray]:
    rng = np.random.default_rng(RANDOM_SEED)
    windows = []
    labels = []
    features = []

    for index in range(N_WINDOWS):
        risk = index >= N_WINDOWS // 2
        sample = generate_window(rng, risk)
        windows.append(sample)
        labels.append(sample["label"])
        bpm = sample["bpm"]
        temperature = sample["temperature"]
        movement = sample["movement"]
        features.append(
            [
                float(np.mean(bpm)),
                float(np.std(bpm)),
                float(np.max(bpm)),
                float(np.min(bpm)),
                float(np.mean(temperature)),
                float(np.max(temperature)),
                float(np.mean(movement)),
                float(bpm[-1] - bpm[0]),
            ]
        )

    return windows, np.array(features), np.array(labels)


def train_logistic_regression(features: np.ndarray, labels: np.ndarray) -> dict[str, object]:
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=RANDOM_SEED,
        stratify=labels,
    )

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000, random_state=RANDOM_SEED)),
        ]
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    return {
        "model": model,
        "accuracy": accuracy_score(y_test, predictions),
        "f1": f1_score(y_test, predictions),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(y_test, predictions, output_dict=True),
    }


def lif_score(window: dict[str, np.ndarray | int]) -> int:
    bpm = window["bpm"]
    temperature = window["temperature"]
    movement = window["movement"]

    potential = 0.0
    spikes = 0
    threshold = 1.4
    leak = 0.88

    for bpm_value, temp_value, move_value in zip(bpm, temperature, movement):
        stimulus = 0.0
        if bpm_value > 120:
            stimulus += 0.55
        if bpm_value < 50:
            stimulus += 0.35
        if temp_value > 38:
            stimulus += 0.50
        if move_value == 0:
            stimulus += 0.08

        potential = potential * leak + stimulus
        if potential >= threshold:
            spikes += 1
            potential = 0.0

    return spikes


def evaluate_lif(windows: list[dict[str, np.ndarray | int]], labels: np.ndarray) -> dict[str, object]:
    scores = np.array([lif_score(window) for window in windows])
    predictions = (scores >= 2).astype(int)

    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions),
        "confusion_matrix": confusion_matrix(labels, predictions).tolist(),
        "classification_report": classification_report(labels, predictions, output_dict=True),
        "spike_threshold": 2,
    }


def main() -> None:
    windows, features, labels = build_dataset()
    logistic = train_logistic_regression(features, labels)
    lif = evaluate_lif(windows, labels)

    output = {
        "dataset": {
            "windows": len(windows),
            "window_size": WINDOW_SIZE,
            "features": [
                "bpm_mean",
                "bpm_std",
                "bpm_max",
                "bpm_min",
                "temperature_mean",
                "temperature_max",
                "movement_ratio",
                "bpm_trend",
            ],
        },
        "logistic_regression": {
            "accuracy": logistic["accuracy"],
            "f1": logistic["f1"],
            "confusion_matrix": logistic["confusion_matrix"],
        },
        "lif_neuromorphic": {
            "accuracy": lif["accuracy"],
            "f1": lif["f1"],
            "confusion_matrix": lif["confusion_matrix"],
            "spike_threshold": lif["spike_threshold"],
        },
    }

    output_dir = Path(__file__).resolve().parent / "resultados"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "metricas_series_temporais.json").write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
