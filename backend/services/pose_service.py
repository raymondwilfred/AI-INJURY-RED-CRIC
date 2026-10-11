"""
YOLO26n-Pose inference and biomechanical feature extraction.
"""

from __future__ import annotations

from pathlib import Path
import base64

import cv2
import numpy as np
from ultralytics import YOLO

from .biomechanics import (
    extract_features,
    features_are_valid,
    sanitize_features,
)


COCO_KEYPOINT_NAMES = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]


class PoseService:

    def __init__(self, model_path: Path):

        model_path = Path(model_path)

        # -------------------------------------------------
        # Allow either:
        #
        # models/yolo26n-pose.pt
        #
        # OR directly:
        #
        # models/
        # -------------------------------------------------

        if model_path.is_dir():

            model_path = (
                model_path /
                "yolo26n-pose.pt"
            )

        if not model_path.exists():

            raise FileNotFoundError(
                f"Pose model not found at {model_path}. "
                "Place yolo26n-pose.pt in the models folder."
            )

        self.model_path = model_path

        print(
            "Loading pose model:",
            self.model_path,
        )

        self.model = YOLO(
            str(self.model_path),
            task="pose",
        )

        print(
            "Pose model loaded successfully."
        )


    def analyze(
        self,
        image_bgr: np.ndarray,
    ) -> dict:

        if image_bgr is None:

            raise ValueError(
                "INVALID_IMAGE"
            )

        if not isinstance(
            image_bgr,
            np.ndarray,
        ):

            raise TypeError(
                "PoseService.analyze expects "
                "an OpenCV numpy image."
            )


        # -------------------------------------------------
        # YOLO pose prediction
        # -------------------------------------------------

        results = self.model.predict(

            source=image_bgr,

            conf=0.05,

            imgsz=640,

            verbose=False,
        )


        if not results:

            raise ValueError(
                "NO_PERSON"
            )


        result = results[0]


        # -------------------------------------------------
        # Check keypoints
        # -------------------------------------------------

        if (
            result.keypoints is None
            or result.keypoints.xy is None
        ):

            raise ValueError(
                "NO_PERSON"
            )


        keypoints_xy = (
            result.keypoints.xy
            .cpu()
            .numpy()
        )


        if (
            keypoints_xy.size == 0
            or len(keypoints_xy) == 0
        ):

            raise ValueError(
                "NO_PERSON"
            )


        # -------------------------------------------------
        # Keypoint confidence
        # -------------------------------------------------

        if result.keypoints.conf is not None:

            keypoints_conf = (
                result.keypoints.conf
                .cpu()
                .numpy()
            )

        else:

            keypoints_conf = np.ones(
                (
                    keypoints_xy.shape[0],
                    keypoints_xy.shape[1],
                ),
                dtype=float,
            )


        # -------------------------------------------------
        # Process every detected person
        # -------------------------------------------------

        persons = []


        for person_id, (
            person,
            confidence,
        ) in enumerate(
            zip(
                keypoints_xy,
                keypoints_conf,
            )
        ):

            features = extract_features(
                person,
                confidence,
            )


            mean_confidence = (
                float(
                    np.mean(
                        confidence
                    )
                )
                if len(confidence)
                else 0.0
            )


            persons.append(

                {
                    "person_id":
                        person_id,

                    "mean_confidence":
                        mean_confidence,

                    "features":
                        features,

                    "valid":
                        features_are_valid(
                            features
                        ),

                    "keypoints": {

                        name: {

                            "x":
                                float(
                                    person[i][0]
                                ),

                            "y":
                                float(
                                    person[i][1]
                                ),

                            "confidence":
                                float(
                                    confidence[i]
                                ),
                        }

                        for i, name in enumerate(
                            COCO_KEYPOINT_NAMES
                        )

                        if i < len(person)
                    },
                }
            )


        # -------------------------------------------------
        # Select best person
        # -------------------------------------------------

        selected = _select_person(
            persons
        )


        if selected is None:

            raise ValueError(
                "NO_PERSON"
            )


        # -------------------------------------------------
        # Annotated image
        # -------------------------------------------------

        annotated = result.plot()


        # -------------------------------------------------
        # Encode annotated image
        # -------------------------------------------------

        annotated_image = (
            encode_jpeg_base64(
                annotated
            )
        )


        annotated_image = (
            "data:image/jpeg;base64,"
            + annotated_image
        )


        # -------------------------------------------------
        # Return pose result
        # -------------------------------------------------

        return {

            "persons_detected":
                len(persons),

            "person_used":
                selected["person_id"],

            "biomechanics":
                sanitize_features(
                    selected["features"]
                ),

            "biomechanics_valid":
                selected["valid"],

            "keypoints":
                selected["keypoints"],

            "annotated_image":
                annotated_image,
        }


# =========================================================
# PERSON SELECTION
# =========================================================

def _select_person(
    persons: list[dict],
) -> dict | None:

    valid = [
        person
        for person in persons
        if person["valid"]
    ]


    pool = (
        valid
        if valid
        else persons
    )


    if not pool:

        return None


    return max(
        pool,
        key=lambda person:
            person["mean_confidence"],
    )


# =========================================================
# IMAGE DECODER
# =========================================================

def decode_image_bytes(
    data: bytes,
) -> np.ndarray:

    array = np.frombuffer(
        data,
        dtype=np.uint8,
    )


    image = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR,
    )


    if image is None:

        raise ValueError(
            "INVALID_IMAGE"
        )


    return image


# =========================================================
# JPEG BASE64 ENCODER
# =========================================================

def encode_jpeg_base64(
    image_bgr: np.ndarray,
) -> str:

    ok, buffer = cv2.imencode(
        ".jpg",
        image_bgr,
        [
            int(
                cv2.IMWRITE_JPEG_QUALITY
            ),
            90,
        ],
    )


    if not ok:

        raise ValueError(
            "IMAGE_ENCODE_FAILED"
        )


    return base64.b64encode(
        buffer.tobytes()
    ).decode(
        "ascii"
    )