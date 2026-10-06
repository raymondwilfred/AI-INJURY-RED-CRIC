export const project = {
  title: 'AI-INJURY-RED-CRIC',
  subtitle: 'Cricket movement & screening research',
  recordCount: 21900,
  athleteCount: 30,
  positiveRecords: 137,
  negativeRecords: 21763,
  threshold: 2.08,
  selectedModel: 'SVM',
  selectionStatement:
    'SVM was selected as the high-sensitivity screening candidate because it achieved the highest recall and F1-score among the five evaluated models.',
  disclaimer: 'Screening indication only — not a medical diagnosis.',
  lowPrecision: 'Low precision: 5.64%.',
};

export const models = [
  { name: 'Random Forest', accuracy: 98.38, precision: 5.88, recall: 11.54, f1: 7.79 },
  { name: 'XGBoost', accuracy: 99.25, precision: 11.11, recall: 3.85, f1: 5.71 },
  { name: 'SVM', accuracy: 90.43, precision: 5.64, recall: 96.15, f1: 10.66 },
  { name: 'LightGBM', accuracy: 98.65, precision: 5.41, recall: 7.69, f1: 6.35 },
  { name: 'MLP', accuracy: 95.46, precision: 3.74, recall: 26.92, f1: 6.57 },
];

export const cvResults = [
  { model: 'YOLOv8n Cricket Detection', precision: 88.5, recall: 82.2, map50: 84.5, map5095: 69.5 },
  { model: 'BGT YOLOv8n Detection', precision: 90.85, recall: 94.74, map50: 91.935, map5095: 53.147 },
];

export const poseFeatures = [
  'Left knee angle', 'Right knee angle', 'Trunk angle', 'Shoulder angle', 'Hip angle', 'Shoulder-hip rotation',
];
export const svmInputs = ['game_workload', 'groin_squeeze', 'hip_mobility'];
export const methodology = [
  { title: 'Data Collection', description: 'Anonymized cricket player and workload records inform the structured screening dataset. Video is a separate computer-vision input.', detail: '30 athletes · 21,900 structured records' },
  { title: 'Computer Vision', description: 'YOLOv8n detects cricket objects in image and video frames.', detail: 'Validated detection metrics are shown in Model Comparison.' },
  { title: 'Pose Estimation', description: 'YOLOv8n-Pose estimates a 17-point COCO body-keypoint representation.', detail: '17 COCO keypoints' },
  { title: 'Biomechanical Feature Extraction', description: 'Geometric movement features are derived from keypoint positions.', detail: poseFeatures.join(' · ') },
  { title: 'Structured Injury Dataset', description: 'The supplied labeled dataset contains positive and negative injury-labeled records.', detail: '21,900 records · 137 positive · 21,763 negative' },
  { title: 'Machine Learning', description: 'Five models were evaluated on structured data. SVM uses only the specified workload and fitness inputs.', detail: 'Random Forest · XGBoost · SVM · LightGBM · MLP' },
  { title: 'Evaluation', description: 'Held-out test metrics include accuracy, precision, recall, F1-score and confusion-matrix evaluation.', detail: 'Compare model metrics without selecting by accuracy alone.' },
  { title: 'Screening', description: 'SVM is presented as the high-sensitivity candidate. Player indications are structured screening outputs.', detail: 'Threshold: 2.08%' },
];

// All 30 per-player report rows are transcribed from notebook cell 197. Values
// remain strings to preserve the supplied display precision; history is context only.
const playerRows = `001|730|12|Previous injury records present|0.00|339.00|52.00|0.0386%
002|730|7|Previous injury records present|0.00|133.00|32.00|0.0406%
003|730|9|Previous injury records present|0.00|94.00|37.00|0.0371%
004|730|5|Previous injury records present|0.00|339.00|53.00|0.0401%
005|730|1|Previous injury records present|0.00|252.00|34.00|0.0526%
006|730|2|Previous injury records present|0.00|104.00|50.00|0.0528%
007|730|4|Previous injury records present|0.00|110.00|30.00|0.0351%
008|730|2|Previous injury records present|0.00|172.00|40.00|0.0554%
009|730|1|Previous injury records present|0.00|311.00|19.00|0.0570%
010|730|4|Previous injury records present|0.00|187.00|26.00|0.0525%
011|730|3|Previous injury records present|0.00|94.00|50.00|0.0507%
012|730|5|Previous injury records present|0.00|182.00|27.00|0.0511%
013|730|0|No previous injury records present|0.00|316.00|55.00|0.0434%
014|730|3|Previous injury records present|0.00|353.00|38.00|0.0405%
015|730|3|Previous injury records present|0.00|111.00|35.00|0.0382%
016|730|1|Previous injury records present|0.00|364.00|56.00|0.0463%
017|730|4|Previous injury records present|0.00|263.00|36.00|0.0491%
018|730|7|Previous injury records present|0.00|176.00|25.00|0.0511%
019|730|2|Previous injury records present|0.00|320.00|40.00|0.0380%
020|730|6|Previous injury records present|470.00|160.00|48.00|5.40%
021|730|5|Previous injury records present|0.00|173.00|38.00|0.0536%
022|730|10|Previous injury records present|0.00|233.00|43.00|0.0474%
023|730|3|Previous injury records present|0.00|185.00|43.00|0.0566%
024|730|5|Previous injury records present|0.00|312.00|44.00|0.0348%
025|730|12|Previous injury records present|0.00|206.00|43.00|0.0533%
026|730|2|Previous injury records present|0.00|207.00|36.00|0.0535%
027|730|4|Previous injury records present|0.00|191.00|53.00|0.0558%
028|730|5|Previous injury records present|0.00|142.00|28.00|0.0423%
029|730|7|Previous injury records present|385.00|242.00|38.00|6.0444%
030|730|3|Previous injury records present|0.00|95.00|38.00|0.0388%`;

export const players = playerRows.split('\n').map((line) => {
  const [id, totalRecords, injuryRecords, historicalStatus, workload, groin, hip, probability] = line.split('|');
  const higher = id === '020' || id === '029';
  return {
    id: `Player ${id}`, numericId: Number(id), date: '2018-04-30',
    totalRecords: Number(totalRecords), injuryRecords: Number(injuryRecords), historicalStatus,
    workload, groin, hip, probability, threshold: '2.08%',
    result: higher ? 'Higher-risk screening indication' : 'Lower-risk screening indication',
  };
});

export type PlayerReport = (typeof players)[number];
