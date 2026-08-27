import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../services/api'
import { ErrorState, LoadingState, RiskBadge, RiskGauge } from '../components/ui'

export function ReviewDetailPage() {
  const { id } = useParams()
  const [review, setReview] = useState<any>(null)
  const [prediction, setPrediction] = useState<any>(null)
  const [similarities, setSimilarities] = useState<any[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    Promise.all([
      api.reviews().then((r: any) => r.items.find((i: any) => String(i.id) === id)),
      api.predictionForReview(+id).catch(() => null),
      api.similarities(+id).catch(() => [] as any[]),
    ]).then(([rev, pred, sims]) => {
      setReview(rev)
      setPrediction(pred)
      setSimilarities(sims as any[])
    }).catch((e) => setError(e.message))
  }, [id])

  if (error) return <ErrorState message={error} />
  if (!review) return <LoadingState />

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Review Investigation</h1>
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <p className="font-mono text-xs text-slate-500">{review.review_id}</p>
          <p className="mt-4 text-lg text-white">{review.review_text}</p>
          <p className="mt-4 text-sm text-slate-400">Rating: {review.rating}</p>
          <p className="text-sm text-slate-400">Date: {new Date(review.review_timestamp).toLocaleString()}</p>
        </div>
        {prediction && (
          <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
            <RiskGauge value={prediction.fraud_probability} />
            <div className="mt-4 flex justify-center"><RiskBadge classification={prediction.classification} /></div>
            <pre className="mt-4 whitespace-pre-wrap text-xs text-slate-300">{prediction.explanation}</pre>
          </div>
        )}
      </div>
      {similarities.length > 0 && (
        <div className="mt-6 rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">Similar Reviews</h2>
          {similarities.map((s) => (
            <div key={s.id} className="border-b border-slate-800 py-3 text-sm text-slate-300">
              Score: {Math.round(s.similarity_score * 100)}% | Type: {s.similarity_type}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
