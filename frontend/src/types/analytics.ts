export interface ConfusionMatrix {
  true_negative: number
  false_positive: number
  false_negative: number
  true_positive: number
}

export interface ModelMetrics {
  accuracy: number | null
  precision: number | null
  recall: number | null
  f1: number | null
  roc_auc: number | null
  pr_auc: number | null
  labeled_reviews: number
  total_predictions: number
  total_reviews: number
  training_reviews: number
  test_reviews: number
  threshold: number
  confusion_matrix: ConfusionMatrix | null
  data_source: string
  evaluation_protocol: string
  evaluation_note: string
  avg_fraud_probability: number
  modality_averages: Record<string, number>
  classification_distribution: Record<string, number>
}

export interface CampaignReview {
  review_id: string
  reviewer_id: string
  product_id: string
  rating: number
  review_timestamp: string
}

export interface Campaign {
  campaign_id: string
  risk_score: number
  reviewer_count: number
  product_count: number
  review_count: number
  connected_entities: {
    reviewers: string[]
    products: string[]
    reviews: CampaignReview[]
  }
  temporal_evidence: {
    risk_score: number
    burst_windows: number
    avg_interval_hours: number | null
    synchronized_pairs: number
    observations: string[]
  }
  similarity_evidence: {
    pair_count: number
    average_score: number
    max_score: number
    pairs: { review_a_id: string; review_b_id: string; similarity_score: number }[]
  }
  graph_evidence: {
    node_count: number
    edge_count: number
    similarity_link_count: number
  }
  explanation: string
}

export interface CampaignsResponse {
  campaigns: Campaign[]
  total: number
  data_source: string
}
