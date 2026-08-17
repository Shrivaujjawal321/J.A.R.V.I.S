import type { AuditResult, DatasetCard, UploadQuota } from "./types";

export const MOCK_AUDIT_RESULT: AuditResult = {
  audit_id: "audit_demo_001",
  dataset_id: "ds_tata_blast_furnace_01",
  filename: "blast_furnace_sensor_data.csv",
  dataset_type: "time_series",
  n_rows: 48320,
  n_cols: 23,
  composite_score: 74,
  grade: "B+",
  // v2 fields
  status: "scored",
  rank: 4,
  relevance_score: 88,
  tags: ["blast-furnace", "time-series", "sensor"],
  file_size_bytes: 12582912, // ~12 MB
  sub_scores: {
    completeness: {
      score: 88,
      weight: 0.15,
      detail: "2.3% missing values across 4 columns. Sensor_07 has highest gap at 8.1%.",
      severity: "info",
    },
    class_balance: {
      score: 62,
      weight: 0.12,
      detail: "Fault events are 3.1% of total records — imbalanced. Minority class needs augmentation.",
      severity: "warning",
    },
    label_quality: {
      score: 91,
      weight: 0.18,
      detail: "Labels appear consistent. 0.4% suspect annotation rate detected via proximity analysis.",
      severity: "ok",
    },
    duplicates: {
      score: 96,
      weight: 0.08,
      detail: "Only 0.1% duplicate rows. Dataset is clean on this dimension.",
      severity: "ok",
    },
    outliers: {
      score: 71,
      weight: 0.10,
      detail: "Temperature columns show 4.2% statistical outliers. Likely real process excursions, but worth flagging.",
      severity: "warning",
    },
    schema_validity: {
      score: 84,
      weight: 0.08,
      detail: "2 columns have mixed-type ambiguities. pressure_bar has 12 string entries in an otherwise numeric column.",
      severity: "info",
    },
    leakage: {
      score: 78,
      weight: 0.12,
      detail: "Mild correlation risk: output_temp is 0.82 correlated with target. May cause training-time leakage.",
      severity: "warning",
    },
    temporal_coverage: {
      score: 85,
      weight: 0.07,
      detail: "Covers 14 months. 3 gaps >6 hours detected in Jan and Mar periods.",
      severity: "info",
    },
    feature_redundancy: {
      score: 68,
      weight: 0.05,
      detail: "5 feature pairs with correlation >0.92. Dimensionality reduction recommended.",
      severity: "warning",
    },
    distribution_sanity: {
      score: 80,
      weight: 0.05,
      detail: "Most features follow expected industrial distributions. iron_flow shows slight bimodality — worth investigating.",
      severity: "info",
    },
  },
  readiness: {
    readiness_pct: 71,
    baseline_auc: 0.81,
    target_auc: 0.88,
    penalties: {
      class_imbalance: -8,
      feature_leakage: -6,
      missing_values: -3,
      redundant_features: -4,
      schema_errors: -2,
    },
  },
  review: `This dataset has real industrial value — the temporal depth is strong at 14 months, and label quality is excellent which is rare in sensor data. The primary issue holding it back is class imbalance: fault events represent only 3.1% of records, which will cause most classifiers to underperform on the minority class that actually matters.

The leakage risk on output_temp needs attention before training — it's the kind of subtle issue that inflates validation scores but fails in production. The 5 highly-correlated feature pairs are adding noise without adding signal.

Fix the imbalance, drop or flag the leaky column, and remove redundant features — this dataset could realistically move from B+ to A territory with those three changes.`,
  improvements: [
    {
      dimension: "class_balance",
      priority: "P0",
      title: "Address class imbalance in fault labels",
      description:
        "Use SMOTE oversampling or class-weight adjustment. At 3.1% minority rate, most classifiers will learn to ignore fault detection entirely. This is your highest-priority fix.",
      estimated_score_delta: 12,
      effort: "medium",
    },
    {
      dimension: "leakage",
      priority: "P0",
      title: "Remove or isolate output_temp from training features",
      description:
        "output_temp correlates 0.82 with target. This column likely contains information only available after the event you're predicting. Keep it for analysis, exclude from feature set.",
      estimated_score_delta: 8,
      effort: "low",
    },
    {
      dimension: "feature_redundancy",
      priority: "P1",
      title: "Drop 3–5 highly correlated features",
      description:
        "5 feature pairs with correlation >0.92. Run PCA or Variance Inflation Factor analysis. Reducing redundancy improves model generalization and reduces training time.",
      estimated_score_delta: 5,
      effort: "low",
    },
    {
      dimension: "completeness",
      priority: "P1",
      title: "Impute missing values in Sensor_07",
      description:
        "8.1% missing on Sensor_07. Forward-fill or interpolation is appropriate for time-series sensor data. This reduces information loss and improves model stability.",
      estimated_score_delta: 4,
      effort: "low",
    },
    {
      dimension: "schema_validity",
      priority: "P2",
      title: "Fix mixed-type entries in pressure_bar",
      description:
        "12 string entries in pressure_bar. Likely sensor error codes stored as strings. Map to NaN or a dedicated error flag column.",
      estimated_score_delta: 3,
      effort: "low",
    },
    {
      dimension: "outliers",
      priority: "P2",
      title: "Validate temperature outliers with domain knowledge",
      description:
        "4.2% outlier rate in temperature columns may represent real process excursions. Confirm with plant engineers: if real events, keep them — they're valuable signal. If sensor errors, cap/clip.",
      estimated_score_delta: 2,
      effort: "medium",
    },
  ],
  preview: {
    columns: [
      { name: "timestamp", dtype: "datetime64", null_pct: 0.0 },
      { name: "furnace_id", dtype: "int64", null_pct: 0.0 },
      { name: "iron_flow", dtype: "float64", null_pct: 1.2 },
      { name: "pressure_bar", dtype: "object", null_pct: 0.8 },
      { name: "temp_top", dtype: "float64", null_pct: 0.3 },
      { name: "temp_mid", dtype: "float64", null_pct: 0.5 },
      { name: "temp_bottom", dtype: "float64", null_pct: 0.3 },
      { name: "output_temp", dtype: "float64", null_pct: 0.1 },
      { name: "sensor_07", dtype: "float64", null_pct: 8.1 },
      { name: "fault_label", dtype: "int64", null_pct: 0.0 },
    ],
    sample_rows: [
      {
        timestamp: "2024-01-15 08:00:00",
        furnace_id: 3,
        iron_flow: 142.3,
        pressure_bar: "12.4",
        temp_top: 1482.1,
        temp_mid: 1421.7,
        temp_bottom: 1398.2,
        output_temp: 1441.5,
        sensor_07: 0.84,
        fault_label: 0,
      },
      {
        timestamp: "2024-01-15 08:05:00",
        furnace_id: 3,
        iron_flow: 143.1,
        pressure_bar: "12.6",
        temp_top: 1485.4,
        temp_mid: 1424.2,
        temp_bottom: 1401.0,
        output_temp: 1444.2,
        sensor_07: null,
        fault_label: 0,
      },
      {
        timestamp: "2024-01-15 08:10:00",
        furnace_id: 3,
        iron_flow: 138.9,
        pressure_bar: "ERR",
        temp_top: 1521.8,
        temp_mid: 1462.1,
        temp_bottom: 1439.7,
        output_temp: 1481.3,
        sensor_07: 0.91,
        fault_label: 1,
      },
    ],
  },
};

