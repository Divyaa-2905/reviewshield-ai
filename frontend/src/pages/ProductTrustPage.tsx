import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api } from '../services/api'
import { ErrorState, LoadingState } from '../components/ui'
import type { ProductTrust } from '../types/trust'

interface Product {
  product_id: string
  name: string
  category: string
  seller: string | null
}

export function ProductTrustPage() {
  const { id = '' } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [analysis, setAnalysis] = useState<ProductTrust | null>(null)
  const [error, setError] = useState('')
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    Promise.all([api.product(id), api.productTrust(id)])
      .then(([productData, trustData]) => {
        setProduct(productData as Product)
        setAnalysis(trustData)
      })
      .catch((cause: Error) => setError(cause.message))
  }, [id])

  const downloadReport = async () => {
    setDownloading(true)
    setError('')
    try {
      const blob = await api.productReport(id)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `product-investigation-${id}.pdf`
      anchor.click()
      URL.revokeObjectURL(url)
    } catch (cause) {
      setError((cause as Error).message)
    } finally {
      setDownloading(false)
    }
  }

  if (error && !analysis) return <ErrorState message={error} />
  if (!product || !analysis) return <LoadingState />

  const chartData = Object.entries(analysis.rating_distribution).map(([rating, count]) => ({
    rating: `${rating} star`,
    reviews: count,
  }))

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="font-mono text-xs text-slate-500">{product.product_id}</p>
          <h1 className="mt-1 text-2xl font-bold text-white">{product.name}</h1>
          <p className="mt-1 text-sm text-slate-400">
            {product.category}{product.seller ? ` · Seller: ${product.seller}` : ''}
          </p>
        </div>
        <button
          onClick={downloadReport}
          disabled={downloading}
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-50"
        >
          {downloading ? 'Preparing report...' : 'Download PDF report'}
        </button>
      </div>
      {error && <div className="mb-5"><ErrorState message={error} /></div>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Trust score" value={analysis.trust_score === null ? 'N/A' : `${analysis.trust_score.toFixed(1)} / 100`} />
        <Metric label="Risk score" value={analysis.risk_score === null ? 'N/A' : `${analysis.risk_score.toFixed(1)} / 100`} />
        <Metric label="Stored reviews" value={analysis.review_count} />
        <Metric label="Prediction coverage" value={`${analysis.prediction_coverage.toFixed(1)}%`} />
      </div>
      <p className="mt-4 rounded-lg border border-amber-900/70 bg-amber-950/30 p-4 text-sm text-amber-200">
        Scores are heuristic estimates, not proof of fraud. Unscored reviews are not treated as genuine.
      </p>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h2 className="mb-4 text-lg font-semibold text-white">Evidence indicators</h2>
          {analysis.indicators.map((indicator) => (
            <article key={indicator.key} className="border-b border-slate-800 py-4 last:border-0">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="font-medium text-slate-100">{indicator.label}</h3>
                <span className="text-sm text-sky-300">
                  {indicator.value === null ? 'Unavailable' : `${indicator.value.toFixed(1)}% observed`}
                  {' · '}{indicator.weight.toFixed(1)}% score weight
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-400">{indicator.explanation}</p>
              <p className="mt-1 text-xs text-slate-500">
                Indicator risk: {indicator.risk_score === null ? 'N/A' : `${indicator.risk_score.toFixed(1)} / 100`}
              </p>
            </article>
          ))}
          <p className="mt-4 text-xs leading-5 text-slate-500">{analysis.score_explanation}</p>
        </section>
        <section className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h2 className="mb-1 text-lg font-semibold text-white">Rating distribution</h2>
          <p className="mb-4 text-sm text-slate-400">
            Average: {analysis.average_rating === null ? 'N/A' : `${analysis.average_rating.toFixed(2)} / 5`}
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                <XAxis dataKey="rating" stroke="#94a3b8" />
                <YAxis allowDecimals={false} stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="reviews" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-3 text-center text-sm">
            <div><p className="text-slate-500">Suspicious</p><p className="mt-1 font-semibold text-amber-300">{analysis.suspicious_percentage === null ? 'N/A' : `${analysis.suspicious_percentage.toFixed(1)}%`}</p></div>
            <div><p className="text-slate-500">Campaigns</p><p className="mt-1 font-semibold text-white">{analysis.campaign_count}</p></div>
            <div><p className="text-slate-500">Campaign reviews</p><p className="mt-1 font-semibold text-white">{analysis.campaign_review_count}</p></div>
          </div>
        </section>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-2xl font-bold text-white">{value}</p>
    </div>
  )
}
