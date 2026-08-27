import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { login } from '../services/api'

export function LoginPage() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setToken } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { access_token } = await login(username, password)
      setToken(access_token)
      navigate('/')
    } catch {
      setError('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <form onSubmit={handleLogin} className="w-full max-w-md rounded-xl border border-slate-700 bg-slate-900 p-8">
        <h1 className="text-2xl font-bold text-white">ReviewShield AI</h1>
        <p className="mt-1 text-sm text-slate-400">Sign in to the fraud intelligence platform</p>
        <div className="mt-6 space-y-4">
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username"
            className="w-full rounded-lg border border-slate-600 bg-slate-800 p-3 text-white" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password"
            className="w-full rounded-lg border border-slate-600 bg-slate-800 p-3 text-white" />
          {error && <p className="text-sm text-rose-400">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full rounded-lg bg-sky-600 py-3 font-medium text-white hover:bg-sky-500 disabled:opacity-50">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </div>
        <p className="mt-4 text-center text-xs text-slate-500">Demo: admin / admin123</p>
      </form>
    </div>
  )
}
