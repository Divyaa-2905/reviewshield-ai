import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState } from '../components/ui'
import type { FeedbackDecision, FeedbackItem } from '../types/trust'

const decisionLabels: Record<FeedbackDecision, string> = {
  correct: 'Correct',
  incorrect: 'Incorrect',
  needs_correction: 'Needs correction',
}

export function FeedbackPage() {
  const [decision, setDecision] = useState('')
  const [items, setItems] = useState<FeedbackItem[]>([])
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.feedback(page, decision)
      .then((response) => {
        setItems(response.items)
        setPages(response.pages)
        setError('')
      })
      .catch((cause: Error) => setError(cause.message))
      .finally(() => setLoading(false))
  }, [page, decision])

  const exportCsv = async () => {
    setExporting(true)
    setError('')
    try {
      const blob = await api.exportFeedback(decision)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = 'verified-feedback.csv'
      anchor.click()
      URL.revokeObjectURL(url)
    } catch (cause) {
      setError((cause as Error).message)
    } finally {
      setExporting(false)
    }
  }

  if (loading && !items.length) return <LoadingState />

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Verified Feedback</h1>
          <p className="mt-1 text-sm text-slate-400">Analyst corrections linked to stored predictions.</p>
        </div>
        <div className="flex gap-3">
          <select
            value={decision}
            onChange={(event) => {
              setDecision(event.target.value)
              setPage(1)
              setLoading(true)
            }}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white"
            aria-label="Filter by feedback decision"
          >
            <option value="">All decisions</option>
            <option value="correct">Correct</option>
            <option value="incorrect">Incorrect</option>
            <option value="needs_correction">Needs correction</option>
          </select>
          <button
            onClick={exportCsv}
            disabled={exporting}
            className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-50"
          >
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
        </div>
      </div>
      {error && <div className="mb-5"><ErrorState message={error} /></div>}
      {loading ? <LoadingState /> : items.length === 0 ? <EmptyState message="No feedback matches this filter." /> : (
        <div className="overflow-x-auto rounded-xl border border-slate-700 bg-slate-900/80">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead className="border-b border-slate-700 text-xs uppercase text-slate-500">
              <tr>
                <th className="p-4">Review / product</th>
                <th className="p-4">Prediction</th>
                <th className="p-4">Decision</th>
                <th className="p-4">Analyst</th>
                <th className="p-4">Updated</th>
                <th className="p-4">Comment</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-b border-slate-800 text-slate-300 last:border-0">
                  <td className="p-4">
                    <Link to={`/reviews/${item.review_db_id}`} className="font-medium text-sky-300 hover:text-sky-200">
                      {item.review_id}
                    </Link>
                    <p className="mt-1 text-xs text-slate-500">{item.product_name} · {item.product_id}</p>
                  </td>
                  <td className="p-4">{item.prediction_classification}</td>
                  <td className="p-4">{decisionLabels[item.decision]}</td>
                  <td className="p-4">{item.analyst_username}</td>
                  <td className="p-4">{new Date(item.updated_at).toLocaleString()}</td>
                  <td className="max-w-sm whitespace-pre-wrap p-4 text-slate-400">{item.comment || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between border-t border-slate-800 p-4 text-sm text-slate-400">
            <span>Page {page} of {pages}</span>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setPage((current) => Math.max(1, current - 1))
                  setLoading(true)
                }}
                disabled={page <= 1}
                className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40"
              >
                Previous
              </button>
              <button
                onClick={() => {
                  setPage((current) => Math.min(pages, current + 1))
                  setLoading(true)
                }}
                disabled={page >= pages}
                className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
