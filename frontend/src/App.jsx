import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "https://ai-injury-red-cric.onrender.com/api/analyze";
const INITIAL_PLAYER = {
  age: "",
  player_type: "Batsman",
  experience_years: "",
  height_cm: "",
  weight_kg: "",
  bmi: "",
  body_fat_percent: "",
  training_hours_week: "",
  bowling_overs_week: "",
  batting_hours_week: "",
  strength_training_hours: "",
  matches_last_month: "",
  days_since_last_match: "",
  previous_injuries_count: "",
  last_injury_days_ago: "",
  recovery_days_last_injury: "",
  fatigue_level: "",
  sleep_hours_day: "",
  stress_level: "",
  fitness_score: "",
};

const FIELD_RULES = {
  age: { min: 10, max: 60, label: "Age" },
  experience_years: {
    min: 0,
    max: 50,
    label: "Experience years",
  },
  height_cm: {
    min: 100,
    max: 250,
    label: "Height",
  },
  weight_kg: {
    min: 30,
    max: 200,
    label: "Weight",
  },
  bmi: {
    min: 10,
    max: 60,
    label: "BMI",
  },
  body_fat_percent: {
    min: 0,
    max: 60,
    label: "Body fat percentage",
  },
  training_hours_week: {
    min: 0,
    max: 168,
    label: "Training hours per week",
  },
  bowling_overs_week: {
    min: 0,
    max: 200,
    label: "Bowling overs per week",
  },
  batting_hours_week: {
    min: 0,
    max: 168,
    label: "Batting hours per week",
  },
  strength_training_hours: {
    min: 0,
    max: 168,
    label: "Strength training hours",
  },
  matches_last_month: {
    min: 0,
    max: 31,
    label: "Matches last month",
  },
  days_since_last_match: {
    min: 0,
    max: 3650,
    label: "Days since last match",
  },
  previous_injuries_count: {
    min: 0,
    max: 4,
    label: "Previous injuries count",
  },
  last_injury_days_ago: {
    min: 0,
    max: 3650,
    label: "Days since last injury",
  },
  recovery_days_last_injury: {
    min: 0,
    max: 365,
    label: "Recovery days",
  },
  fatigue_level: {
    min: 0,
    max: 10,
    label: "Fatigue level",
  },
  sleep_hours_day: {
    min: 1,
    max: 24,
    label: "Sleep hours per day",
  },
  stress_level: {
    min: 0,
    max: 10,
    label: "Stress level",
  },
  fitness_score: {
    min: 0,
    max: 100,
    label: "Fitness score",
  },
};

function formatPercent(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "N/A";
  }

  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatAngle(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "N/A";
  }

  return `${Number(value).toFixed(1)}°`;
}

function getRiskClass(risk) {
  const value = String(risk || "").toLowerCase();

  if (value === "high") {
    return "risk-high";
  }

  if (value === "medium") {
    return "risk-medium";
  }

  if (value === "low") {
    return "risk-low";
  }

  return "risk-unknown";
}

