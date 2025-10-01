import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  User, 
  CreditCard, 
  History, 
  Settings, 
  TrendingUp, 
  Calendar,
  Download
} from 'lucide-react';
import CreditsPurchase from './credits-purchase';
import { useAuth } from './auth-provider';
import { Link } from 'react-router-dom';

// Mock transaction history data
const mockTransactions = [
  {
    id: '1',
    type: 'consumption',
    amount: -2,
    description: 'Analysis: advanced_analysis',
    date: '2025-08-24T10:30:00Z',
    status: 'completed'
  },
  {
    id: '2',
    type: 'purchase',
    amount: 30,
    description: 'Credit package purchase: medium',
    date: '2025-08-23T15:45:00Z',
    status: 'completed'
  },
  {
    id: '3',
    type: 'subscription',
    amount: 15,
    description: 'Monthly credits reset: starter',
    date: '2025-08-01T00:00:00Z',
    status: 'completed'
  }
];

export function UserCenter() {
  const [activeTab, setActiveTab] = useState('overview');
  const { user, loading, isAuthenticated, refreshUser } = useAuth();

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">User Center</h1>
            <p className="text-muted-foreground">Manage your account, credits and subscriptions</p>
          </div>
          <Button variant="outline" disabled>
            Loading...
          </Button>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Loading</CardTitle>
            <CardDescription>Please wait while we fetch your account information...</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-muted-foreground">Fetching latest balance and subscription status...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold">Please login to view your account</h1>
          <p className="text-muted-foreground">You need to be logged in to access the user center.</p>
          <div className="flex justify-center gap-3">
            <Link to="/dashboard" className="px-4 py-2 rounded bg-primary text-white hover:opacity-90">Go to Dashboard</Link>
            <Link to="/pricing" className="px-4 py-2 rounded bg-secondary text-secondary-foreground hover:opacity-90">View Plans</Link>
          </div>
        </div>
      </div>
    );
  }

  const currentUser = {
    name: user?.username || '—',
    email: user?.email || '—',
    subscription_tier: user?.subscription_tier || 'free',
    credits_balance: user?.credits_balance ?? 0,
    subscription_expires_at: user?.subscription_expires_at,
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'consumption':
        return <TrendingUp className="w-4 h-4 text-red-500" />;
      case 'purchase':
        return <CreditCard className="w-4 h-4 text-green-500" />;
      case 'subscription':
        return <Calendar className="w-4 h-4 text-blue-500" />;
      default:
        return <History className="w-4 h-4" />;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">User Center</h1>
          <p className="text-muted-foreground">Manage your account, credits and subscriptions</p>
        </div>
        <Button variant="outline" onClick={refreshUser}>
          Refresh
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <User className="w-4 h-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="credits" className="flex items-center gap-2">
            <CreditCard className="w-4 h-4" />
            Credit Management
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <History className="w-4 h-4" />
            Transaction History
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Account Settings
          </TabsTrigger>
        </TabsList>

        {/* Overview Page */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Account Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Account Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">Username</p>
                  <p className="font-medium">{currentUser.name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{currentUser.email}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Current Plan</p>
                  <Badge variant="outline" className="mt-1">
                    {currentUser.subscription_tier.toUpperCase()}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Credit Balance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="w-5 h-5 text-yellow-500" />
                  Credit Balance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary mb-2">
                    {currentUser.credits_balance}
                  </p>
                  <p className="text-sm text-muted-foreground">Available Credits</p>
                  <Button size="sm" className="mt-3" onClick={() => setActiveTab('credits')}>
                    Purchase Credits
                  </Button>
                  {currentUser.credits_balance <= 0 && (
                    <div className="mt-4 bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded">
                      Your credit balance is 0. Please purchase credits or subscribe to continue using advanced analysis features.
                      <div className="mt-3 flex gap-3 justify-center">
                        <Link to="/pricing" className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700 text-sm">View Plans</Link>
                        <Link to="/credits" className="px-3 py-1.5 rounded bg-indigo-600 text-white hover:bg-indigo-700 text-sm">Buy Credits</Link>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Subscription Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-blue-500" />
                  Subscription Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground">Plan Type</p>
                  <p className="font-medium">{currentUser.subscription_tier.toUpperCase()}</p>
                </div>
                {currentUser.subscription_expires_at && (
                  <div>
                    <p className="text-sm text-muted-foreground">Expiry Date</p>
                    <p className="font-medium">
                      {formatDate(currentUser.subscription_expires_at)}
                    </p>
                  </div>
                )}
                <Button size="sm" variant="outline" className="w-full">
                  Manage Subscription
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Usage Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Monthly Usage Statistics</CardTitle>
              <CardDescription>Your analysis usage overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary">12</p>
                  <p className="text-sm text-muted-foreground">Total Analyses</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-500">8</p>
                  <p className="text-sm text-muted-foreground">Successful Analyses</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-500">3</p>
                  <p className="text-sm text-muted-foreground">PDF Reports</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-orange-500">25</p>
                  <p className="text-sm text-muted-foreground">Credits Consumed</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Credit Management */}
        <TabsContent value="credits">
          <CreditsPurchase 
            currentBalance={currentUser.credits_balance}
            userTier={currentUser.subscription_tier}
          />
        </TabsContent>

        {/* Transaction History */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Credit Transaction History</CardTitle>
              <CardDescription>View all your credit transaction records</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockTransactions.map((transaction) => (
                  <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {getTransactionIcon(transaction.type)}
                      <div>
                        <p className="font-medium">{transaction.description}</p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(transaction.date)}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`font-bold ${
                        transaction.amount > 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {transaction.amount > 0 ? '+' : ''}{transaction.amount} Credits
                      </p>
                      <Badge variant={transaction.status === 'completed' ? 'default' : 'secondary'}>
                        {transaction.status === 'completed' ? 'Completed' : 'Processing'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 text-center">
                <Button variant="outline" className="gap-2">
                  <Download className="w-4 h-4" />
                  Export Transaction Records
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Account Settings */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Account Settings</CardTitle>
              <CardDescription>Manage your personal information and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-3">Personal Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Username</label>
                    <p className="mt-1 p-2 border rounded bg-muted/50">{currentUser.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Email Address</label>
                    <p className="mt-1 p-2 border rounded bg-muted/50">{currentUser.email}</p>
                  </div>
                </div>
                <Button className="mt-4" variant="outline">
                  Edit Personal Information
                </Button>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Notification Settings</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Analysis Completion Notifications</span>
                    <Button variant="outline" size="sm">Enabled</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Monthly Reports</span>
                    <Button variant="outline" size="sm">Enabled</Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Promotional Notifications</span>
                    <Button variant="outline" size="sm">Enabled</Button>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3">Security Settings</h3>
                <div className="space-y-3">
                  <Button variant="outline">
                    Change Password
                  </Button>
                  <Button variant="outline">
                    Two-Factor Authentication
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default UserCenter;
