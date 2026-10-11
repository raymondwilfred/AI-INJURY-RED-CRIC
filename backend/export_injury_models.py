"""Reproduce the notebook MLP exports if cricket_player_data_fixed.csv is present.

This does not retrain YOLO. It repeats the notebook's sklearn fit/dump steps
with the same hyperparameters and random_state=42.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler


def mlp() -> MLPClassifier:
    return MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        alpha=0.0001,
        learning_rate_init=0.001,
        max_iter=1000,
        early_stopping=False,
        random_state=42,
    )


def export_tabular(df: pd.DataFrame, out_dir: Path) -> None:
    data = df.drop(columns=["player_id"])
    encoder = LabelEncoder()
    data["player_type"] = encoder.fit_transform(data["player_type"])
    X = data.drop(columns=["injury_risk"])
    y = data["injury_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.20, random_state=42, stratify=y_train
    )
    del X_test, y_test, X_val, y_val

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    model = mlp()
    model.fit(np.asarray(X_train_scaled, dtype=np.float64), y_train)

    joblib.dump(model, out_dir / "mlp_injury_risk_model.pkl")
    joblib.dump(scaler, out_dir / "feature_scaler.pkl")
    joblib.dump(list(X.columns), out_dir / "feature_columns.pkl")


def export_fusion(df: pd.DataFrame, out_dir: Path) -> None:
    fusion_df = df.copy()
    fusion_df["player_type"] = fusion_df["player_type"].map(
        {"All-Rounder": 0, "Batsman": 1, "Bowler": 2}
    )
    X_fusion = fusion_df.drop(columns=["player_id", "injury_risk"])
    np.random.seed(42)
    n = len(X_fusion)
    X_fusion["left_knee_angle"] = np.random.uniform(70, 170, n)
    X_fusion["right_knee_angle"] = np.random.uniform(70, 170, n)
    X_fusion["trunk_angle"] = np.random.uniform(-30, 30, n)
    X_fusion["shoulder_line_angle"] = np.random.uniform(-45, 45, n)
    X_fusion["hip_line_angle"] = np.random.uniform(-30, 30, n)
    X_fusion["shoulder_hip_angle_difference"] = np.random.uniform(0, 90, n)
    y_fusion = fusion_df["injury_risk"]

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X_fusion, y_fusion, test_size=0.20, random_state=42, stratify=y_fusion
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.20,
        random_state=42,
        stratify=y_train_val,
    )
    del X_test, y_test, X_val, y_val

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    model = mlp()
    model.fit(X_train_scaled, y_train)

    joblib.dump(model, out_dir / "fusion_mlp_model.pkl")
    joblib.dump(scaler, out_dir / "fusion_scaler.pkl")
    joblib.dump(X_fusion.columns.tolist(), out_dir / "fusion_feature_columns.pkl")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parents[1] / "models"),
    )
    args = parser.parse_args()
    csv_path = Path(args.csv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)
    export_tabular(df, out_dir)
    export_fusion(df, out_dir)
    print("Exported tabular and fusion MLP files to", out_dir)


if __name__ == "__main__":
    main()
