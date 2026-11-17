import { useEffect, useState } from 'react'
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../services/api'
import { ErrorState, LoadingState } from '../components/ui'
import type { ModelMetrics } from '../types/analytics'

function pct(value: number | null | undefined) {
  if (value == null || Number.isNaN(value)) return 'n/a'
  return `${Math.round(value * 100)}%`
}

function MetricCard({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-bold text-white">{value}</p>
      {note && <p className="mt-1 text-xs text-slate-500">{note}</p>}
    </div>
  )
}

export function AnalyticsPage() {
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.modelMetrics().then(setMetrics).catch((e: Error) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!metrics) return <LoadingState />

  const modalityData = Object.entries(metrics.modality_averages).map(([name, value]) => ({
    name: name.replaceAll('_', ' '),
    value: Math.round(value * 100),
  }))
  const matrix = metrics.confusion_matrix

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Model Performance</h1>
      <div className="mb-6 rounded-xl border border-sky-900 bg-sky-950/40 p-4 text-sm text-sky-200">
        <p className="font-semibold">
          Evaluation source: {metrics.data_source}
        </p>
        <p className="mt-1 text-sky-100/80">{metrics.evaluation_protocol}</p>
        <p className="mt-1 text-sky-100/80">{metrics.evaluation_note}</p>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MetricCard label="Accuracy" value={pct(metrics.accuracy)} />
        <MetricCard label="Precision" value={pct(metrics.precision)} />
        <MetricCard label="Recall" value={pct(metrics.recall)} />
        <MetricCard label="F1-score" value={pct(metrics.f1)} />
        <MetricCard label="ROC AUC" value={pct(metrics.roc_auc)} />
        <MetricCard label="PR AUC" value={pct(metrics.pr_auc)} />
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <MetricCard label="Labeled test reviews" value={String(metrics.labeled_reviews)} />
        <MetricCard
          label="Held-out reviews scored"
          value={String(metrics.total_predictions)}
          note={`Test window: ${metrics.test_reviews} reviews · threshold ${metrics.threshold}`}
        />
        <MetricCard
          label="Earlier reference reviews"
          value={String(metrics.training_reviews)}
          note={`${metrics.total_reviews} stored reviews total`}
        />
      </div>

      <div className="mb-6 rounded-xl border border-slate-700 bg-slate-900/80 p-6">
        <h2 className="mb-1 text-lg font-semibold text-white">Confusion Matrix</h2>
        <p className="mb-4 text-xs text-slate-500">
          Binary fake-vs-genuine results at threshold {metrics.threshold}. Rows are predicted; columns are actual.
        </p>
        {matrix ? (
          <div className="overflow-x-auto">
            <table className="w-full max-w-xl border-collapse text-left text-sm">
              <thead>
                <tr className="text-slate-400">
                  <th className="p-3 font-medium">Predicted / Actual</th>
                  <th className="p-3 font-medium">Genuine</th>
                  <th className="p-3 font-medium">Fake</th>
                </tr>
              </thead>
              <tbody className="text-white">
                <tr className="border-t border-slate-700">
                  <th className="p-3 font-medium text-slate-300">Genuine</th>
                  <td className="p-3">{matrix.true_negative} (TN)</td>
                  <td className="p-3">{matrix.false_negative} (FN)</td>
                </tr>
                <tr className="border-t border-slate-700">
                  <th className="p-3 font-medium text-slate-300">Fake</th>
                  <td className="p-3">{matrix.false_positive} (FP)</td>
                  <td className="p-3">{matrix.true_positive} (TP)</td>
                </tr>
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-amber-300">
            No labeled reviews are available in the held-out period, so performance metrics are not reported.
          </p>
        )}
      </div>

      {modalityData.length > 0 && (
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">Held-out Modality Risk Averages</h2>
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
