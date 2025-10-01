import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from "@/components/theme-provider"
import { AuthProvider } from "@/components/auth-provider"
import { TrendAnalyzer } from "@/components/trend-analyzer"
import { TechFeaturesShowcase } from "@/components/tech-features-showcase"
import { AdminLayout } from "@/components/admin/AdminLayout"
import { AdminLogin } from "@/components/admin/AdminLogin"
import { AdminDashboard } from "@/components/admin/AdminDashboard"
import { UserManagement } from "@/components/admin/UserManagement"
import { SubscriptionManagement } from "@/components/admin/SubscriptionManagement"
import { SystemMonitoring } from "@/components/admin/SystemMonitoring"
import { PaymentSuccess } from "@/components/payment-success" // Add payment success page import
import PricingPage from "@/components/pricing-page"
import UserCenter from "@/components/user-center"
import CreditsPurchase from "@/components/credits-purchase"
import { EntrepreneurDashboard } from "@/components/entrepreneur-dashboard"
import { UnifiedWorkspace } from "@/components/unified-workspace"
import { UserDashboard } from "@/components/user-dashboard"

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="trend-analyzer-theme">
      <AuthProvider>
        <Router>
        <Routes>
          {/* Regular user interface */}
          <Route path="/" element={<TrendAnalyzer />} />
        <Route path="/dashboard" element={<UserDashboard />} />
          <Route path="/workspace" element={<UnifiedWorkspace />} />
          <Route path="/entrepreneur" element={<EntrepreneurDashboard />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/user-center" element={<UserCenter />} />
          <Route path="/credits" element={<CreditsPurchase />} />
          
          {/* Payment success page */}
          <Route path="/payment-success" element={<PaymentSuccess />} />
          
          {/* Admin login page */}
          <Route path="/admin/login" element={<AdminLogin />} />
          
          {/* Admin interface */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="subscriptions" element={<SubscriptionManagement />} />
            <Route path="monitoring" element={<SystemMonitoring />} />
          </Route>
          
          {/* 404 redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App