export interface ProductTrustIndicator {
  key: string
  label: string
  value: number | null
  risk_score: number | null
  weight: number
  explanation: string
}

export interface ProductTrust {
  product_id: string
  product_name: string
  review_count: number
  prediction_coverage: number
  predicted_review_count: number
  suspicious_review_count: number
  suspicious_percentage: number | null
  rating_distribution: Record<string, number>
  average_rating: number | null
  five_star_percentage: number | null
  campaign_count: number
  campaign_review_count: number
  campaign_involvement_percentage: number | null
  risk_score: number | null
  trust_score: number | null
  indicators: ProductTrustIndicator[]
  score_explanation: string
}

export type FeedbackDecision = 'correct' | 'incorrect' | 'needs_correction'

export interface FeedbackItem {
  id: number
  prediction_id: number
  review_db_id: number
  review_id: string
  product_id: string
  product_name: string
  prediction_classification: string
  decision: FeedbackDecision
  comment: string | null
  analyst_username: string
  created_at: string
  updated_at: string
}

export interface PredictionDetails {
  id: number
  review_id: number
  fraud_probability: number
  classification: string
  model_version: string
  text_risk: number
  behavior_risk: number
  temporal_risk: number
  similarity_risk: number
  graph_risk: number
  explanation: string | null
  created_at: string
}

export interface PaginatedFeedback {
  items: FeedbackItem[]
  total: number
  page: number
  page_size: number
  pages: number
}
