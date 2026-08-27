export function StatCard({ label, value, accent = 'text-white' }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/80 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${accent}`}>{value}</p>
    </div>
  )
}

export function RiskBadge({ classification }: { classification: string }) {
  const colors: Record<string, string> = {
    Genuine: 'bg-emerald-500/20 text-emerald-300',
    Suspicious: 'bg-amber-500/20 text-amber-300',
    'Potentially Fake': 'bg-rose-500/20 text-rose-300',
  }
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-medium ${colors[classification] || 'bg-slate-700 text-slate-300'}`}>
      {classification}
    </span>
  )
}

export function RiskGauge({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = value < 0.4 ? 'text-emerald-400' : value < 0.7 ? 'text-amber-400' : 'text-rose-400'
  return (
    <div className="text-center">
      <div className={`text-5xl font-bold ${color}`}>{pct}%</div>
      <p className="mt-1 text-sm text-slate-400">Fraud Probability</p>
    </div>
  )
}

export function LoadingState() {
  return <div className="py-12 text-center text-slate-400">Loading...</div>
}

export function ErrorState({ message }: { message: string }) {
  return <div className="rounded-lg border border-rose-800 bg-rose-950/50 p-4 text-rose-300">{message}</div>
}

export function EmptyState({ message }: { message: string }) {
  return <div className="py-12 text-center text-slate-500">{message}</div>
}
