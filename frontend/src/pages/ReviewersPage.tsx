import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState } from '../components/ui'

export function ReviewersPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.reviewers().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState />
  if (!data.items.length) return <EmptyState message="No reviewers found." />

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Reviewer Intelligence</h1>
      <div className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900 text-slate-400">
            <tr>
              <th className="p-4">Reviewer ID</th>
              <th className="p-4">Reviews</th>
              <th className="p-4">Avg Rating</th>
              <th className="p-4">5-Star %</th>
              <th className="p-4">Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((r: any) => (
              <tr key={r.id} className="border-t border-slate-800 text-slate-300">
                <td className="p-4 font-mono">{r.reviewer_id}</td>
                <td className="p-4">{r.total_reviews}</td>
                <td className="p-4">{r.average_rating.toFixed(1)}</td>
                <td className="p-4">{Math.round(r.five_star_percentage * 100)}%</td>
                <td className="p-4">
                  <span className={r.suspicious_score > 0.7 ? 'text-rose-400' : 'text-emerald-400'}>
                    {Math.round(r.suspicious_score * 100)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
