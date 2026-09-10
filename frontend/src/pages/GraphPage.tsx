import { useEffect, useMemo, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState } from '../components/ui'

type GraphNode = {
  id: string
  label: string
  type: string
  risk_score: number
}

type GraphEdge = {
  source: string
  target: string
  rating?: number | null
  review_id?: string | null
}

type GraphData = {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export function GraphPage() {
  const [data, setData] = useState<GraphData | null>(null)
  const [selected, setSelected] = useState<GraphNode | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.graph()
      .then((payload) => setData(payload as GraphData))
      .catch((e: Error) => setError(e.message))
  }, [])

  const elements = useMemo(() => {
    if (!data) return []
    return [
      ...data.nodes.map((node) => ({
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          risk_score: node.risk_score,
        },
      })),
      ...data.edges.map((edge, index) => ({
        data: {
          id: `${edge.source}-${edge.target}-${index}`,
          source: edge.source,
          target: edge.target,
          rating: edge.rating ?? undefined,
          review_id: edge.review_id ?? undefined,
        },
      })),
    ]
  }, [data])

  useEffect(() => {
    if (!containerRef.current || !data?.nodes.length) return

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      minZoom: 0.3,
      maxZoom: 2.5,
      wheelSensitivity: 0.3,
      layout: {
        name: 'cose',
        animate: false,
        padding: 24,
        nodeRepulsion: 8000,
        idealEdgeLength: 90,
      },
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            color: '#e2e8f0',
            'font-size': 8,
            'text-valign': 'bottom',
            'text-margin-y': 6,
            width: 18,
            height: 18,
            'border-width': 2,
            'border-color': '#0f172a',
          },
        },
        {
          selector: 'node[type = "reviewer"]',
          style: {
            'background-color': '#38bdf8',
            shape: 'ellipse',
          },
        },
        {
          selector: 'node[type = "product"]',
          style: {
            'background-color': '#34d399',
            shape: 'round-rectangle',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 1.4,
            'line-color': '#334155',
            'curve-style': 'bezier',
            opacity: 0.8,
          },
        },
        {
          selector: '.selected',
          style: {
            'border-color': '#fbbf24',
            'border-width': 3,
          },
        },
        {
          selector: '.neighbor',
          style: {
            'line-color': '#f59e0b',
            'background-color': '#f59e0b',
          },
        },
      ],
    })

    cy.on('tap', 'node', (event) => {
      const node = event.target
      const payload: GraphNode = {
        id: String(node.id()),
        label: String(node.data('label') ?? node.id()),
        type: String(node.data('type') ?? 'unknown'),
        risk_score: Number(node.data('risk_score') ?? 0),
      }
      setSelected(payload)
      cy.elements().removeClass('selected neighbor')
      node.addClass('selected')
      node.neighborhood().addClass('neighbor')
    })

    cy.on('tap', (event) => {
      if (event.target === cy) {
        cy.elements().removeClass('selected neighbor')
        setSelected(null)
      }
    })

    return () => {
      cy.destroy()
    }
  }, [data, elements])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState />
  if (!data.nodes.length) return <EmptyState message="No graph data. Seed demo or public dataset first." />

  const connections = selected
    ? data.edges.filter((edge) => edge.source === selected.id || edge.target === selected.id)
    : []

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-white">Graph Explorer</h1>
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-700 bg-slate-900/80 p-4">
          <div className="mb-3 flex items-center justify-between text-sm text-slate-400">
            <p>{data.nodes.length} nodes, {data.edges.length} edges</p>
            <div className="flex gap-4">
              <span className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-sky-400" /> Reviewer</span>
              <span className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-400" /> Product</span>
            </div>
          </div>
          <div ref={containerRef} className="h-[560px] w-full overflow-hidden rounded-lg bg-slate-950" />
        </div>
        <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <h3 className="font-semibold text-white">Node Details</h3>
          {selected ? (
            <div className="mt-4 space-y-2 text-sm text-slate-300">
              <p>ID: {selected.id}</p>
              <p>Type: {selected.type}</p>
              <p>Label: {selected.label}</p>
              <p>Risk: {Math.round(selected.risk_score * 100)}%</p>
              <p>Connections: {connections.length}</p>
              <ul className="mt-3 max-h-64 space-y-1 overflow-y-auto text-xs text-slate-400">
                {connections.map((edge, index) => (
                  <li key={`${edge.source}-${edge.target}-${index}`}>
                    {edge.source === selected.id ? edge.target : edge.source}
                    {edge.rating != null ? ` · ${edge.rating}★` : ''}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="mt-4 text-sm text-slate-500">Click a node to inspect neighbors. Scroll to zoom, drag to pan.</p>
          )}
        </div>
      </div>
    </div>
  )
}
