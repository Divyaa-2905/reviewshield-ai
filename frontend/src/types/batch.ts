export interface BatchValidationRow {
  row_number: number
  review_text: string
  rating: number | null
  reviewer_id: string | null
  review_id: string | null
  review_timestamp: string | null
  errors: string[]
}

export interface BatchValidationResponse {
  total_rows: number
  valid_rows: number
  invalid_rows: number
  rows: BatchValidationRow[]
}

export interface BatchAnalysisResult {
  row_number: number
  review_id: string | null
  reviewer_id: string | null
  review_text: string
  rating: number
  fraud_probability: number
  classification: string
  model_version: string
  text_risk: number
  behavior_risk: number
  temporal_risk: number
  similarity_risk: number
  graph_risk: number
  explanation: string | null
}

export interface BatchAnalysisResponse {
  total_rows: number
  statistics: {
    average_fraud_probability: number
    high_risk_count: number
    classification_counts: Record<string, number>
  }
  results: BatchAnalysisResult[]
}
