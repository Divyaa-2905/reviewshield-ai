import { useState } from 'react'
import { api } from '../services/api'
import { ErrorState, RiskBadge, RiskGauge } from '../components/ui'

export function AnalyzerPage() {
  const [text, setText] = useState('')
  const [rating, setRating] = useState(5)
  const [reviewerId, setReviewerId] = useState('')
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const analyze = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.analyze({
        review_text: text,
        rating,
        reviewer_id: reviewerId || undefined,
        review_timestamp: new Date().toISOString(),
      })
      setResult(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Review Analyzer</h1>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter review text..."
            className="h-32 w-full rounded-lg border border-slate-600 bg-slate-800 p-3 text-white"
          />
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-sm text-slate-400">Rating</label>
              <input type="number" min={1} max={5} value={rating} onChange={(e) => setRating(+e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-800 p-2 text-white" />
            </div>
            <div>
              <label className="text-sm text-slate-400">Reviewer ID (optional)</label>
              <input value={reviewerId} onChange={(e) => setReviewerId(e.target.value)}
                placeholder="rev-suspicious-01"
                className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-800 p-2 text-white" />
            </div>
          </div>
          <button onClick={analyze} disabled={loading || !text}
            className="mt-4 rounded-lg bg-sky-600 px-6 py-2 font-medium text-white hover:bg-sky-500 disabled:opacity-50">
            {loading ? 'Analyzing...' : 'Analyze Review'}
          </button>
          {error && <div className="mt-4"><ErrorState message={error} /></div>}
        </div>

        {result && (
          <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
            {result.persisted === false && (
              <p className="mb-3 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs text-slate-400">
                Live analysis only — this result was not written to the database.
              </p>
            )}
            <RiskGauge value={result.fraud_probability} />
            <div className="mt-4 flex justify-center"><RiskBadge classification={result.classification} /></div>
            {!result.history_available && (
              <p className="mt-3 text-center text-xs text-amber-300">
                Reviewer history missing. Behavior and temporal weights were redistributed.
              </p>
            )}
            <div className="mt-6 grid grid-cols-2 gap-3 text-sm">
              {[
                ['Text Risk', result.text_risk],
                ['Behavior Risk', result.behavior_risk],
                ['Temporal Risk', result.temporal_risk],
                ['Similarity Risk', result.similarity_risk],
                ['Graph Risk', result.graph_risk],
              ].map(([label, val]) => (
                <div key={label as string} className="rounded-lg bg-slate-800 p-3">
                  <p className="text-slate-400">{label}</p>
                  <p className="font-medium text-white">{Math.round((val as number) * 100)}%</p>
                </div>
              ))}
            </div>
            {result.weights_used && (
              <p className="mt-3 text-xs text-slate-500">
                Weights: {Object.entries(result.weights_used).map(([k, v]) => `${k} ${(Number(v) * 100).toFixed(0)}%`).join(' · ')}
              </p>
            )}
            {result.explanation && (
              <pre className="mt-4 whitespace-pre-wrap rounded-lg bg-slate-800 p-4 text-xs text-slate-300">{result.explanation}</pre>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
