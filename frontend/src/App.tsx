import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppProvider } from './context/AppContext';
import { ToastProvider } from './context/ToastContext';
import { ToastContainer } from './components/ui/Toast';
import { AppShell } from './components/layout/AppShell';
import { Skeleton } from './components/ui/SkeletonLoader';

// Lazy load pages for performance
const LandingPage        = lazy(() => import('./pages/LandingPage'));
const LoginPage          = lazy(() => import('./pages/LoginPage'));
const DashboardPage      = lazy(() => import('./pages/DashboardPage'));
const RepositoriesPage   = lazy(() => import('./pages/RepositoriesPage'));
const CommitAnalyzerPage = lazy(() => import('./pages/CommitAnalyzerPage'));
const CommitHistoryPage  = lazy(() => import('./pages/CommitHistoryPage'));
const CommitDetailPage   = lazy(() => import('./pages/CommitDetailPage'));
const AnalyticsPage      = lazy(() => import('./pages/AnalyticsPage'));
const ContributorsPage   = lazy(() => import('./pages/ContributorsPage'));
const RecommendationsPage = lazy(() => import('./pages/RecommendationsPage'));
const ActivityPage       = lazy(() => import('./pages/ActivityPage'));
const SettingsPage       = lazy(() => import('./pages/SettingsPage'));
const ModelPerfPage      = lazy(() => import('./pages/ModelPerformancePage'));
const DemoPage           = lazy(() => import('./pages/DemoPage'));

const PageFallback = () => (
  <div style={{ padding: 'var(--space-8)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
    <Skeleton width="40%" height={32} />
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 'var(--space-4)' }}>
      {[1,2,3,4].map(i => <Skeleton key={i} height={100} />)}
    </div>
    <Skeleton height={280} />
  </div>
);

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <PageFallback />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppShell>
      <Suspense fallback={<PageFallback />}>
        {children}
      </Suspense>
    </AppShell>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <AppProvider>
            {/* Animated background */}
            <div className="app-background" aria-hidden="true">
              <div className="bg-grid" />
              <div className="bg-gradient-1" />
              <div className="bg-gradient-2" />
              <div className="bg-gradient-3" />
            </div>

            <BrowserRouter>
              <Routes>
                {/* Public routes */}
                <Route path="/" element={
                  <Suspense fallback={<PageFallback />}>
                    <LandingPage />
                  </Suspense>
                } />
                <Route path="/login" element={
                  <Suspense fallback={<PageFallback />}>
                    <LoginPage />
                  </Suspense>
                } />
                <Route path="/demo" element={
                  <Suspense fallback={<PageFallback />}>
                    <DemoPage />
                  </Suspense>
                } />

                {/* Auth callback */}
                <Route path="/auth/callback" element={<AuthCallback />} />

                {/* Protected app routes */}
                <Route path="/dashboard" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><DashboardPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/repositories" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><RepositoriesPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/analyzer" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><CommitAnalyzerPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/history" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><CommitHistoryPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/commits/:hash" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><CommitDetailPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/analytics" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><AnalyticsPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/contributors" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><ContributorsPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/recommendations" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><RecommendationsPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/activity" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><ActivityPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/settings" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><SettingsPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />
                <Route path="/model-performance" element={
                  <ProtectedRoute>
                    <AuthenticatedLayout><ModelPerfPage /></AuthenticatedLayout>
                  </ProtectedRoute>
                } />

                {/* Catch-all */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>

            <ToastContainer />
          </AppProvider>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

// OAuth callback handler
function AuthCallback() {
  const { refreshUser } = useAuth();
  React.useEffect(() => {
    refreshUser().then(() => {
      window.location.href = '/dashboard';
    });
  }, []);
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', flexDirection: 'column', gap: 'var(--space-4)' }}>
      <div style={{ width: 40, height: 40, border: '3px solid var(--accent-primary)', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>Completing authentication...</p>
    </div>
  );
}