function App() {
  const [player, setPlayer] = useState(INITIAL_PLAYER);
  const [file, setFile] = useState(null);

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setResult(null);
    setError("");
    setSuccess("");
  }, [file]);

  function handleChange(event) {
    const { name, value } = event.target;

    setPlayer((previous) => ({
      ...previous,
      [name]: value,
    }));

    setResult(null);
    setError("");
    setSuccess("");
  }

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0] || null;

    if (!selectedFile) {
      setFile(null);
      return;
    }

    const allowedTypes = [
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setFile(null);
      setError("Please upload a JPG, PNG or WEBP image.");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setFile(null);
      setError("Image size must be less than 10 MB.");
      return;
    }

    setFile(selectedFile);
    setError("");
  }

  function validatePlayer() {
    for (const [field, rule] of Object.entries(FIELD_RULES)) {
      const value = Number(player[field]);

      if (player[field] === "" || player[field] === null) {
        return `${rule.label} is required.`;
      }

      if (!Number.isFinite(value)) {
        return `${rule.label} must be a valid number.`;
      }

      if (value < rule.min || value > rule.max) {
        return `${rule.label} must be between ${rule.min} and ${rule.max}.`;
      }
    }

    if (Number(player.previous_injuries_count) > 4) {
      return "Previous injuries count cannot be greater than 4.";
    }

    if (Number(player.sleep_hours_day) <= 0) {
      return "Sleep hours must be greater than 0.";
    }

    return "";
  }

  async function analyzePlayer(event) {
    event.preventDefault();

    setResult(null);
    setError("");
    setSuccess("");

    if (!file) {
      setError("Please upload a cricket player image first.");
      return;
    }

    const validationError = validatePlayer();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      const form = new FormData();

      form.append("image", file);

      Object.entries(player).forEach(([key, value]) => {
        form.append(key, value);
      });

      const response = await fetch(API_URL, {
        method: "POST",
        body: form,
      });

      let data = null;

      try {
        data = await response.json();
      } catch {
        throw new Error(
          "The backend returned an invalid response."
        );
      }

      if (!response.ok) {
        const backendMessage =
          data?.detail ||
          data?.message ||
          data?.error ||
          "Analysis failed.";

        throw new Error(
          typeof backendMessage === "string"
            ? backendMessage
            : JSON.stringify(backendMessage)
        );
      }

      setResult(data);
      setSuccess("Analysis completed successfully.");
    } catch (err) {
      setResult(null);

      setError(
        err?.message ||
          "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const biomechanics = result?.biomechanics || {};
  const classProbabilities =
    result?.class_probabilities || {};

  return (
    <div className="page">

      {/* HERO */}
      <header className="hero-band">
        <div className="hero-content">

          <div className="brand-row">

            <div className="brand-icon">
              🩹
            </div>

            <div>
              <h1>
                AI Injury Red Cric
              </h1>

              <p>
                AI-based cricket movement and
                injury-risk analysis
              </p>
            </div>

          </div>

          <div className="hero-description">
            Analyze cricket player movement using
            computer vision, pose estimation,
            biomechanical measurements and
            machine learning.
          </div>

        </div>
      </header>

      {/* MAIN */}
      <main className="layout">

        {/* LEFT SIDE */}
        <section className="panel">

          {/* IMAGE */}
          <div className="section-title">

            <span className="section-number">
              01
            </span>

            <div>
              <h2>
                Player Movement Image
              </h2>

              <p>
                Upload an image of the cricket player
                for pose estimation and biomechanical
                analysis.
              </p>
            </div>

          </div>

          <div className="upload">

            <div className="upload-icon">
              📷
            </div>

            <h3>
              Upload player image
            </h3>

            <p>
              JPG, PNG or WEBP · Maximum 10 MB
            </p>

            <label className="file-button">
              Choose Image

              <input
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleFileChange}
              />
            </label>

            {file && (
              <div className="file-name">
                ✓ {file.name}
              </div>
            )}

          </div>

          {/* PLAYER FORM */}
          <form onSubmit={analyzePlayer}>

            <div className="section-title">

              <span className="section-number">
                02
              </span>

              <div>
                <h2>
                  Player Information
                </h2>

                <p>
                  Enter the structured player and
                  workload information.
                </p>
              </div>

            </div>

            <div className="grid">

              <div className="field">
                <label>Age</label>

                <input
                  type="number"
                  name="age"
                  value={player.age}
                  onChange={handleChange}
                  placeholder="e.g. 24"
                />
              </div>

              <div className="field">
                <label>Player type</label>

                <select
                  name="player_type"
                  value={player.player_type}
                  onChange={handleChange}
                >
                  <option value="Batsman">
                    Batsman
                  </option>

                  <option value="Bowler">
                    Bowler
                  </option>

                  <option value="All-Rounder">
                    All-Rounder
                  </option>
                </select>
              </div>

              <div className="field">
                <label>
                  Experience years
                </label>

                <input
                  type="number"
                  name="experience_years"
                  value={player.experience_years}
                  onChange={handleChange}
                  placeholder="e.g. 6"
                />
              </div>

              <div className="field">
                <label>
                  Height (cm)
                </label>

                <input
                  type="number"
                  name="height_cm"
                  value={player.height_cm}
                  onChange={handleChange}
                  placeholder="e.g. 178"
                />
              </div>

              <div className="field">
                <label>
                  Weight (kg)
                </label>

                <input
                  type="number"
                  name="weight_kg"
                  value={player.weight_kg}
                  onChange={handleChange}
                  placeholder="e.g. 72"
                />
              </div>

              <div className="field">
                <label>
                  BMI
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="bmi"
                  value={player.bmi}
                  onChange={handleChange}
                  placeholder="e.g. 22.7"
                />
              </div>

              <div className="field">
                <label>
                  Body fat (%)
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="body_fat_percent"
                  value={player.body_fat_percent}
                  onChange={handleChange}
                  placeholder="e.g. 14"
                />
              </div>

              <div className="field">
                <label>
                  Training hours/week
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="training_hours_week"
                  value={player.training_hours_week}
                  onChange={handleChange}
                  placeholder="e.g. 20"
                />
              </div>

              <div className="field">
                <label>
                  Bowling overs/week
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="bowling_overs_week"
                  value={player.bowling_overs_week}
                  onChange={handleChange}
                  placeholder="e.g. 35"
                />
              </div>

              <div className="field">
                <label>
                  Batting hours/week
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="batting_hours_week"
                  value={player.batting_hours_week}
                  onChange={handleChange}
                  placeholder="e.g. 12"
                />
              </div>

              <div className="field">
                <label>
                  Strength training hours
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="strength_training_hours"
                  value={player.strength_training_hours}
                  onChange={handleChange}
                  placeholder="e.g. 5"
                />
              </div>

              <div className="field">
                <label>
                  Matches last month
                </label>

                <input
                  type="number"
                  name="matches_last_month"
                  value={player.matches_last_month}
                  onChange={handleChange}
                  placeholder="e.g. 8"
                />
              </div>

              <div className="field">
                <label>
                  Days since last match
                </label>

                <input
                  type="number"
                  name="days_since_last_match"
                  value={player.days_since_last_match}
                  onChange={handleChange}
                  placeholder="e.g. 4"
                />
              </div>

              <div className="field">
                <label>
                  Previous injuries
                </label>

                <input
                  type="number"
                  name="previous_injuries_count"
                  value={player.previous_injuries_count}
                  onChange={handleChange}
                  placeholder="0 - 4"
                />
              </div>

              <div className="field">
                <label>
                  Days since last injury
                </label>

                <input
                  type="number"
                  name="last_injury_days_ago"
                  value={player.last_injury_days_ago}
                  onChange={handleChange}
                  placeholder="e.g. 300"
                />
              </div>

              <div className="field">
                <label>
                  Recovery days
                </label>

                <input
                  type="number"
                  name="recovery_days_last_injury"
                  value={player.recovery_days_last_injury}
                  onChange={handleChange}
                  placeholder="e.g. 30"
                />
              </div>

              <div className="field">
                <label>
                  Fatigue level (0-10)
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="fatigue_level"
                  value={player.fatigue_level}
                  onChange={handleChange}
                  placeholder="e.g. 4"
                />
              </div>

              <div className="field">
                <label>
                  Sleep hours/day
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="sleep_hours_day"
                  value={player.sleep_hours_day}
                  onChange={handleChange}
                  placeholder="e.g. 8"
                />
              </div>

              <div className="field">
                <label>
                  Stress level (0-10)
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="stress_level"
                  value={player.stress_level}
                  onChange={handleChange}
                  placeholder="e.g. 3"
                />
              </div>

              <div className="field">
                <label>
                  Fitness score (0-100)
                </label>

                <input
                  type="number"
                  step="0.1"
                  name="fitness_score"
                  value={player.fitness_score}
                  onChange={handleChange}
                  placeholder="e.g. 85"
                />
              </div>

            </div>

            {error && (
              <div className="error">
                <strong>
                  Analysis error
                </strong>

                <span>
                  {error}
                </span>
              </div>
            )}

            {success && !error && (
              <div className="success">
                ✓ {success}
              </div>
            )}

            <button
              className="analyze"
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Analyzing player..."
                : "Analyze Injury Risk"}
            </button>

          </form>

        </section>

        {/* RIGHT SIDE */}
        <section className="panel result-panel">

          <div className="section-title">

            <span className="section-number">
              03
            </span>

            <div>
              <h2>
                AI Analysis
              </h2>

              <p>
                Risk prediction and computer-vision
                analysis results.
              </p>
            </div>

          </div>

          {/* BEFORE ANALYSIS */}
          {!result && !loading && (
            <div className="empty-state">

              <div className="empty-icon">
                🧠
              </div>

              <h3>
                Ready for analysis
              </h3>

              <p>
                Upload a player image and enter the
                player information, then click
                <strong>
                  {" "}Analyze Injury Risk
                </strong>.
              </p>

            </div>
          )}

          {/* LOADING */}
          {loading && (
            <div className="loading-state">

              <div className="spinner"></div>

              <h3>
                Analyzing player...
              </h3>

              <p>
                Running pose estimation,
                biomechanics and injury-risk
                prediction.
              </p>

            </div>
          )}

          {/* RESULTS */}
          {result && !loading && (
            <>

              {/* RISK */}
              <div
                className={`risk-card ${getRiskClass(
                  result.risk
                )}`}
              >

                <div className="risk-label">
                  INJURY RISK
                </div>

                <div className="risk-value">
                  {String(
                    result.risk || "Unknown"
                  )}
                </div>

                <div className="confidence">
                  Model confidence:{" "}
                  <strong>
                    {formatPercent(
                      result.confidence
                    )}
                  </strong>
                </div>

              </div>

              {/* PROBABILITIES */}
              <div className="result-card">

                <div className="card-heading">

                  <h3>
                    Risk probabilities
                  </h3>

                  <span>
                    ML classification
                  </span>

                </div>

                <div className="probability-list">

                  {["Low", "Medium", "High"].map(
                    (risk) => {

                      const probability =
                        classProbabilities[risk] ??
                        0;

                      return (
                        <div
                          className="probability-row"
                          key={risk}
                        >

                          <div className="probability-header">

                            <span>
                              {risk}
                            </span>

                            <strong>
                              {formatPercent(
                                probability
                              )}
                            </strong>

                          </div>

                          <div className="progress">

                            <div
                              className={`progress-bar progress-${risk.toLowerCase()}`}
                              style={{
                                width: `${Math.max(
                                  0,
                                  Math.min(
                                    100,
                                    Number(
                                      probability
                                    ) * 100
                                  )
                                )}%`,
                              }}
                            />

                          </div>

                        </div>
                      );
                    }
                  )}

                </div>

              </div>

              {/* BIOMECHANICAL ANALYSIS */}
              <div className="result-card">

                <div className="card-heading">

                  <h3>
                    Biomechanical analysis
                  </h3>

                  <span>
                    Pose-derived geometry
                  </span>

                </div>

                {result.biomechanics_valid === false ? (
                  <div className="warning">
                    Pose landmarks were not sufficient
                    to calculate all biomechanical
                    measurements.
                  </div>
                ) : (
                  <div className="biomechanics">

                    <div className="bio-item">
                      <span>
                        Left knee angle
                      </span>

                      <strong>
                        {formatAngle(
                          biomechanics.left_knee_angle
                        )}
                      </strong>
                    </div>

                    <div className="bio-item">
                      <span>
                        Right knee angle
                      </span>

                      <strong>
                        {formatAngle(
                          biomechanics.right_knee_angle
                        )}
                      </strong>
                    </div>

                    <div className="bio-item">
                      <span>
                        Trunk angle
                      </span>

                      <strong>
                        {formatAngle(
                          biomechanics.trunk_angle
                        )}
                      </strong>
                    </div>

                    <div className="bio-item">
                      <span>
                        Shoulder line angle
                      </span>

                      <strong>
                        {formatAngle(
                          biomechanics.shoulder_line_angle
                        )}
                      </strong>
                    </div>

                    <div className="bio-item">
                      <span>
                        Hip line angle
                      </span>

                      <strong>
                        {formatAngle(
                          biomechanics.hip_line_angle
                        )}
                      </strong>
                    </div>

                    <div className="bio-item">
                      <span>
                        Shoulder-hip rotation
                      </span>

                      <strong>
                        {formatAngle(
                          biomechanics.shoulder_hip_angle_difference
                        )}
                      </strong>
                    </div>

                  </div>
                )}

              </div>

              {/* POSE ESTIMATION */}
              <div className="result-card">

                <div className="card-heading">

                  <h3>
                    Pose estimation
                  </h3>

                </div>

                <div className="metric-grid">

                  <div className="metric">

                    <strong>
                      Persons detected
                    </strong>

                    <span>
                      {result.persons_detected ?? 0}
                    </span>

                  </div>

                  <div className="metric">

                    <strong>
                      Person used
                    </strong>

                    <span>
                      {result.person_used ?? "N/A"}
                    </span>

                  </div>

                </div>

              </div>

              {/* COMPUTER VISION OUTPUT */}
              {(result.original_image ||
                result.annotated_image) && (
                <div className="result-card">

                  <div className="card-heading">

                    <h3>
                      Computer vision output
                    </h3>

                  </div>

                  <div className="images">

                    {result.original_image && (
                      <div className="image-card">

                        <h4>
                          Original
                        </h4>

                        <img
                          src={result.original_image}
                          alt="Original cricket player"
                        />

                      </div>
                    )}

                    {result.annotated_image && (
                      <div className="image-card">

                        <h4>
                          Pose annotated
                        </h4>

                        <img
                          src={result.annotated_image}
                          alt="Pose estimation output"
                        />

                      </div>
                    )}

                  </div>

                </div>
              )}

              {/* PIPELINE */}
              <div className="result-card">

                <div className="card-heading">

                  <h3>
                    AI pipeline
                  </h3>

                </div>

                <div className="pipeline">

                  <div>
                    📷 Player image
                  </div>

                  <div className="arrow">
                    ↓
                  </div>

                  <div>
                    🤖 YOLO pose estimation
                  </div>

                  <div className="arrow">
                    ↓
                  </div>

                  <div>
                    🦴 17 body keypoints
                  </div>

                  <div className="arrow">
                    ↓
                  </div>

                  <div>
                    📐 Biomechanical features
                  </div>

                  <div className="arrow">
                    ↓
                  </div>

                  <div>
                    🧠 Injury-risk ML model
                  </div>

                  <div className="arrow">
                    ↓
                  </div>

                  <div>
                    📊 Risk classification
                  </div>

                </div>

              </div>

            </>
          )}

        </section>

      </main>

      {/* DISCLAIMER */}
      <footer className="disclaimer">

        <strong>
          ⚠️ Research prototype:
        </strong>{" "}

        This system is designed for academic and
        research purposes. The prediction is an
        AI-based risk estimate and does not replace
        professional medical assessment, diagnosis
        or treatment.

      </footer>

    </div>
  );
}

export default App;
