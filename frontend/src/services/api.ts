import type {
  BatchAnalysisResponse,
  BatchAnalysisResult,
  BatchValidationResponse,
  BatchValidationRow,
} from '../types/batch'
import type { CampaignsResponse, ModelMetrics } from '../types/analytics'
import type {
  FeedbackDecision,
  FeedbackItem,
  PaginatedFeedback,
  PredictionDetails,
  ProductTrust,
} from '../types/trust'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function getToken(): string | null {
  return localStorage.getItem('token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }
  return response.json()
}

async function downloadAuthenticated(path: string, defaultError: string): Promise<Blob> {
  const token = getToken()
  const headers: Record<string, string> = {}
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`${API_BASE}${path}`, { headers })
  if (response.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: defaultError }))
    throw new Error(err.detail || defaultError)
  }
  return response.blob()
}

export async function login(username: string, password: string) {
  const form = new URLSearchParams()
  form.append('username', username)
  form.append('password', password)
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  })
  if (!response.ok) throw new Error('Invalid credentials')
  return response.json()
}

export const api = {
  health: () => request('/health'),
  me: () => request('/api/v1/auth/me'),
  dashboard: () => request('/api/v1/analytics/dashboard'),
  modelMetrics: () => request<ModelMetrics>('/api/v1/analytics/model'),
  modelInfo: () => request('/api/v1/models/info'),
  reviews: (page = 1) => request(`/api/v1/reviews?page=${page}`),
  review: (id: string) => request(`/api/v1/reviews/${id}`),
  reviewers: (page = 1) => request(`/api/v1/reviewers?page=${page}`),
  reviewer: (id: string) => request(`/api/v1/reviewers/${id}`),
  products: (page = 1) => request(`/api/v1/products?page=${page}`),
  product: (id: string) => request(`/api/v1/products/${encodeURIComponent(id)}`),
  productTrust: (id: string): Promise<ProductTrust> =>
    request(`/api/v1/products/${encodeURIComponent(id)}/trust`),
  productReport: (id: string): Promise<Blob> =>
    downloadAuthenticated(`/api/v1/products/${encodeURIComponent(id)}/report.pdf`, 'PDF report download failed'),
  predictions: (page = 1) => request(`/api/v1/predictions?page=${page}`),
  predictionForReview: (id: number): Promise<PredictionDetails> =>
    request(`/api/v1/predictions/review/${id}`),
  analyze: (data: object) => request('/api/v1/predictions/analyze', { method: 'POST', body: JSON.stringify(data) }),
  feedbackForPrediction: (predictionId: number): Promise<FeedbackItem | null> =>
    request(`/api/v1/predictions/${predictionId}/feedback`),
  savePredictionFeedback: (
    predictionId: number,
    data: { decision: FeedbackDecision; comment: string | null },
  ): Promise<FeedbackItem> =>
    request(`/api/v1/predictions/${predictionId}/feedback`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  feedback: (page = 1, decision = ''): Promise<PaginatedFeedback> =>
    request(`/api/v1/feedback?page=${page}${decision ? `&decision=${decision}` : ''}`),
  exportFeedback: (decision = ''): Promise<Blob> =>
    downloadAuthenticated(
      `/api/v1/feedback/export${decision ? `?decision=${decision}` : ''}`,
      'Feedback CSV export failed',
    ),
  validateCsv: async (file: File): Promise<BatchValidationResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const headers: Record<string, string> = {}
    const token = getToken()
    if (token) headers.Authorization = `Bearer ${token}`

    const response = await fetch(`${API_BASE}/api/v1/predictions/batch/validate`, {
      method: 'POST',
      headers,
      body: formData,
    })
    if (response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      throw new Error('Unauthorized')
    }
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'CSV validation failed' }))
      throw new Error(err.detail || 'CSV validation failed')
    }
    return response.json()
  },
  analyzeBatch: (rows: BatchValidationRow[]): Promise<BatchAnalysisResponse> =>
    request('/api/v1/predictions/batch/analyze', {
      method: 'POST',
      body: JSON.stringify({ rows }),
    }),
  exportBatch: async (results: BatchAnalysisResult[]): Promise<Blob> => {
    const token = getToken()
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) headers.Authorization = `Bearer ${token}`
    const response = await fetch(`${API_BASE}/api/v1/predictions/batch/export`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ results }),
    })
    if (response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
      throw new Error('Unauthorized')
    }
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'CSV export failed' }))
      throw new Error(err.detail || 'CSV export failed')
    }
    return response.blob()
  },
  similarities: (reviewId: number) => request(`/api/v1/similarity/review/${reviewId}`),
  clusters: (page = 1) => request(`/api/v1/clusters?page=${page}`),
  cluster: (id: string) => request(`/api/v1/clusters/${id}`),
  campaigns: () => request<CampaignsResponse>('/api/v1/campaigns'),
  graph: () => request('/api/v1/graph'),
}
