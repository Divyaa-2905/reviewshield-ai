import { useEffect, useState } from 'react'
import { fetchHealth } from '../services/api'
import type { HealthResponse } from '../types/health'

type ConnectionState = 'loading' | 'connected' | 'error'

export function HealthStatus() {
  const [state, setState] = useState<ConnectionState>('loading')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function checkHealth() {
      try {
        const data = await fetchHealth()
        if (!active) return
        setHealth(data)
        setState('connected')
        setError(null)
      } catch (err) {
        if (!active) return
        setState('error')
        setError(err instanceof Error ? err.message : 'Unknown error')
      }
    }

    void checkHealth()
    const interval = window.setInterval(() => void checkHealth(), 15000)

    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [])

  const statusColor =
    state === 'connected' ? 'bg-emerald-500' : state === 'error' ? 'bg-rose-500' : 'bg-amber-400'

  const statusLabel =
    state === 'connected' ? 'Connected' : state === 'error' ? 'Disconnected' : 'Checking...'

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Backend Status</h2>
        <span className="inline-flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1 text-sm">
          <span className={`h-2.5 w-2.5 rounded-full ${statusColor}`} />
          {statusLabel}
        </span>
      </div>

      {state === 'loading' && (
        <p className="text-sm text-slate-400">Checking backend connectivity...</p>
      )}

      {state === 'error' && (
        <div className="space-y-2">
          <p className="text-sm text-rose-300">
            Unable to reach the backend API. Start it with <code className="rounded bg-slate-800 px-1">make dev-backend</code>.
          </p>
          {error && <p className="text-xs text-slate-500">{error}</p>}
        </div>
      )}

      {state === 'connected' && health && (
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-slate-400">Service</dt>
            <dd className="font-medium text-white">{health.service}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Status</dt>
            <dd className="font-medium text-emerald-300">{health.status}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Version</dt>
            <dd className="font-medium text-white">{health.version}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Environment</dt>
            <dd className="font-medium text-white">{health.environment}</dd>
          </div>
        </dl>
      )}
    </div>
  )
}
