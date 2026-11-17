import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../services/api'
import { ErrorState, LoadingState, RiskBadge, RiskGauge } from '../components/ui'
import { useAuth } from '../contexts/AuthContext'
import type { FeedbackDecision, FeedbackItem } from '../types/trust'

export function ReviewDetailPage() {
  const { id } = useParams()
  const [review, setReview] = useState<any>(null)
  const [prediction, setPrediction] = useState<any>(null)
  const [feedback, setFeedback] = useState<FeedbackItem | null>(null)
  const [decision, setDecision] = useState<FeedbackDecision>('correct')
  const [comment, setComment] = useState('')
  const [savingFeedback, setSavingFeedback] = useState(false)
  const [similarities, setSimilarities] = useState<any[]>([])
  const [error, setError] = useState('')
  const { user } = useAuth()
  const canReview = user?.role === 'admin' || user?.role === 'analyst'

  useEffect(() => {
    if (!id) return
    Promise.all([
      api.reviews().then((r: any) => r.items.find((i: any) => String(i.id) === id)),
      api.predictionForReview(+id).catch(() => null),
      api.similarities(+id).catch(() => [] as any[]),
    ]).then(async ([rev, pred, sims]) => {
      setReview(rev)
      setPrediction(pred)
      setSimilarities(sims as any[])
      if (pred) {
        const existingFeedback = await api.feedbackForPrediction(pred.id)
        setFeedback(existingFeedback)
        if (existingFeedback) {
          setDecision(existingFeedback.decision)
          setComment(existingFeedback.comment || '')
        }
      }
    }).catch((e) => setError(e.message))
  }, [id])

  const saveFeedback = async () => {
    if (!prediction) return
    setSavingFeedback(true)
    setError('')
    try {
      const saved = await api.savePredictionFeedback(prediction.id, { decision, comment: comment || null })
      setFeedback(saved)
    } catch (cause) {
      setError((cause as Error).message)
    } finally {
      setSavingFeedback(false)
    }
  }

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
      {prediction && canReview && (
        <section className="mt-6 rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h2 className="text-lg font-semibold text-white">Analyst feedback</h2>
          <p className="mt-1 text-sm text-slate-400">
            Feedback is saved against this stored prediction and records the analyst and update time.
          </p>
          <div className="mt-4 grid gap-4 md:grid-cols-[220px_1fr_auto]">
            <select
              value={decision}
              onChange={(event) => setDecision(event.target.value as FeedbackDecision)}
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
              aria-label="Prediction feedback decision"
            >
              <option value="correct">Correct</option>
              <option value="incorrect">Incorrect</option>
              <option value="needs_correction">Needs correction</option>
            </select>
            <textarea
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              maxLength={2000}
              rows={2}
              placeholder="Optional correction note"
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white"
            />
            <button
              onClick={saveFeedback}
              disabled={savingFeedback}
              className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-50"
            >
              {savingFeedback ? 'Saving...' : feedback ? 'Update feedback' : 'Save feedback'}
            </button>
          </div>
          {feedback && (
            <p className="mt-3 text-xs text-slate-500">
              Last updated by {feedback.analyst_username} at {new Date(feedback.updated_at).toLocaleString()}.
            </p>
          )}
        </section>
      )}
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
