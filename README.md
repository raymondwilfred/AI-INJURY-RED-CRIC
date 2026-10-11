# AI-INJURY-RED-CRIC

AI-Based Injury Risk Analysis for Cricket Players.

This academic prototype combines YOLO26n-Pose biomechanical measurements with a structured cricket player record and an MLP injury-risk classifier from the project notebook.

**This is not a medical diagnosis, clinical assessment, or a probability of future injury.**

## Objective

Estimate a **Low / Medium / High** injury-risk class for a cricket player from:

1. A cricket image (17 COCO keypoints via YOLO26n-Pose)
2. Player information matching the notebook feature columns

## Architecture

```
React (Vite)  -->  POST /api/analyze  -->  FastAPI
                                              |
                                              +-- YOLO26n-Pose (Ultralytics)
                                              +-- 2D biomechanics (NumPy)
                                              +-- StandardScaler + MLPClassifier
```

The notebook is the source of truth (`notebooks/notebookb6997a44db (1).ipynb`).

## Technologies

- Frontend: React, Vite, Axios
- Backend: FastAPI, Uvicorn, Ultralytics, OpenCV, NumPy, Pandas, scikit-learn, Joblib
- Pose: pretrained **YOLO26n-Pose** (`yolo26n-pose.pt`)
- Injury classifier: **MLPClassifier** (`hidden_layer_sizes=(64, 32)`, ReLU, Adam)

## Datasets (from the notebook)

- Structured injury-risk CSV: `cricket_player_data_fixed.csv` (500 records, 22 columns, target `injury_risk` with classes Low / Medium / High)
- Cricket images: Roboflow `cricket-r97s2` (297 images; 7 classes: Ball, Batsmen, Bowler, Fielder, Umpire, Wicket, Wicket-Keeper)

## Model pipeline

1. **YOLO26n** was trained in the notebook for cricket object detection (50 epochs). That detector is **not** required by `/api/analyze`.
2. **YOLO26n-Pose** estimates 17 COCO keypoints.
3. Geometry features extracted:
   - `left_knee_angle`
   - `right_knee_angle`
   - `trunk_angle`
   - `shoulder_line_angle`
   - `hip_line_angle`
   - `shoulder_hip_angle_difference` (circular-normalized to (-180, 180])
4. Player fields (LabelEncoder / map: All-Rounder=0, Batsman=1, Bowler=2), `player_id` dropped, `injury_risk` as target.
5. `StandardScaler` on training features.
6. Compared classifiers: RandomForest, XGBoost, SVM, LightGBM, MLP.
7. Two saved MLPs in the notebook:
   - Tabular MLP: 20 player features → `mlp_injury_risk_model.pkl`, `feature_scaler.pkl`, `feature_columns.pkl`
   - Fusion MLP: 20 player + 6 pose features → `fusion_mlp_model.pkl`, `fusion_scaler.pkl`, `fusion_feature_columns.pkl`

The application prefers the **fusion** files because `/api/analyze` accepts an image and player information. If only the tabular files are present, it uses those and still returns pose measurements.

The fusion training set in the notebook added **synthetic** pose columns with `np.random.seed(42)` (`np.random.uniform(...)`). Real pose angles from YOLO were not the fusion training features.

## Verified notebook metrics

Do not treat these as real-world injury probabilities.

### Tabular models — validation (80 records)

| Model | Accuracy | Macro precision | Macro recall | Macro F1 |
| --- | --- | --- | --- | --- |
| Random Forest | 0.8375 | 0.8569 | 0.8275 | 0.8326 |
| XGBoost | 0.8500 | 0.8665 | 0.8368 | 0.8405 |
| SVM | 0.9125 | 0.9205 | 0.9067 | 0.9108 |
| LightGBM | 0.8750 | 0.8787 | 0.8658 | 0.8685 |
| MLP | 0.9375 | 0.9364 | 0.9357 | 0.9359 |

### Tabular MLP — final test (100 records)

- Accuracy: 0.9800 (98.00%)
- Macro precision: 0.9812 (98.12%)
- Macro recall: 0.9794 (97.94%)
- Macro F1: 0.9801 (98.01%)

Confusion matrix on that test set: `[[34, 1, 0], [0, 35, 0], [1, 0, 29]]` with display labels from `mlp_model.classes_`.

### Fusion MLP (26 features)

- Validation (80 records): accuracy 0.925, macro precision 0.9344, macro recall 0.9190, macro F1 0.9231
- Test (100 records): accuracy 0.9400, macro precision 0.9449, macro recall 0.9397, macro F1 0.9417

### YOLO26n cricket detector — notebook test split

31 images, 158 instances:

- all: Box P 0.853, R 0.733, mAP50 0.797, mAP50-95 0.642

## Installation

Use Python 3.11 or 3.12 (PyTorch / Ultralytics are not reliable on newer feature releases).

```powershell
cd D:\pep\AI-INJURY-RED-CRIC
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

Place notebook artifacts in `models/`:

- Required for pose: `yolo26n-pose.pt`
- Required for ML risk: either the fusion trio or the tabular trio listed above

If the Kaggle-exported `.pkl` files are missing and `cricket_player_data_fixed.csv` is available locally, run:

```powershell
python backend\export_injury_models.py --csv PATH\cricket_player_data_fixed.csv
```

Do **not** retrain YOLO for this application.

Frontend:

```powershell
cd frontend
npm install
```

## Backend command

```powershell
cd D:\pep\AI-INJURY-RED-CRIC\backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Backend URL: `http://localhost:8000`  
Health: `GET http://localhost:8000/health`

## Frontend command

```powershell
cd D:\pep\AI-INJURY-RED-CRIC\frontend
npm run dev
```

Frontend URL: `http://localhost:5173`

## API

`POST http://localhost:8000/api/analyze`

- Multipart form
- File field: `image`
- Player fields: the 20 notebook columns (`age`, `player_type`, `experience_years`, `height_cm`, `weight_kg`, `bmi`, `body_fat_percent`, `training_hours_week`, `bowling_overs_week`, `batting_hours_week`, `strength_training_hours`, `matches_last_month`, `days_since_last_match`, `previous_injuries_count`, `last_injury_days_ago`, `recovery_days_last_injury`, `fatigue_level`, `sleep_hours_day`, `stress_level`, `fitness_score`)

CORS is enabled for `http://localhost:5173`.

Error cases:

- missing / invalid image
- invalid player fields
- no person detected
- missing pose model
- prediction errors

If the injury MLP files are missing, pose analysis still runs and the API reports that the ML risk model is unavailable. Predictions are never invented.

Displayed **model confidence** is the MLP class probability for the predicted label. It is **not** an actual probability of injury.

## Limitations

- Academic prototype on a 500-row structured table plus 2D pose from a single image
- Fusion MLP was trained with randomly generated pose features, not the extracted YOLO angles
- 2D keypoints cannot recover true 3D joint moments or tissue load
- Keypoints can fail on occluded, cropped, or multi-player frames
- YOLO cricket-detection weights from the 50-epoch run were not copied into this repo and are unused by the dashboard
- Trained `.pkl` exports lived under `/kaggle/working/` and must be copied into `models/` for live classification

## Disclaimer

AI-INJURY-RED-CRIC is an academic software prototype for coursework demonstration. It must not be used to diagnose, treat, prevent, or predict clinical injury. Always consult qualified medical and coaching professionals.