export const MOCK_IMPROVED_AUDIT_RESULT: AuditResult = {
  ...MOCK_AUDIT_RESULT,
  audit_id: "audit_demo_002",
  composite_score: 86,
  grade: "A",
  status: "scored",
  rank: 2,
  relevance_score: 91,
  sub_scores: {
    ...MOCK_AUDIT_RESULT.sub_scores,
    class_balance: { score: 81, weight: 0.12, detail: "Fault events augmented via SMOTE. Class ratio now 18%. Well balanced for training.", severity: "ok" },
    leakage: { score: 92, weight: 0.12, detail: "output_temp removed from feature set. No remaining high-risk leakage paths.", severity: "ok" },
    feature_redundancy: { score: 88, weight: 0.05, detail: "3 redundant features dropped. Remaining pairs max correlation 0.71.", severity: "ok" },
    completeness: { score: 95, weight: 0.15, detail: "Sensor_07 imputed via forward-fill. Missing rate now <0.5% across all columns.", severity: "ok" },
  },
  readiness: {
    readiness_pct: 88,
    baseline_auc: 0.87,
    target_auc: 0.88,
    penalties: {
      missing_values: -1,
      schema_errors: -2,
    },
  },
  review: "Significant improvement from v1. The class balance fix and leakage removal have the greatest impact. This dataset is now production-ready for most industrial fault prediction workloads. Minor schema issues remain but are low-risk.",
  improvements: [
    {
      dimension: "schema_validity",
      priority: "P1",
      title: "Fix mixed-type entries in pressure_bar",
      description: "12 string entries remain. Map sensor error codes to a dedicated flag column.",
      estimated_score_delta: 3,
      effort: "low",
    },
  ],
};

