import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import { DashboardLayout } from './layouts/DashboardLayout'
import { LoginPage } from './pages/LoginPage'
import { OverviewPage } from './pages/OverviewPage'
import { AnalyzerPage } from './pages/AnalyzerPage'
import { BatchAnalysisPage } from './pages/BatchAnalysisPage'
import { ReviewsPage } from './pages/ReviewsPage'
import { ReviewDetailPage } from './pages/ReviewDetailPage'
import { ReviewersPage } from './pages/ReviewersPage'
import { ProductsPage } from './pages/ProductsPage'
import { ProductTrustPage } from './pages/ProductTrustPage'
import { FeedbackPage } from './pages/FeedbackPage'
import { ClustersPage } from './pages/ClustersPage'
import { CampaignsPage } from './pages/CampaignsPage'
import { GraphPage } from './pages/GraphPage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { SettingsPage } from './pages/SettingsPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-400">Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/analyzer" element={<AnalyzerPage />} />
        <Route path="/batch-analysis" element={<BatchAnalysisPage />} />
        <Route path="/reviews" element={<ReviewsPage />} />
        <Route path="/reviews/:id" element={<ReviewDetailPage />} />
        <Route path="/reviewers" element={<ReviewersPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/products/:id" element={<ProductTrustPage />} />
        <Route path="/feedback" element={<FeedbackPage />} />
        <Route path="/clusters" element={<ClustersPage />} />
        <Route path="/campaigns" element={<CampaignsPage />} />
        <Route path="/graph" element={<GraphPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
