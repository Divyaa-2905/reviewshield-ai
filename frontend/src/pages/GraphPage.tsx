import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState } from '../components/ui'

export function GraphPage() {
  const [data, setData] = useState<any>(null)
  const [selected, setSelected] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.graph().then(setData).catch((e) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState />
  if (!data.nodes.length) return <EmptyState message="No graph data. Seed demo data first." />

  const reviewerNodes = data.nodes.filter((n: any) => n.type === 'reviewer')
  const productNodes = data.nodes.filter((n: any) => n.type === 'product')

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Graph Explorer</h1>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <p className="mb-4 text-sm text-slate-400">
            {data.nodes.length} nodes, {data.edges.length} edges
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="mb-2 text-sm font-medium text-sky-400">Reviewers ({reviewerNodes.length})</h3>
              <div className="max-h-64 space-y-1 overflow-y-auto">
                {reviewerNodes.map((n: any) => (
                  <button key={n.id} onClick={() => setSelected(n)}
                    className={`block w-full rounded px-2 py-1 text-left text-xs ${selected?.id === n.id ? 'bg-sky-600 text-white' : 'text-slate-400 hover:bg-slate-800'}`}>
                    {n.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <h3 className="mb-2 text-sm font-medium text-emerald-400">Products ({productNodes.length})</h3>
              <div className="max-h-64 space-y-1 overflow-y-auto">
                {productNodes.map((n: any) => (
                  <button key={n.id} onClick={() => setSelected(n)}
                    className={`block w-full rounded px-2 py-1 text-left text-xs ${selected?.id === n.id ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:bg-slate-800'}`}>
                    {n.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h3 className="font-semibold text-white">Node Details</h3>
          {selected ? (
            <div className="mt-4 text-sm text-slate-300">
              <p>ID: {selected.id}</p>
              <p>Type: {selected.type}</p>
              <p>Label: {selected.label}</p>
              <p className="mt-2">Connections: {data.edges.filter((e: any) => e.source === selected.id || e.target === selected.id).length}</p>
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-500">Select a node to inspect</p>
          )}
        </div>
      </div>
    </div>
  )
}
