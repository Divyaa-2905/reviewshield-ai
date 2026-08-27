import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { ErrorState, LoadingState } from '../components/ui'

export function SettingsPage() {
  const [health, setHealth] = useState<any>(null)
  const [model, setModel] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.health(), api.modelInfo()])
      .then(([h, m]) => { setHealth(h); setModel(m) })
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!health) return <LoadingState />

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Settings</h1>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h2 className="font-semibold text-white">API Status</h2>
          <p className="mt-2 text-emerald-400">{health.status}</p>
          <p className="text-sm text-slate-400">Version: {health.version}</p>
          <p className="text-sm text-slate-400">Environment: {health.environment}</p>
        </div>
        {model && (
          <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
            <h2 className="font-semibold text-white">Model Info</h2>
            <p className="mt-2 text-sm text-slate-300">Version: {model.model_version}</p>
            <p className="text-sm text-slate-300">Device: {model.device}</p>
            <p className="text-sm text-slate-300">Status: {model.status}</p>
            <p className="mt-2 text-xs text-slate-500">Modalities: {model.modalities?.join(', ')}</p>
          </div>
        )}
      </div>
      <div className="mt-6 rounded-xl border border-amber-800/50 bg-amber-950/30 p-4">
        <p className="text-sm text-amber-200">
          Demo credentials: admin/admin123, analyst/analyst123, viewer/viewer123
        </p>
      </div>
    </div>
  )
}
