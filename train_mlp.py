import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

# Paths
CSV_PATH = r"D:\pep\AI-INJURY-RED-CRIC\data\cricket_player_data_fixed.csv"
MODEL_DIR = r"D:\pep\AI-INJURY-RED-CRIC\models"

os.makedirs(MODEL_DIR, exist_ok=True)

# Load dataset
df = pd.read_csv(CSV_PATH)

print("Dataset shape:", df.shape)
print("Columns:", list(df.columns))

# Target
TARGET = "injury_risk"

# Remove ID because it is not a useful prediction feature
drop_columns = ["player_id", TARGET]

X = df.drop(columns=drop_columns)
y = df[TARGET]

# Convert categorical columns to numbers
X = pd.get_dummies(X, drop_first=False)

# Make sure everything is numeric
X = X.apply(pd.to_numeric, errors="coerce")
X = X.fillna(0)

# Save exact feature columns
feature_columns = list(X.columns)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Scale features
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# MLP model
model = MLPClassifier(
    hidden_layer_sizes=(64, 32),
    activation="relu",
    solver="adam",
    max_iter=1000,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.15,
    n_iter_no_change=30
)

print("\nTraining MLP...")
model.fit(X_train_scaled, y_train)

# Evaluate
predictions = model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, predictions)

print("\n==============================")
print("MLP TRAINING COMPLETE")
print("==============================")
print("Accuracy:", round(accuracy, 4))
print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Save model
joblib.dump(
    model,
    os.path.join(MODEL_DIR, "mlp_injury_risk_model.pkl")
)

# Save scaler
joblib.dump(
    scaler,
    os.path.join(MODEL_DIR, "feature_scaler.pkl")
)

# Save feature columns
joblib.dump(
    feature_columns,
    os.path.join(MODEL_DIR, "feature_columns.pkl")
)

print("\nSaved files:")
print(os.path.join(MODEL_DIR, "mlp_injury_risk_model.pkl"))
print(os.path.join(MODEL_DIR, "feature_scaler.pkl"))
print(os.path.join(MODEL_DIR, "feature_columns.pkl"))