import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState, RiskBadge } from '../components/ui'

export function ReviewsPage() {
  const [data, setData] = useState<any>(null)
  const [predictions, setPredictions] = useState<Record<number, any>>({})
  const [error, setError] = useState('')

  useEffect(() => {
    api.reviews()
      .then(async (res: any) => {
        setData(res)
        const preds: Record<number, any> = {}
        for (const review of res.items) {
          try {
            preds[review.id] = await api.predictionForReview(review.id)
          } catch { /* no prediction */ }
        }
        setPredictions(preds)
      })
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState />
  if (!data.items.length) return <EmptyState message="No reviews found. Run seed_demo_data.py first." />

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Review Investigation</h1>
      <div className="space-y-4">
        {data.items.map((review: any) => {
          const pred = predictions[review.id]
          return (
            <div key={review.id} className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-mono text-xs text-slate-500">{review.review_id}</p>
                  <p className="mt-2 text-white">{review.review_text}</p>
                  <p className="mt-2 text-sm text-slate-400">Rating: {review.rating} | {new Date(review.review_timestamp).toLocaleDateString()}</p>
                </div>
                {pred && <RiskBadge classification={pred.classification} />}
              </div>
              {pred && (
                <div className="mt-4 flex items-center gap-4">
                  <span className="text-sm text-slate-400">Risk: {Math.round(pred.fraud_probability * 100)}%</span>
                  <Link to={`/reviews/${review.id}`} className="text-sm text-sky-400 hover:underline">View details</Link>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
