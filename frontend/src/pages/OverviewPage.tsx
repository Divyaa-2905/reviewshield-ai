import { useEffect, useState } from 'react'
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../services/api'
import { ErrorState, LoadingState, StatCard } from '../components/ui'

export function OverviewPage() {
  const [stats, setStats] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.dashboard().then(setStats).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!stats) return <LoadingState />

  const chartData = [
    { name: 'Genuine', count: stats.genuine_reviews },
    { name: 'Suspicious', count: stats.suspicious_reviews },
    { name: 'Potentially Fake', count: stats.potentially_fake_reviews },
  ]

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Overview Dashboard</h1>
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard label="Total Reviews" value={stats.total_reviews} />
        <StatCard label="Suspicious Reviews" value={stats.suspicious_reviews} accent="text-amber-400" />
        <StatCard label="Potentially Fake" value={stats.potentially_fake_reviews} accent="text-rose-400" />
        <StatCard label="Genuine Reviews" value={stats.genuine_reviews} accent="text-emerald-400" />
        <StatCard label="High-Risk Reviewers" value={stats.high_risk_reviewers} accent="text-rose-400" />
        <StatCard label="Suspicious Clusters" value={stats.suspicious_clusters} accent="text-amber-400" />
      </div>
      <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">Classification Distribution</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155' }} />
            <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
