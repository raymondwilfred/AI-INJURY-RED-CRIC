"""2D biomechanical features from COCO-17 keypoints.

Geometry matches the notebook's production extraction (cell 54 / cell 56):
knee joint angles, trunk lean vs vertical, shoulder/hip line angles,
and circular-normalized shoulder-hip difference.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

# COCO-17 indices used by YOLO-Pose
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_HIP = 11
RIGHT_HIP = 12
LEFT_KNEE = 13
RIGHT_KNEE = 14
LEFT_ANKLE = 15
RIGHT_ANKLE = 16

REQUIRED_KEYPOINTS = [
    LEFT_SHOULDER,
    RIGHT_SHOULDER,
    LEFT_HIP,
    RIGHT_HIP,
    LEFT_KNEE,
    RIGHT_KNEE,
    LEFT_ANKLE,
    RIGHT_ANKLE,
]

BIOMECH_FEATURE_NAMES = [
    "left_knee_angle",
    "right_knee_angle",
    "trunk_angle",
    "shoulder_line_angle",
    "hip_line_angle",
    "shoulder_hip_angle_difference",
]


def calculate_angle(a, b, c) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)

    ba = a - b
    bc = c - b

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denominator == 0:
        return float("nan")

    cosine = np.dot(ba, bc) / denominator
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def circular_angle_difference(angle_a: float, angle_b: float) -> float:
    """Normalize (a - b) into (-180, 180], as in the notebook."""
    return (angle_a - angle_b + 180.0) % 360.0 - 180.0


def empty_features() -> dict[str, float]:
    return {name: float("nan") for name in BIOMECH_FEATURE_NAMES}


def extract_features(
    person: np.ndarray,
    confidence: np.ndarray,
    threshold: float = 0.25,
) -> dict[str, float]:
    if any(confidence[i] < threshold for i in REQUIRED_KEYPOINTS):
        return empty_features()

    left_shoulder = person[LEFT_SHOULDER]
    right_shoulder = person[RIGHT_SHOULDER]
    left_hip = person[LEFT_HIP]
    right_hip = person[RIGHT_HIP]
    left_knee = person[LEFT_KNEE]
    right_knee = person[RIGHT_KNEE]
    left_ankle = person[LEFT_ANKLE]
    right_ankle = person[RIGHT_ANKLE]

    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

    shoulder_center = (left_shoulder + right_shoulder) / 2
    hip_center = (left_hip + right_hip) / 2
    trunk_vector = shoulder_center - hip_center
    vertical_vector = np.array([0.0, -1.0])
    trunk_norm = np.linalg.norm(trunk_vector)

    if trunk_norm > 0:
        trunk_angle = float(
            np.degrees(
                np.arccos(
                    np.clip(
                        np.dot(trunk_vector, vertical_vector) / trunk_norm,
                        -1.0,
                        1.0,
                    )
                )
            )
        )
    else:
        trunk_angle = float("nan")

    shoulder_vector = right_shoulder - left_shoulder
    hip_vector = right_hip - left_hip

    shoulder_line_angle = float(
        np.degrees(np.arctan2(shoulder_vector[1], shoulder_vector[0]))
    )
    hip_line_angle = float(np.degrees(np.arctan2(hip_vector[1], hip_vector[0])))
    angle_difference = circular_angle_difference(
        shoulder_line_angle, hip_line_angle
    )

    return {
        "left_knee_angle": left_knee_angle,
        "right_knee_angle": right_knee_angle,
        "trunk_angle": trunk_angle,
        "shoulder_line_angle": shoulder_line_angle,
        "hip_line_angle": hip_line_angle,
        "shoulder_hip_angle_difference": angle_difference,
    }


def features_are_valid(features: dict[str, Any]) -> bool:
    return all(
        value is not None and not (isinstance(value, float) and math.isnan(value))
        for value in features.values()
    )


def sanitize_features(features: dict[str, Any]) -> dict[str, float | None]:
    cleaned: dict[str, float | None] = {}
    for name in BIOMECH_FEATURE_NAMES:
        value = features.get(name)
        if value is None or (isinstance(value, float) and math.isnan(value)):
            cleaned[name] = None
        else:
            cleaned[name] = float(value)
    return cleaned
