import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/components/auth-provider';
import { Toaster } from '@/components/ui/toaster';
import LandingPage from '@/components/landing-page';
import { LoginPage } from '@/components/login-page';
import { RegisterPage } from '@/components/register-page';
import { UnifiedWorkspace } from '@/components/unified-workspace';
import PricingPage from '@/components/pricing-page';
import { CreditsPurchase } from '@/components/credits-purchase';
import { PaymentSuccess } from '@/components/payment-success';
import { AdminLogin } from '@/components/admin/AdminLogin';
import { AdminDashboard } from '@/components/admin/AdminDashboard';
import UserManagement from '@/components/admin/UserManagement';
import { SubscriptionManagement } from '@/components/admin/SubscriptionManagement';
import { SystemMonitoring } from '@/components/admin/SystemMonitoring';
import { AdminLayout } from '@/components/admin/AdminLayout';
import { UserDashboard } from '@/components/user-dashboard';
import { AnalysisPage } from '@/components/analysis-page';
import AIExpertConsultation from '@/components/ai-expert-consultation';
import SimpleChatPage from '@/components/simple-chat-page';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/pricing" element={<PricingPage />} />
            
            {/* Protected routes */}
            <Route path="/workspace" element={<UnifiedWorkspace />} />
            <Route path="/dashboard" element={<UserDashboard />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/ai-expert" element={<AIExpertConsultation />} />
            <Route path="/chat" element={<SimpleChatPage />} />
            <Route path="/credits" element={<CreditsPurchase />} />
            <Route path="/payment-success" element={<PaymentSuccess />} />

            {/* Admin routes */}
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin" element={
              <AdminLayout>
                <AdminDashboard />
              </AdminLayout>
            } />
            <Route path="/admin/users" element={
              <AdminLayout>
                <UserManagement />
              </AdminLayout>
            } />
            <Route path="/admin/subscriptions" element={
              <AdminLayout>
                <SubscriptionManagement />
              </AdminLayout>
            } />
            <Route path="/admin/monitoring" element={
              <AdminLayout>
                <SystemMonitoring />
              </AdminLayout>
            } />

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        <Toaster />
      </AuthProvider>
    </Router>
  );
}

export default App