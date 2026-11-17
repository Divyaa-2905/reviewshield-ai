import { useState } from 'react'
import { api } from '../services/api'
import { ErrorState, RiskBadge } from '../components/ui'
import type {
  BatchAnalysisResponse,
  BatchValidationResponse,
  BatchValidationRow,
} from '../types/batch'

function messageOf(error: unknown) {
  return error instanceof Error ? error.message : 'The request failed.'
}

function percent(value: number) {
  return `${Math.round(value * 100)}%`
}

export function BatchAnalysisPage() {
  const [file, setFile] = useState<File | null>(null)
  const [validation, setValidation] = useState<BatchValidationResponse | null>(null)
  const [analysis, setAnalysis] = useState<BatchAnalysisResponse | null>(null)
  const [error, setError] = useState('')
  const [exportError, setExportError] = useState('')
  const [validating, setValidating] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [exporting, setExporting] = useState(false)

  const upload = async () => {
    if (!file) return
    setValidating(true)
    setError('')
    setExportError('')
    setValidation(null)
    setAnalysis(null)
    try {
      setValidation(await api.validateCsv(file))
    } catch (requestError) {
      setError(messageOf(requestError))
    } finally {
      setValidating(false)
    }
  }

  const analyze = async () => {
    if (!validation) return
    const validRows: BatchValidationRow[] = validation.rows.filter(
      (row) => row.errors.length === 0 && row.rating !== null,
    )
    if (validRows.length === 0) return

    setAnalyzing(true)
    setError('')
    setAnalysis(null)
    try {
      setAnalysis(await api.analyzeBatch(validRows))
    } catch (requestError) {
      setError(messageOf(requestError))
    } finally {
      setAnalyzing(false)
    }
  }

  const exportResults = async () => {
    if (!analysis) return
    setExporting(true)
    setExportError('')
    try {
      const blob = await api.exportBatch(analysis.results)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'review-analysis-results.csv'
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (requestError) {
      setExportError(messageOf(requestError))
    } finally {
      setExporting(false)
    }
  }

  const onFileSelected = (selected: File | null) => {
    setFile(selected)
    setValidation(null)
    setAnalysis(null)
    setError('')
    setExportError('')
  }

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold text-white">Batch CSV Analysis</h1>
      <p className="mb-6 text-sm text-slate-400">
        Upload review rows for in-memory risk scoring. Results are estimates, not proof of fraud, and are not saved to the database.
      </p>

      <section className="rounded-xl border border-slate-700 bg-slate-900/80 p-6">
        <div className="grid gap-5 lg:grid-cols-[1fr_auto] lg:items-end">
          <div>
            <label htmlFor="review-csv" className="mb-2 block text-sm font-medium text-slate-200">
              Review CSV
            </label>
            <input
              id="review-csv"
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => onFileSelected(event.target.files?.[0] ?? null)}
              className="block w-full rounded-lg border border-slate-600 bg-slate-800 p-3 text-sm text-slate-300 file:mr-4 file:rounded-md file:border-0 file:bg-sky-700 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
            />
            <p className="mt-2 text-xs text-slate-500">
              Required columns: <code>review_text</code>, <code>rating</code>. Optional: <code>reviewer_id</code>, <code>review_id</code>, <code>review_timestamp</code>. Up to 500 rows and 5 MB.
            </p>
          </div>
          <button
            type="button"
            onClick={upload}
            disabled={!file || validating}
            className="rounded-lg bg-sky-600 px-5 py-3 text-sm font-medium text-white hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {validating ? 'Validating CSV...' : 'Upload and Validate'}
          </button>
        </div>
        {error && <div className="mt-4"><ErrorState message={error} /></div>}
      </section>

      {validation && (
        <section className="mt-6 rounded-xl border border-slate-700 bg-slate-900/80 p-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-white">CSV preview</h2>
              <p className="text-sm text-slate-400">
                {validation.valid_rows} valid · {validation.invalid_rows} invalid · {validation.total_rows} total rows
              </p>
            </div>
            <button
              type="button"
              onClick={analyze}
              disabled={validation.valid_rows === 0 || analyzing}
              className="rounded-lg bg-emerald-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {analyzing ? 'Analyzing valid rows...' : `Analyze ${validation.valid_rows} valid rows`}
            </button>
          </div>

          <div className="max-h-[28rem] overflow-auto rounded-lg border border-slate-700">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="sticky top-0 bg-slate-800 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-3 py-3">CSV row</th>
                  <th className="px-3 py-3">Review</th>
                  <th className="px-3 py-3">Rating</th>
                  <th className="px-3 py-3">Reviewer ID</th>
                  <th className="px-3 py-3">Validation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {validation.rows.map((row) => (
                  <tr key={row.row_number} className="align-top">
                    <td className="whitespace-nowrap px-3 py-3 text-slate-400">{row.row_number}</td>
                    <td className="max-w-xl px-3 py-3 text-slate-200">
                      <span className="line-clamp-2">{row.review_text || '—'}</span>
                    </td>
                    <td className="px-3 py-3 text-slate-300">{row.rating ?? '—'}</td>
                    <td className="px-3 py-3 text-slate-400">{row.reviewer_id || '—'}</td>
                    <td className="px-3 py-3">
                      {row.errors.length ? (
                        <ul className="list-inside list-disc text-xs text-rose-300">
                          {row.errors.map((rowError) => <li key={rowError}>{rowError}</li>)}
                        </ul>
                      ) : (
                        <span className="text-xs text-emerald-300">Valid</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {analysis && (
        <>
          <section className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
              <p className="text-sm text-slate-400">Analyzed reviews</p>
              <p className="mt-2 text-3xl font-bold text-white">{analysis.total_rows}</p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
              <p className="text-sm text-slate-400">Average fraud probability</p>
              <p className="mt-2 text-3xl font-bold text-amber-300">
                {percent(analysis.statistics.average_fraud_probability)}
              </p>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
              <p className="text-sm text-slate-400">High risk (70%+)</p>
              <p className="mt-2 text-3xl font-bold text-rose-300">{analysis.statistics.high_risk_count}</p>
            </div>
          </section>

          <section className="mt-6 rounded-xl border border-slate-700 bg-slate-900/80 p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-white">Analysis results</h2>
                <p className="text-sm text-slate-400">
                  {Object.entries(analysis.statistics.classification_counts)
                    .map(([name, count]) => `${name}: ${count}`)
                    .join(' · ')}
                </p>
              </div>
              <button
                type="button"
                onClick={exportResults}
                disabled={exporting}
                className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800 disabled:opacity-50"
              >
                {exporting ? 'Preparing CSV...' : 'Export results CSV'}
              </button>
            </div>
            {exportError && <div className="mb-4"><ErrorState message={exportError} /></div>}
            <div className="max-h-[34rem] overflow-auto rounded-lg border border-slate-700">
              <table className="w-full min-w-[1000px] text-left text-sm">
                <thead className="sticky top-0 bg-slate-800 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="px-3 py-3">CSV row</th>
                    <th className="px-3 py-3">Review</th>
                    <th className="px-3 py-3">Risk score</th>
                    <th className="px-3 py-3">Classification</th>
                    <th className="px-3 py-3">Text</th>
                    <th className="px-3 py-3">Behavior</th>
                    <th className="px-3 py-3">Temporal</th>
                    <th className="px-3 py-3">Similarity</th>
                    <th className="px-3 py-3">Graph</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {analysis.results.map((result) => (
                    <tr key={result.row_number} className="align-top">
                      <td className="px-3 py-3 text-slate-400">{result.row_number}</td>
                      <td className="max-w-lg px-3 py-3 text-slate-200">
                        <span className="line-clamp-2">{result.review_text}</span>
                      </td>
                      <td className="px-3 py-3 font-semibold text-white">{percent(result.fraud_probability)}</td>
                      <td className="px-3 py-3"><RiskBadge classification={result.classification} /></td>
                      {[result.text_risk, result.behavior_risk, result.temporal_risk, result.similarity_risk, result.graph_risk]
                        .map((score, index) => (
                          <td key={index} className="px-3 py-3 text-slate-300">{percent(score)}</td>
                        ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  )
}
