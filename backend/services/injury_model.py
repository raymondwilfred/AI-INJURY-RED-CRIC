from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd


PLAYER_FIELDS = [
    "age",
    "player_type",
    "experience_years",
    "height_cm",
    "weight_kg",
    "bmi",
    "body_fat_percent",
    "training_hours_week",
    "bowling_overs_week",
    "batting_hours_week",
    "strength_training_hours",
    "matches_last_month",
    "days_since_last_match",
    "previous_injuries_count",
    "last_injury_days_ago",
    "recovery_days_last_injury",
    "fatigue_level",
    "sleep_hours_day",
    "stress_level",
    "fitness_score",
]


class InjuryModelUnavailable(Exception):
    pass


class InvalidPlayerFields(Exception):
    pass


class InjuryModelService:

    PLAYER_FIELDS = PLAYER_FIELDS

    PLAYER_TYPE_MAP = {
        "All-Rounder": "All-Rounder",
        "All Rounder": "All-Rounder",
        "All-rounder": "All-Rounder",
        "Batsman": "Batsman",
        "Batter": "Batsman",
        "Bowler": "Bowler",
    }

    NUMERIC_FIELDS = [
        "age",
        "experience_years",
        "height_cm",
        "weight_kg",
        "bmi",
        "body_fat_percent",
        "training_hours_week",
        "bowling_overs_week",
        "batting_hours_week",
        "strength_training_hours",
        "matches_last_month",
        "days_since_last_match",
        "previous_injuries_count",
        "last_injury_days_ago",
        "recovery_days_last_injury",
        "fatigue_level",
        "sleep_hours_day",
        "stress_level",
        "fitness_score",
    ]

    def __init__(self, models_dir: Path):

        self.models_dir = Path(models_dir)

        self.model = None
        self.scaler = None
        self.feature_columns = None

        self.model_path = (
            self.models_dir / "mlp_injury_risk_model.pkl"
        )

        self.scaler_path = (
            self.models_dir / "feature_scaler.pkl"
        )

        self.features_path = (
            self.models_dir / "feature_columns.pkl"
        )

        # Dataset used for similarity checking.
        self.dataset_path = (
            self.models_dir.parent
            / "data"
            / "cricket_player_data_fixed.csv"
        )

        self.reference_data = None
        self.reference_scaled = None
        self.reference_labels = None

        self._load_model()
        self._load_reference_data()

    # ---------------------------------------------------------
    # LOAD MLP
    # ---------------------------------------------------------

    def _load_model(self):

        missing = []

        if not self.model_path.exists():
            missing.append(str(self.model_path))

        if not self.scaler_path.exists():
            missing.append(str(self.scaler_path))

        if not self.features_path.exists():
            missing.append(str(self.features_path))

        if missing:

            self.model = None
            self.scaler = None
            self.feature_columns = None

            return

        try:

            self.model = joblib.load(
                self.model_path
            )

            self.scaler = joblib.load(
                self.scaler_path
            )

            self.feature_columns = joblib.load(
                self.features_path
            )

        except Exception as exc:

            self.model = None
            self.scaler = None
            self.feature_columns = None

            raise InjuryModelUnavailable(
                f"Unable to load injury model: {exc}"
            )

    # ---------------------------------------------------------
    # LOAD REAL DATASET
    # ---------------------------------------------------------

    def _load_reference_data(self):

        if not self.dataset_path.exists():

            print(
                "Reference dataset not found:",
                self.dataset_path
            )

            return

        try:

            df = pd.read_csv(
                self.dataset_path
            )

            if "injury_risk" not in df.columns:

                print(
                    "Reference dataset does not contain injury_risk."
                )

                return

            # Same preprocessing used during training.
            X = df.drop(
                columns=[
                    "player_id",
                    "injury_risk",
                ],
                errors="ignore",
            )

            y = df["injury_risk"].astype(str)

            X = pd.get_dummies(
                X,
                columns=["player_type"],
                drop_first=False,
            )

            X = X.reindex(
                columns=self.feature_columns,
                fill_value=0,
            )

            X = X.apply(
                pd.to_numeric,
                errors="coerce",
            ).fillna(0)

            self.reference_data = df
            self.reference_labels = y.to_numpy()

            # Scale exactly like the MLP.
            self.reference_scaled = (
                self.scaler.transform(X)
            )

            print(
                f"Reference dataset loaded: {len(df)} records"
            )

        except Exception as exc:

            print(
                "Reference dataset loading failed:",
                exc
            )

            self.reference_data = None
            self.reference_scaled = None
            self.reference_labels = None

    # ---------------------------------------------------------
    # AVAILABILITY
    # ---------------------------------------------------------

    @property
    def available(self) -> bool:

        return (
            self.model is not None
            and self.scaler is not None
            and self.feature_columns is not None
        )

    # ---------------------------------------------------------
    # PARSE INPUT
    # ---------------------------------------------------------

    def parse_player_fields(
        self,
        raw: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not isinstance(raw, dict):

            raise InvalidPlayerFields(
                "Player fields must be an object."
            )

        result = {}

        for field in self.NUMERIC_FIELDS:

            value = raw.get(field)

            if value is None or value == "":

                raise InvalidPlayerFields(
                    f"Missing player field: {field}"
                )

            try:

                result[field] = float(value)

            except (TypeError, ValueError):

                raise InvalidPlayerFields(
                    f"Invalid value for {field}: {value}"
                )

        player_type = raw.get(
            "player_type"
        )

        if not player_type:

            raise InvalidPlayerFields(
                "Missing player field: player_type"
            )

        player_type = str(
            player_type
        ).strip()

        if player_type not in self.PLAYER_TYPE_MAP:

            raise InvalidPlayerFields(
                "Invalid player_type. "
                "Use Batsman, Bowler or All-Rounder."
            )

        result["player_type"] = (
            self.PLAYER_TYPE_MAP[
                player_type
            ]
        )

        return result

    # ---------------------------------------------------------
    # BUILD MODEL INPUT
    # ---------------------------------------------------------

    def _build_dataframe(
        self,
        player_fields: Dict[str, Any],
    ) -> pd.DataFrame:

        frame = pd.DataFrame(
            [dict(player_fields)]
        )

        frame = pd.get_dummies(
            frame,
            columns=["player_type"],
            drop_first=False,
        )

        frame = frame.reindex(
            columns=self.feature_columns,
            fill_value=0,
        )

        frame = frame.apply(
            pd.to_numeric,
            errors="coerce",
        ).fillna(0)

        return frame

    # ---------------------------------------------------------
    # SIMILARITY ANALYSIS
    # ---------------------------------------------------------

    def _similarity_prediction(
        self,
        scaled_input,
    ):

        if (
            self.reference_scaled is None
            or self.reference_labels is None
        ):

            return None

        # Calculate Euclidean distance
        # between new player and all real dataset records.
        distances = np.linalg.norm(
            self.reference_scaled
            - scaled_input[0],
            axis=1,
        )

        # Get 15 closest real records.
        nearest_indices = np.argsort(
            distances
        )[:15]

        nearest_labels = (
            self.reference_labels[
                nearest_indices
            ]
        )

        nearest_distances = (
            distances[
                nearest_indices
            ]
        )

        # Inverse-distance weighting.
        weights = 1.0 / (
            nearest_distances + 1e-6
        )

        class_scores = {}

        for label, weight in zip(
            nearest_labels,
            weights,
        ):

            class_scores[label] = (
                class_scores.get(
                    label,
                    0.0,
                )
                + float(weight)
            )

        total = sum(
            class_scores.values()
        )

        if total > 0:

            class_probabilities = {
                label: score / total
                for label, score
                in class_scores.items()
            }

        else:

            class_probabilities = {}

        if not class_probabilities:

            return None

        similarity_prediction = max(
            class_probabilities,
            key=class_probabilities.get,
        )

        return {
            "prediction": similarity_prediction,
            "probabilities": class_probabilities,
            "nearest_count": len(
                nearest_indices
            ),
            "nearest_distances": [
                float(x)
                for x in nearest_distances[:5]
            ],
        }

    # ---------------------------------------------------------
    # FINAL PREDICTION
    # ---------------------------------------------------------

    def predict(
        self,
        player_fields: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not self.available:

            raise InjuryModelUnavailable(
                "Injury-risk model artifacts are not available."
            )

        try:

            frame = self._build_dataframe(
                player_fields
            )

            scaled = self.scaler.transform(
                frame
            )

            # -------------------------------------------------
            # MLP
            # -------------------------------------------------

            mlp_prediction = self.model.predict(
                scaled
            )[0]

            if hasattr(
                self.model,
                "predict_proba",
            ):

                mlp_probabilities = (
                    self.model.predict_proba(
                        scaled
                    )[0]
                )

                classes = list(
                    self.model.classes_
                )

            else:

                mlp_probabilities = None
                classes = []

            mlp_prediction = str(
                mlp_prediction
            )

            mlp_probability_dict = {}

            if mlp_probabilities is not None:

                for cls, probability in zip(
                    classes,
                    mlp_probabilities,
                ):

                    mlp_probability_dict[
                        str(cls)
                    ] = float(
                        probability
                    )

            # -------------------------------------------------
            # REAL-DATA SIMILARITY
            # -------------------------------------------------

            similarity = (
                self._similarity_prediction(
                    scaled
                )
            )

            # -------------------------------------------------
            # COMBINE MLP + REAL-DATA SIMILARITY
            # -------------------------------------------------

            final_probabilities = {}

            all_classes = [
                "High",
                "Low",
                "Medium",
            ]

            for cls in all_classes:

                mlp_score = (
                    mlp_probability_dict.get(
                        cls,
                        0.0,
                    )
                )

                similarity_score = 0.0

                if similarity:

                    similarity_score = (
                        similarity[
                            "probabilities"
                        ].get(
                            cls,
                            0.0,
                        )
                    )

                # 60% MLP
                # 40% similarity to actual records.
                final_score = (
                    0.60 * mlp_score
                    + 0.40
                    * similarity_score
                )

                final_probabilities[
                    cls
                ] = final_score

            final_prediction = max(
                final_probabilities,
                key=final_probabilities.get,
            )

            confidence = float(
                final_probabilities[
                    final_prediction
                ]
            )

            return {

                "risk": final_prediction,

                "confidence": confidence,

                "class_probabilities":
                    final_probabilities,

                "mlp_prediction":
                    mlp_prediction,

                "mlp_probabilities":
                    mlp_probability_dict,

                "similarity_prediction":
                    (
                        similarity[
                            "prediction"
                        ]
                        if similarity
                        else None
                    ),

                "similarity_probabilities":
                    (
                        similarity[
                            "probabilities"
                        ]
                        if similarity
                        else {}
                    ),

                "similar_records_used":
                    (
                        similarity[
                            "nearest_count"
                        ]
                        if similarity
                        else 0
                    ),

                "pipeline":
                    "mlp_plus_dataset_similarity",

                "feature_count":
                    len(
                        self.feature_columns
                    ),
            }

        except Exception as exc:

            raise InjuryModelUnavailable(
                f"Injury model prediction failed: {exc}"
            )