import { NavLink, Outlet } from 'react-router-dom'
import {
  BarChart3, GitBranch, LayoutDashboard, LogOut, Search,
  Settings, Shield, Users, Package, Network,
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const nav = [
  { to: '/', icon: LayoutDashboard, label: 'Overview' },
  { to: '/analyzer', icon: Search, label: 'Analyzer' },
  { to: '/reviews', icon: Shield, label: 'Investigation' },
  { to: '/reviewers', icon: Users, label: 'Reviewers' },
  { to: '/products', icon: Package, label: 'Products' },
  { to: '/clusters', icon: GitBranch, label: 'Clusters' },
  { to: '/graph', icon: Network, label: 'Graph' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function DashboardLayout() {
  const { user, logout } = useAuth()

  return (
    <div className="flex min-h-screen bg-slate-950">
      <aside className="w-64 border-r border-slate-800 bg-slate-900 p-4">
        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-widest text-sky-400">ReviewShield AI</p>
          <h1 className="text-lg font-bold text-white">Fraud Intelligence</h1>
        </div>
        <nav className="space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
                  isActive ? 'bg-sky-600 text-white' : 'text-slate-300 hover:bg-slate-800'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto border-t border-slate-800 pt-4">
          <p className="text-xs text-slate-400">{user?.username} ({user?.role})</p>
          <button onClick={logout} className="mt-2 flex items-center gap-2 text-sm text-slate-400 hover:text-white">
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-8">
        <Outlet />
      </main>
    </div>
  )
}
