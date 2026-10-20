export interface Dataset {
  id: string;
  original_filename: string;
  n_rows: number;
  n_cols: number;
  columns: string[];
  created_at: string;
  is_cleaned: boolean;
}

export interface ColumnProfile {
  name: string;
  dtype: string;
  inferred_type: "numeric" | "categorical" | "datetime" | "boolean";
  missing_count: number;
  missing_pct: number;
  unique_count: number;
  high_cardinality: boolean;
  mean?: number | null;
  std?: number | null;
  min?: number | null;
  max?: number | null;
  median?: number | null;
  top_values?: Record<string, number>;
}

export interface DatasetProfile {
  n_rows: number;
  n_cols: number;
  duplicate_rows: number;
  duplicate_pct: number;
  numeric_columns: string[];
  categorical_columns: string[];
  columns: ColumnProfile[];
  target_candidates: string[];
  class_imbalance: { column: string; majority_pct: number; imbalance_ratio: number }[];
  total_missing_cells: number;
}

export interface EDAResult {
  descriptive_stats: Record<string, Record<string, number>>;
  correlations: Record<string, Record<string, number>>;
  strong_correlations: { col1: string; col2: string; correlation: number }[];
  categorical_frequencies: Record<string, Record<string, number>>;
  skewness: Record<string, number>;
  outliers: Record<string, { count: number; pct: number; lower_bound: number; upper_bound: number }>;
  insights: string[];
}

export interface ChartResult {
  chart_type: string;
  x: string | null;
  y: string | null;
  data: any[];
  meta: Record<string, any>;
  interpretation: string;
}

export interface AskResult {
  question: string;
  sql: string;
  sql_source: string;
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  chart: { chart_type: string; data: any[] } | null;
  explanation: string;
  error: string | null;
}

export interface TrainResult {
  model_id: string;
  metrics: Record<string, any>;
  problem_type: string;
  algorithm: string;
  feature_columns: string[];
  target: string | null;
  tuning?: { before: any; after: any; best_params: Record<string, any>; tuned: boolean };
}

export interface ModelSummary {
  id: string;
  dataset_id: string;
  target: string | null;
  problem_type: string;
  algorithm: string;
  feature_columns: string[];
  metrics: Record<string, any>;
  created_at: string;
}

export interface DashboardKPIs {
  dataset_id: string;
  rows: number;
  columns: number;
  missing_cells: number;
  duplicate_rows: number;
  numeric_columns: number;
  categorical_columns: number;
  is_cleaned: boolean;
  models_trained: number;
  best_model: { id: string; algorithm: string; target: string; metrics: Record<string, any> } | null;
}
