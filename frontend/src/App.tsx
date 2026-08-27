import { HealthStatus } from './components/HealthStatus'

function App() {
  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-sky-400">
              Review Fraud Intelligence
            </p>
            <h1 className="text-2xl font-bold text-white">ReviewShield AI</h1>
          </div>
          <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
            Phase 1 — Foundation
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <section className="mb-8">
          <h2 className="mb-2 text-xl font-semibold text-white">
            AI-powered review fraud intelligence
          </h2>
          <p className="max-w-2xl text-slate-400">
            Multi-modal evidence platform combining language, behaviour, timing, similarity,
            and network analysis for evidence-based fraud risk assessment.
          </p>
        </section>

        <div className="grid gap-6 lg:grid-cols-2">
          <HealthStatus />

          <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-6 shadow-lg">
            <h2 className="mb-4 text-lg font-semibold text-white">Planned Capabilities</h2>
            <ul className="grid gap-2 text-sm text-slate-300">
              <li>NLP and transformer embeddings</li>
              <li>Reviewer behaviour profiling</li>
              <li>Temporal pattern detection</li>
              <li>Semantic similarity analysis</li>
              <li>Graph-based coordination detection</li>
              <li>Multimodal fraud scoring with explainability</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
