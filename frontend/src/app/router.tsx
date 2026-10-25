import {
  Navigate,
  Outlet,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Loader from '../components/ui/Loader'

import LoginPage from '../pages/LoginPage'
import RegisterPage from '../pages/PegisterPage'
import DashboardPage from '../pages/DashboardPage'
import ProductsPage from '../pages/ProductsPage'
import ProductDetailsPage from '../pages/ProductDetailsPage'
import ApplicationCreatePage from '../pages/ApplicationCreatePage'
import ApplicationsPage from '../pages/ApplicationsPage'
import ApplicationDetailsPage from '../pages/ApplicationDetailsPage'
import ComparisonPage from '../pages/ComparisonPage'
import NotFoundPage from '../pages/NotFoundPage'
import BusinessProfilePage from '../pages/BusinessProfilePage'
import RecommendationsPage from '../pages/RecommendationsPage'
import StaffApplicationsPage from '../pages/StaffApplicationPage'

function ProtectedRoute() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) return <Loader text="Проверяем авторизацию..." />
  if (!user) {
    return (
      <Navigate to="/login" replace state={{ from: location.pathname }} />
    )
  }
  return <Outlet />
}

function StaffRoute() {
  const { user, loading, isStaff } = useAuth()
  const location = useLocation()

  if (loading) return <Loader text="Проверяем авторизацию..." />
  if (!user) {
    return (
      <Navigate to="/login" replace state={{ from: location.pathname }} />
    )
  }
  if (!isStaff) return <Navigate to="/dashboard" replace />
  return <Outlet />
}

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/products/:id" element={<ProductDetailsPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/applications/new" element={<ApplicationCreatePage />} />
        <Route path="/applications/:id" element={<ApplicationDetailsPage />} />
        <Route path="/compare" element={<ComparisonPage />} />
        <Route path="/business-profile" element={<BusinessProfilePage />} />
        <Route path="/recommendations" element={<RecommendationsPage />} />
      </Route>

      <Route element={<StaffRoute />}>
        <Route path="/staff/applications" element={<StaffApplicationsPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}