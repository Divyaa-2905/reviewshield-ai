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
  modelMetrics: () => request('/api/v1/analytics/model'),
  modelInfo: () => request('/api/v1/models/info'),
  reviews: (page = 1) => request(`/api/v1/reviews?page=${page}`),
  review: (id: string) => request(`/api/v1/reviews/${id}`),
  reviewers: (page = 1) => request(`/api/v1/reviewers?page=${page}`),
  reviewer: (id: string) => request(`/api/v1/reviewers/${id}`),
  products: (page = 1) => request(`/api/v1/products?page=${page}`),
  product: (id: string) => request(`/api/v1/products/${id}`),
  predictions: (page = 1) => request(`/api/v1/predictions?page=${page}`),
  predictionForReview: (id: number) => request(`/api/v1/predictions/review/${id}`),
  analyze: (data: object) => request('/api/v1/predictions/analyze', { method: 'POST', body: JSON.stringify(data) }),
  similarities: (reviewId: number) => request(`/api/v1/similarity/review/${reviewId}`),
  clusters: (page = 1) => request(`/api/v1/clusters?page=${page}`),
  cluster: (id: string) => request(`/api/v1/clusters/${id}`),
  graph: () => request('/api/v1/graph'),
}
