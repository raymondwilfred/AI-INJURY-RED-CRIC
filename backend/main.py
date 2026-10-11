from pathlib import Path
from typing import Dict, Any
import base64
import tempfile

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from services.pose_service import (
    PoseService,
    decode_image_bytes,
)
from services.injury_model import (
    InjuryModelService,
    InjuryModelUnavailable,
    InvalidPlayerFields,
)


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
MODELS_DIR = PROJECT_DIR / "models"


app = FastAPI(
    title="AI Injury Red Cric API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pose_service = None
injury_service = None


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


@app.on_event("startup")
def startup_event():

    global pose_service
    global injury_service

    try:
        injury_service = InjuryModelService(
            MODELS_DIR
        )

        print(
            "Injury model available:",
            injury_service.available,
        )

    except Exception as exc:

        injury_service = None

        print(
            "Injury model unavailable:",
            exc,
        )

    try:

        pose_model_path = (
            MODELS_DIR /
            "yolo26n-pose.pt"
        )

        pose_service = PoseService(
            pose_model_path
        )

        print(
            "Pose service loaded."
        )

    except Exception as exc:

        pose_service = None

        print(
            "Pose service unavailable:",
            exc,
        )


@app.get("/")
def root():

    return {
        "message": "AI Injury Red Cric API",
        "status": "running",
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "injury_model_available": (
            injury_service is not None
            and injury_service.available
        ),
        "pose_service_available": (
            pose_service is not None
        ),
    }


def build_player_fields(
    age: str,
    player_type: str,
    experience_years: str,
    height_cm: str,
    weight_kg: str,
    bmi: str,
    body_fat_percent: str,
    training_hours_week: str,
    bowling_overs_week: str,
    batting_hours_week: str,
    strength_training_hours: str,
    matches_last_month: str,
    days_since_last_match: str,
    previous_injuries_count: str,
    last_injury_days_ago: str,
    recovery_days_last_injury: str,
    fatigue_level: str,
    sleep_hours_day: str,
    stress_level: str,
    fitness_score: str,
) -> Dict[str, Any]:

    return {
        "age": age,
        "player_type": player_type,
        "experience_years": experience_years,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "bmi": bmi,
        "body_fat_percent": body_fat_percent,
        "training_hours_week": training_hours_week,
        "bowling_overs_week": bowling_overs_week,
        "batting_hours_week": batting_hours_week,
        "strength_training_hours": strength_training_hours,
        "matches_last_month": matches_last_month,
        "days_since_last_match": days_since_last_match,
        "previous_injuries_count": previous_injuries_count,
        "last_injury_days_ago": last_injury_days_ago,
        "recovery_days_last_injury": recovery_days_last_injury,
        "fatigue_level": fatigue_level,
        "sleep_hours_day": sleep_hours_day,
        "stress_level": stress_level,
        "fitness_score": fitness_score,
    }


def image_to_data_url(
    image_bytes: bytes,
) -> str:

    encoded = base64.b64encode(
        image_bytes
    ).decode("ascii")

    return (
        "data:image/jpeg;base64,"
        + encoded
    )


@app.post("/api/analyze")
async def analyze(

    image: UploadFile = File(...),

    age: str = Form(...),
    player_type: str = Form(...),
    experience_years: str = Form(...),
    height_cm: str = Form(...),
    weight_kg: str = Form(...),
    bmi: str = Form(...),
    body_fat_percent: str = Form(...),
    training_hours_week: str = Form(...),
    bowling_overs_week: str = Form(...),
    batting_hours_week: str = Form(...),
    strength_training_hours: str = Form(...),
    matches_last_month: str = Form(...),
    days_since_last_match: str = Form(...),
    previous_injuries_count: str = Form(...),
    last_injury_days_ago: str = Form(...),
    recovery_days_last_injury: str = Form(...),
    fatigue_level: str = Form(...),
    sleep_hours_day: str = Form(...),
    stress_level: str = Form(...),
    fitness_score: str = Form(...),

):

    if pose_service is None:

        raise HTTPException(
            status_code=503,
            detail="Pose service is not available.",
        )

    if injury_service is None:

        raise HTTPException(
            status_code=503,
            detail="Injury model service is not available.",
        )

    image_bytes = await image.read()

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    temporary_path = None

    try:

        player_fields = build_player_fields(

            age=age,
            player_type=player_type,
            experience_years=experience_years,
            height_cm=height_cm,
            weight_kg=weight_kg,
            bmi=bmi,
            body_fat_percent=body_fat_percent,
            training_hours_week=training_hours_week,
            bowling_overs_week=bowling_overs_week,
            batting_hours_week=batting_hours_week,
            strength_training_hours=strength_training_hours,
            matches_last_month=matches_last_month,
            days_since_last_match=days_since_last_match,
            previous_injuries_count=previous_injuries_count,
            last_injury_days_ago=last_injury_days_ago,
            recovery_days_last_injury=recovery_days_last_injury,
            fatigue_level=fatigue_level,
            sleep_hours_day=sleep_hours_day,
            stress_level=stress_level,
            fitness_score=fitness_score,
        )

        parsed_player_fields = (
            injury_service.parse_player_fields(
                player_fields
            )
        )

        original_image = image_to_data_url(
            image_bytes
        )

        # -------------------------------------------------
        # IMPORTANT:
        # Convert uploaded bytes into an OpenCV NumPy image
        # BEFORE sending it to PoseService.analyze().
        # -------------------------------------------------

        image_bgr = decode_image_bytes(
            image_bytes
        )

        pose_result = None
        pose_error = None

        try:

            pose_result = (
                pose_service.analyze(
                    image_bgr
                )
            )

        except Exception as exc:

            pose_error = str(exc)

            print(
                "Pose analysis warning:",
                pose_error,
            )

        # -------------------------------------------------
        # Injury-risk prediction
        # Current local MLP uses structured player data.
        # -------------------------------------------------

        prediction = None
        prediction_error = None

        try:

            prediction = (
                injury_service.predict(
                    parsed_player_fields
                )
            )

        except (
            InjuryModelUnavailable,
            InvalidPlayerFields,
            Exception,
        ) as exc:

            prediction_error = str(exc)

            print(
                "Prediction warning:",
                prediction_error,
            )

        # -------------------------------------------------
        # Default pose response
        # -------------------------------------------------

        if pose_result is not None:

            biomechanics = (
                pose_result.get(
                    "biomechanics",
                    {},
                )
            )

            biomechanics_valid = (
                pose_result.get(
                    "biomechanics_valid",
                    False,
                )
            )

            persons_detected = (
                pose_result.get(
                    "persons_detected",
                    0,
                )
            )

            person_used = (
                pose_result.get(
                    "person_used",
                    None,
                )
            )

            annotated_image = (
                pose_result.get(
                    "annotated_image",
                    None,
                )
            )

            keypoints = (
                pose_result.get(
                    "keypoints",
                    {},
                )
            )

        else:

            biomechanics = {
                "left_knee_angle": None,
                "right_knee_angle": None,
                "trunk_angle": None,
                "shoulder_line_angle": None,
                "hip_line_angle": None,
                "shoulder_hip_angle_difference": None,
            }

            biomechanics_valid = False
            persons_detected = 0
            person_used = None
            annotated_image = None
            keypoints = {}

        # -------------------------------------------------
        # Default prediction response
        # -------------------------------------------------

        if prediction is not None:

            risk = prediction.get(
                "risk",
                "Unknown",
            )

            confidence = prediction.get(
                "confidence",
                None,
            )

            class_probabilities = (
                prediction.get(
                    "class_probabilities",
                    {},
                )
            )

            ml_available = True

            ml_pipeline = prediction.get(
                "pipeline",
                "tabular_mlp",
            )

            ml_message = None

        else:

            risk = "Unknown"
            confidence = None
            class_probabilities = {}

            ml_available = False

            ml_pipeline = "unavailable"

            ml_message = (
                prediction_error
                or "Injury model prediction unavailable."
            )

        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        return {

            "risk": risk,

            "confidence": confidence,

            "class_probabilities": (
                class_probabilities
            ),

            "ml_available": ml_available,

            "ml_pipeline": ml_pipeline,

            "ml_message": ml_message,

            "biomechanics": biomechanics,

            "biomechanics_valid": (
                biomechanics_valid
            ),

            "persons_detected": (
                persons_detected
            ),

            "person_used": person_used,

            "keypoints": keypoints,

            "original_image": (
                original_image
            ),

            "annotated_image": (
                annotated_image
            ),

            "pose_error": pose_error,

        }

    except InvalidPlayerFields as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            "API analysis error:",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:

        if temporary_path is not None:

            try:

                Path(
                    temporary_path
                ).unlink(
                    missing_ok=True
                )

            except Exception:
                pass