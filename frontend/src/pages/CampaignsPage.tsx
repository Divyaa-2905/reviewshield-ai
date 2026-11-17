import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { EmptyState, ErrorState, LoadingState } from '../components/ui'
import type { CampaignsResponse } from '../types/analytics'

function pct(value: number) {
  return `${Math.round(value * 100)}%`
}

export function CampaignsPage() {
  const [data, setData] = useState<CampaignsResponse | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.campaigns().then(setData).catch((e: Error) => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState />

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Coordinated Campaigns</h1>
          <p className="mt-1 text-sm text-slate-400">
            {data.total} candidate{data.total === 1 ? '' : 's'} · source: {data.data_source}
          </p>
        </div>
        <p className="max-w-2xl text-xs text-slate-500">
          Campaign scores are heuristic investigation signals combining reviewer-product connections,
          synchronized timing, and cross-reviewer text similarity. They are estimates, not proof of fraud.
        </p>
      </div>

      {data.campaigns.length === 0 ? (
        <EmptyState message="No connected groups with temporal or similarity evidence were detected." />
      ) : (
        <div className="space-y-4">
          {data.campaigns.map((campaign) => {
            const expanded = selectedId === campaign.campaign_id
            return (
              <section key={campaign.campaign_id} className="overflow-hidden rounded-xl border border-slate-700 bg-slate-900/80">
                <button
                  type="button"
                  aria-expanded={expanded}
                  onClick={() => setSelectedId(expanded ? null : campaign.campaign_id)}
                  className="flex w-full flex-wrap items-center justify-between gap-4 p-5 text-left hover:bg-slate-800/50"
                >
                  <div>
                    <h2 className="font-mono font-semibold text-white">{campaign.campaign_id}</h2>
                    <p className="mt-1 text-sm text-slate-400">
                      {campaign.reviewer_count} reviewers · {campaign.product_count} products · {campaign.review_count} reviews
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400">{expanded ? 'Hide investigation' : 'Investigate'}</span>
                    <span className={`text-lg font-bold ${campaign.risk_score >= 0.7 ? 'text-rose-400' : 'text-amber-400'}`}>
                      {pct(campaign.risk_score)} risk
                    </span>
                  </div>
                </button>

                <div className="border-t border-slate-800 px-5 pb-5">
                  <p className="pt-4 text-sm text-slate-300">{campaign.explanation}</p>
                  {expanded && (
                    <div className="mt-5 grid gap-5 xl:grid-cols-2">
                      <div className="space-y-4">
                        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
                          <h3 className="font-semibold text-white">Connected entities</h3>
                          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Reviewers</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {campaign.connected_entities.reviewers.map((reviewer) => (
                              <span key={reviewer} className="rounded bg-sky-950 px-2 py-1 text-xs text-sky-200">{reviewer}</span>
                            ))}
                          </div>
                          <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-500">Products</p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {campaign.connected_entities.products.map((product) => (
                              <span key={product} className="rounded bg-emerald-950 px-2 py-1 text-xs text-emerald-200">{product}</span>
                            ))}
                          </div>
                        </div>

                        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
                          <h3 className="font-semibold text-white">Temporal evidence</h3>
                          <p className="mt-2 text-sm text-slate-300">
                            {campaign.temporal_evidence.synchronized_pairs} synchronized review pairs ·{' '}
                            {campaign.temporal_evidence.burst_windows} 24-hour burst windows
                          </p>
                          {campaign.temporal_evidence.avg_interval_hours != null && (
                            <p className="mt-1 text-sm text-slate-400">
                              Average interval: {campaign.temporal_evidence.avg_interval_hours.toFixed(1)} hours
                            </p>
                          )}
                          {campaign.temporal_evidence.observations.map((observation) => (
                            <p key={observation} className="mt-2 text-xs text-amber-300">{observation}</p>
                          ))}
                          <p className="mt-3 text-xs text-slate-500">
                            Temporal signal: {pct(campaign.temporal_evidence.risk_score)}
                          </p>
                        </div>

                        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
                          <h3 className="font-semibold text-white">Graph evidence</h3>
                          <p className="mt-2 text-sm text-slate-300">
                            {campaign.graph_evidence.node_count} connected nodes · {campaign.graph_evidence.edge_count} links ·{' '}
                            {campaign.graph_evidence.similarity_link_count} similarity links between reviewers
                          </p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
                          <h3 className="font-semibold text-white">Review similarity evidence</h3>
                          <p className="mt-2 text-sm text-slate-300">
                            {campaign.similarity_evidence.pair_count} cross-reviewer pairs · average similarity{' '}
                            {pct(campaign.similarity_evidence.average_score)} · maximum{' '}
                            {pct(campaign.similarity_evidence.max_score)}
                          </p>
                          {campaign.similarity_evidence.pairs.length > 0 && (
                            <ul className="mt-3 space-y-2 text-xs text-slate-400">
                              {campaign.similarity_evidence.pairs.map((pair) => (
                                <li key={`${pair.review_a_id}-${pair.review_b_id}`} className="flex justify-between gap-3">
                                  <span>{pair.review_a_id} ↔ {pair.review_b_id}</span>
                                  <span>{pct(pair.similarity_score)}</span>
                                </li>
                              ))}
                            </ul>
                          )}
                        </div>

                        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
                          <h3 className="font-semibold text-white">Reviews in this group</h3>
                          <ul className="mt-3 max-h-80 space-y-2 overflow-y-auto">
                            {campaign.connected_entities.reviews.map((review) => (
                              <li key={review.review_id} className="rounded bg-slate-900 p-3 text-xs text-slate-300">
                                <div className="flex flex-wrap justify-between gap-2">
                                  <span className="font-mono text-sky-300">{review.review_id}</span>
                                  <span>{new Date(review.review_timestamp).toLocaleString()}</span>
                                </div>
                                <p className="mt-1 text-slate-400">
                                  {review.reviewer_id} → {review.product_id} · {review.rating}★
                                </p>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )
          })}
        </div>
      )}
    </div>
  )
}
