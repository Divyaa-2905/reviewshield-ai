import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState } from '../components/ui'

export function ClustersPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.clusters().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState />
  if (!data.items.length) return <EmptyState message="No fraud clusters detected." />

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Fraud Clusters</h1>
      <div className="space-y-4">
        {data.items.map((c: any) => (
          <div key={c.id} className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
            <div className="flex items-center justify-between">
              <h3 className="font-mono text-white">{c.cluster_id}</h3>
              <span className={`text-lg font-bold ${c.risk_score > 0.7 ? 'text-rose-400' : 'text-amber-400'}`}>
                {Math.round(c.risk_score * 100)}% risk
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-400">
              {c.reviewer_count} reviewers, {c.product_count} products, {c.review_count} reviews
            </p>
            <p className="mt-3 text-sm text-slate-300">{c.explanation}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {c.reviewers?.map((r: string) => (
                <span key={r} className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-400">{r}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
