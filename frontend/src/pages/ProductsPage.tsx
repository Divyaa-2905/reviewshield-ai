import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState } from '../components/ui'

export function ProductsPage() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.products().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState />
  if (!data.items.length) return <EmptyState message="No products found." />

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Product Intelligence</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.items.map((p: any) => (
          <Link
            key={p.id}
            to={`/products/${encodeURIComponent(p.product_id)}`}
            className="rounded-xl border border-slate-700 bg-slate-900/80 p-5 transition hover:border-sky-600"
          >
            <h3 className="font-semibold text-white">{p.name}</h3>
            <p className="mt-1 text-sm text-slate-400">{p.category}</p>
            <p className="mt-2 font-mono text-xs text-slate-500">{p.product_id}</p>
            {p.seller && <p className="mt-1 text-xs text-slate-500">Seller: {p.seller}</p>}
            <p className="mt-4 text-sm font-medium text-sky-300">Open trust investigation →</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
