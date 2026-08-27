import { useEffect, useState } from 'react'
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../services/api'
import { ErrorState, LoadingState } from '../components/ui'

export function AnalyticsPage() {
  const [metrics, setMetrics] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.modelMetrics().then(setMetrics).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!metrics) return <LoadingState />

  const modalityData = metrics.modality_averages
    ? Object.entries(metrics.modality_averages).map(([k, v]) => ({
        name: k.replace('_', ' '),
        value: Math.round((v as number) * 100),
      }))
    : []

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Model Analytics</h1>
      <div className="mb-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-400">Total Predictions</p>
          <p className="text-3xl font-bold text-white">{metrics.total_predictions || 0}</p>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-400">Avg Fraud Probability</p>
          <p className="text-3xl font-bold text-amber-400">
            {metrics.avg_fraud_probability ? Math.round(metrics.avg_fraud_probability * 100) : 0}%
          </p>
        </div>
      </div>
      {modalityData.length > 0 && (
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">Modality Risk Averages</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={modalityData}>
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155' }} />
              <Bar dataKey="value" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