export const MOCK_DATASETS: DatasetCard[] = [
  {
    audit_id: "ds_caster_quality", dataset_id: "ds_caster_quality",
    filename: "continuous_caster_quality.csv",
    composite_score: 91,
    grade: "A+",
    n_rows: 32100,
    n_cols: 31,
    download_count: 204,
    created_at: "2026-05-20T09:15:00Z",
    // v2
    rank: 1,
    relevance_score: 95,
    status: "scored",
    description: "Continuous caster sensor readings with quality labels from 2024 production run.",
    tags: ["continuous-caster", "quality", "labeled"],
    file_size_bytes: 8912896, // ~8.5 MB
  },
  {
    audit_id: "ds_ladle_refining", dataset_id: "ds_ladle_refining",
    filename: "ladle_refining_furnace.csv",
    composite_score: 83,
    grade: "A",
    n_rows: 19200,
    n_cols: 27,
    download_count: 115,
    created_at: "2026-05-15T10:00:00Z",
    // v2
    rank: 2,
    relevance_score: 90,
    status: "scored",
    description: "Ladle furnace temperature and chemistry logs with maintenance event labels.",
    tags: ["ladle", "maintenance", "time-series"],
    file_size_bytes: 5242880, // ~5 MB
  },
  {
    audit_id: "ds_tata_blast_furnace_01", dataset_id: "ds_tata_blast_furnace_01",
    filename: "blast_furnace_sensor_data.csv",
    composite_score: 86,
    grade: "A",
    n_rows: 48320,
    n_cols: 23,
    download_count: 142,
    created_at: "2026-06-01T08:00:00Z",
    // v2
    rank: 3,
    relevance_score: 88,
    status: "scored",
    description: "14-month blast furnace sensor stream with fault labels. Strong temporal coverage.",
    tags: ["blast-furnace", "sensor", "fault-detection"],
    file_size_bytes: 12582912, // ~12 MB
  },
  {
    audit_id: "ds_slag_composition", dataset_id: "ds_slag_composition",
    filename: "slag_composition_samples.csv",
    composite_score: 79,
    grade: "B+",
    n_rows: 8900,
    n_cols: 12,
    download_count: 61,
    created_at: "2026-06-05T16:45:00Z",
    // v2
    rank: 4,
    relevance_score: 82,
    status: "scored",
    description: "Chemical composition samples from slag processing with quality grades.",
    tags: ["slag", "composition", "quality"],
    file_size_bytes: 1572864, // ~1.5 MB
  },
  {
    audit_id: "ds_rolling_mill_vibration", dataset_id: "ds_rolling_mill_vibration",
    filename: "rolling_mill_vibration_2025.csv",
    composite_score: 71,
    grade: "B",
    n_rows: 124000,
    n_cols: 18,
    download_count: 89,
    created_at: "2026-05-28T14:30:00Z",
    // v2
    rank: 5,
    relevance_score: 76,
    status: "scored",
    description: "Vibration sensor data from rolling mill with anomaly annotations.",
    tags: ["rolling-mill", "vibration", "anomaly"],
    file_size_bytes: 26214400, // ~25 MB
  },
  {
    audit_id: "ds_hot_strip_mill", dataset_id: "ds_hot_strip_mill",
    filename: "hot_strip_mill_pass_data.csv",
    composite_score: 58,
    grade: "C+",
    n_rows: 67400,
    n_cols: 14,
    download_count: 37,
    created_at: "2026-06-03T11:00:00Z",
    // v2
    rank: 6,
    relevance_score: 65,
    status: "scored",
    description: "Hot strip mill pass data — partial labels, needs balance improvement.",
    tags: ["hot-strip", "production"],
    file_size_bytes: 9437184, // ~9 MB
  },
  {
    audit_id: "ds_rejected_iris", dataset_id: "ds_rejected_iris",
    filename: "iris_dataset.csv",
    composite_score: 0,
    grade: "F",
    n_rows: 150,
    n_cols: 5,
    download_count: 3,
    created_at: "2026-06-08T14:00:00Z",
    // v2 — rejected
    rank: null,
    relevance_score: 0,
    status: "rejected",
    rejection_reason: "Dataset contains flower classification data (Iris) which is not relevant to Tata Steel manufacturing processes.",
    tags: [],
    file_size_bytes: 4096,
  },
  {
    audit_id: "ds_processing_hot_strip_2", dataset_id: "ds_processing_hot_strip_2",
    filename: "hot_strip_mill_2026_q2.csv",
    composite_score: 0,
    grade: "F",
    n_rows: 0,
    n_cols: 0,
    download_count: 0,
    created_at: "2026-06-10T10:30:00Z",
    // v2 — processing
    rank: null,
    relevance_score: null,
    status: "processing",
    description: "Q2 2026 hot strip mill sensor readings — analysis in progress.",
    tags: [],
    file_size_bytes: 14680064, // ~14 MB
  },
];

// Mock upload quota
export const MOCK_QUOTA: UploadQuota = {
  used: 2,
  max: 5,
  remaining: 3,
};
