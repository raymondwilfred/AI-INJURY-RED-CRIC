# 🏏 AI-INJURY-RED-CRIC

## AI-Based Injury Prediction and Prevention for Cricket Players

An AI-powered cricket injury-risk analysis system that combines **computer vision, human pose estimation, biomechanical feature extraction, and machine learning** to identify movement patterns and estimate injury risk.

The system is designed as an **AI assistant for coaches and physiotherapists**, helping them analyze player movement and structured workload/injury-related information.

---

## 🎯 Project Objective

The main objective is to develop an AI system that can analyze cricket players':

* Batting movements
* Bowling movements
* Fielding movements
* Running and sprinting
* Jumping and landing
* Throwing and catching
* General body movement
* Workload and fitness-related information
* Previous injury information

The system aims to identify potentially risky movement patterns and provide an injury-risk classification that can support preventive decision-making.

> **Important:** The system is a research/prototype project and is not intended to provide medical diagnosis.

---

# 🏗️ System Architecture

```text
                Cricket Player
                      │
                      ▼
             Images / Video Data
                      │
                      ▼
             YOLOv8 Object Detection
                      │
                      ▼
             YOLOv8 Pose Estimation
                      │
                      ▼
              17 Body Keypoints
                      │
                      ▼
        Biomechanical Feature Extraction
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     Knee Angles   Trunk Angle   Shoulder-Hip
                                  Rotation
                      │
                      ▼
              Injury-Risk ML Models
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
 Random Forest     XGBoost          SVM
       │              │              │
       └──────────────┼──────────────┘
                      ▼
             Risk Classification
                      │
                      ▼
          Coach / Physiotherapist
```

---

# 🤖 Models Used

## Computer Vision Models

### 1. YOLOv8n Object Detection

A cricket object-detection model was trained to identify:

* Ball
* Batsmen
* Bowler
* Fielder
* Umpire
* Wicket
* Wicket-Keeper

Test performance:

| Metric    | Result |
| --------- | -----: |
| Precision |  0.885 |
| Recall    |  0.822 |
| mAP50     |  0.845 |
| mAP50-95  |  0.695 |

---

### 2. YOLOv8n-Pose

YOLOv8n-Pose was used to extract human body keypoints.

The model provides **17 COCO body keypoints**, which are used to calculate geometric biomechanical features.

Extracted features include:

* Left knee angle
* Right knee angle
* Trunk angle
* Shoulder angle
* Hip angle
* Shoulder-hip rotation

The extracted pose data is stored in:

```text
pose_keypoints.csv
```

---

### 3. BGT Cricket Object Detection — YOLOv8n

A second cricket dataset was used to train and evaluate another YOLOv8n object-detection model.

Test performance:

| Metric    |  Result |
| --------- | ------: |
| Precision |  0.9085 |
| Recall    |  0.9474 |
| mAP50     | 0.91935 |
| mAP50-95  | 0.53147 |

---

# 🧬 Biomechanical Analysis

Pose keypoints are converted into geometric features that can be used for movement analysis.

Current features include:

```text
Left Knee Angle
Right Knee Angle
Trunk Angle
Shoulder Angle
Hip Angle
Shoulder-Hip Rotation
```

These measurements represent **geometric movement features extracted from pose estimation**. They should not be interpreted as medical diagnoses.

---

# 🩺 Injury-Risk Classification

A structured sports injury dataset was used to experiment with machine-learning injury-risk classification.

The current modeling dataset contains:

```text
21,900 records
```

Features:

```text
game_workload
groin_squeeze
hip_mobility
```

Target:

```text
injury
```

The dataset contains a highly imbalanced injury class, so accuracy alone is not used to evaluate the models.

---

# 🧠 Injury-Risk Models

Three injury-risk classification models have currently been trained and evaluated.

### Random Forest

| Metric    | Result |
| --------- | -----: |
| Accuracy  |   0.98 |
| Precision |   0.09 |
| Recall    |   0.19 |
| F1-score  |   0.12 |

### XGBoost

| Metric    | Result |
| --------- | -----: |
| Accuracy  |   0.99 |
| Precision |   0.11 |
| Recall    |   0.04 |
| F1-score  |   0.06 |

### SVM

| Metric    | Result |
| --------- | -----: |
| Accuracy  |   0.91 |
| Precision |   0.06 |
| Recall    |   0.96 |
| F1-score  |   0.11 |

### Current Comparison

| Model         | Accuracy | Precision |   Recall |       F1 |
| ------------- | -------: | --------: | -------: | -------: |
| Random Forest |     0.98 |      0.09 |     0.19 | **0.12** |
| XGBoost       |     0.99 |  **0.11** |     0.04 |     0.06 |
| SVM           |     0.91 |      0.06 | **0.96** |     0.11 |

The remaining planned models are:

* LightGBM
* MLP Neural Network

The final model will be selected only after completing the five-model comparison.

---

# 📊 Evaluation Strategy

Because the injury dataset is highly imbalanced, the project evaluates:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion Matrix

Validation data is used to select the classification threshold, while the chronological test set is kept separate for final evaluation.

---

# 📁 Project Structure

```text
AI-INJURY-RED-CRIC/
│
├── README.md
│
├── notebooks/
│   └── injury_risk_models_kaggle.ipynb
│
├── datasets/
│   └── README.md
│
├── models/
│   └── README.md
│
├── src/
│   ├── detection/
│   ├── pose/
│   ├── biomechanics/
│   └── prediction/
│
├── results/
│   ├── detection/
│   ├── pose/
│   └── injury_risk/
│
├── app/
│   ├── frontend/
│   └── backend/
│
├── requirements.txt
│
└── .gitignore
```

---

# 📓 Kaggle Training

The machine-learning experiments are currently being developed and trained in Kaggle using GPU acceleration.

The Kaggle notebook contains the preprocessing, training, validation, threshold selection and evaluation workflow.

**Kaggle Notebook:**

https://www.kaggle.com/code/raymondwilfred13/notebook95d361c69f

---

# 📂 Google Drive — Videos & Project Data

The project videos and additional project data are available here:

**Google Drive:**

https://drive.google.com/drive/folders/1ln8j0wzjQV_AYVv7H7KuQi89lACQFBIaU?usp=drive_link

> The repository does not include large video datasets directly. The Google Drive folder is provided as the external project-data location.

---

# 🗃️ Dataset Sources

The project uses multiple datasets for different stages of the pipeline, including cricket object-detection, pose/keypoint and structured injury-risk data.

The datasets are used for different purposes and should not be interpreted as one unified medically validated cricket injury dataset.

---

# ⚙️ Technologies

### Programming

* Python
* JavaScript

### Machine Learning

* Scikit-learn
* Random Forest
* XGBoost
* SVM

### Computer Vision

* YOLOv8
* YOLOv8-Pose
* OpenCV

### Data Processing

* Pandas
* NumPy

### Development

* Kaggle
* Jupyter Notebook
* Git
* GitHub

### Planned

* LightGBM
* MLP Neural Network
* FastAPI
* React

---

# 🔬 Research Limitations

The current project is a research/prototype implementation.

Important limitations include:

1. The structured injury dataset is general sports data rather than a cricket-specific clinical injury dataset.
2. The injury class is highly imbalanced.
3. The current test set contains only a small number of injury cases.
4. Pose-derived biomechanical features are geometric measurements and are not medical diagnoses.
5. Public cricket datasets provide stronger coverage for batting and bowling than for every cricket activity.
6. A movement pattern alone does not establish that an injury will occur.
7. Further validation with larger, player-specific and clinically validated cricket injury datasets is required.

---

# 🚀 Future Work

Planned improvements include:

* Complete five-model injury-risk comparison
* LightGBM
* MLP Neural Network
* More cricket-specific injury data
* Player-specific/video-session validation
* Additional biomechanical features
* More batting, bowling and fielding actions
* Real-time video processing
* React dashboard
* FastAPI backend
* Explainable AI using SHAP/LIME
* Risk trend visualization
* Physiotherapist/coach dashboard
* Validation on unseen players and independent video data

---



## ⚠️ Disclaimer

This project is an academic/research prototype for exploring AI-based cricket movement and injury-risk analysis. It does not replace professional medical assessment, diagnosis or treatment.
