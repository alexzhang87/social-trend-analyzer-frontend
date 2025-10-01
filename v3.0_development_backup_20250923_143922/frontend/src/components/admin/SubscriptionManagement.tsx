import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/components/auth-provider';
import { 
  Users, 
  CreditCard, 
  Calendar, 
  CheckCircle, 
  XCircle,
  Plus,
  Edit,
  Trash2,
  DollarSign
} from 'lucide-react';

interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  credits: number;
  features: string[];
}

interface UserSubscription {
  id: string;
  email: string;
  name: string;
  plan: string;
  status: 'active' | 'expired' | 'cancelled';
  credits: number;
  expiresAt: string;
}

export function SubscriptionManagement() {
  const { toast } = useToast();
  const { user } = useAuth();
  const [users, setUsers] = useState<UserSubscription[]>([]);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserSubscription | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Mock data
  useEffect(() => {
    // Mock get user subscription data
    setUsers([
      {
        id: '1',
        email: 'user1@example.com',
        name: 'John Doe',
        plan: 'starter',
        status: 'active',
        credits: 25,
        expiresAt: '2025-09-30'
      },
      {
        id: '2',
        email: 'user2@example.com',
        name: 'Jane Smith',
        plan: 'pro',
        status: 'active',
        credits: 60,
        expiresAt: '2025-10-15'
      }
    ]);

    // Mock get subscription plans
    setPlans([
      {
        id: 'free',
        name: 'Free Plan',
        price: 0,
        credits: 5,
        features: ['Basic Analysis', '3 daily limit']
      },
      {
        id: 'starter',
        name: 'Starter Plan',
        price: 9.99,
        credits: 25,
        features: ['Basic Analysis', 'Advanced Analysis', '20 daily limit']
      },
      {
        id: 'pro',
        name: 'Professional Plan',
        price: 29.99,
        credits: 60,
        features: ['All Features', 'Business Insights', 'Unlimited Usage']
      }
    ]);
  }, []);

  const handleUpdateSubscription = async (userData: UserSubscription) => {
    setIsProcessing(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update user data
      setUsers(prev => prev.map(user => 
        user.id === userData.id ? userData : user
      ));
      
      toast({
        title: 'Subscription Updated Successfully',
        description: `User ${userData.name}'s subscription has been updated`
      });
      
      setIsDialogOpen(false);
    } catch (error) {
      toast({
        title: 'Update Failed',
        description: 'Unable to update user subscription information',
        variant: 'destructive'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCreateCheckoutSession = async (productId: string, productType: 'subscription' | 'credits') => {
    if (!user) {
      toast({
        title: "Please Login First",
        description: "You need to login before purchasing a subscription",
        variant: "destructive"
      });
      return;
    }

    try {
      // Call backend API to create Stripe checkout session
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.access_token}`
        },
        body: JSON.stringify({
          product_type: productType,
          product_id: productId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create payment session');
      }

      const data = await response.json();
      
      // Redirect to Stripe checkout page
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('Failed to get payment page URL');
      }
    } catch (error) {
      toast({
        title: 'Payment Failed',
        description: error instanceof Error ? error.message : 'Unable to start payment process',
        variant: 'destructive'
      });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default">Active</Badge>;
      case 'canceled':
        return <Badge variant="secondary">Cancelled</Badge>;
      case 'past_due':
        return <Badge variant="destructive">Past Due</Badge>;
      case 'unpaid':
        return <Badge variant="destructive">Unpaid</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Subscription Management</h1>
          <p className="text-muted-foreground">Manage user subscriptions and payments</p>
        </div>
        <Button onClick={() => {
          setSelectedUser(null);
          setIsDialogOpen(true);
        }}>
          <Plus className="w-4 h-4 mr-2" />
          Add Subscription
        </Button>
      </div>

      {/* Subscription statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,234</div>
            <p className="text-xs text-muted-foreground">+12% this month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Subscriptions</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">892</div>
            <p className="text-xs text-muted-foreground">+5% this month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$12,234</div>
            <p className="text-xs text-muted-foreground">+18% this month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Renewal Rate</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87%</div>
            <p className="text-xs text-muted-foreground">+2% this month</p>
          </CardContent>
        </Card>
      </div>

      {/* User subscription list */}
      <Card>
        <CardHeader>
          <CardTitle>User Subscriptions</CardTitle>
          <CardDescription>Manage all user subscription statuses</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Subscription Plan</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Credit Balance</TableHead>
                <TableHead>Expiry Date</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{user.name}</div>
                      <div className="text-sm text-muted-foreground">{user.email}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{user.plan}</Badge>
                  </TableCell>
                  <TableCell>{getStatusBadge(user.status)}</TableCell>
                  <TableCell>{user.credits}</TableCell>
                  <TableCell>{user.expiresAt}</TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setSelectedUser(user);
                          setIsDialogOpen(true);
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleCreateCheckoutSession(user.plan, 'subscription')}
                      >
                        <CreditCard className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Subscription plan management */}
      <Card>
        <CardHeader>
          <CardTitle>Subscription Plans</CardTitle>
          <CardDescription>Manage available subscription plans</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {plans.map((plan) => (
              <Card key={plan.id} className={plan.id === 'pro' ? 'border-primary' : ''}>
                {plan.id === 'pro' && (
                  <div className="bg-primary text-primary-foreground px-3 py-1 text-xs font-semibold rounded-t-lg">
                    Most Popular
                  </div>
                )}
                <CardHeader>
                  <CardTitle>{plan.name}</CardTitle>
                  <div className="text-2xl font-bold">¥{plan.price}<span className="text-sm font-normal text-muted-foreground">/month</span></div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center">
                      <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                      {plan.credits} credits per month
                    </li>
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center">
                        <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
                <div className="p-4 pt-0">
                  <Button 
                    className="w-full" 
                    variant={plan.id === 'pro' ? 'default' : 'outline'}
                    onClick={() => handleCreateCheckoutSession(plan.id, 'subscription')}
                  >
                    Select Plan
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Edit subscription dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedUser ? 'Edit Subscription' : 'Add Subscription'}</DialogTitle>
            <DialogDescription>
              {selectedUser ? 'Modify user subscription information' : 'Create subscription for new user'}
            </DialogDescription>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-4">
              <div>
                <Label>User Email</Label>
                <Input value={selectedUser.email} disabled />
              </div>
              <div>
                <Label>Subscription Plan</Label>
                <Select 
                  value={selectedUser.plan} 
                  onValueChange={(value) => setSelectedUser({...selectedUser, plan: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {plans.map((plan) => (
                      <SelectItem key={plan.id} value={plan.id}>
                        {plan.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Credit Balance</Label>
                <Input 
                  type="number" 
                  value={selectedUser.credits} 
                  onChange={(e) => setSelectedUser({...selectedUser, credits: parseInt(e.target.value) || 0})}
                />
              </div>
              <div>
                <Label>Status</Label>
                <Select 
                  value={selectedUser.status} 
                  onValueChange={(value: any) => setSelectedUser({...selectedUser, status: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="expired">Expired</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Expiry Date</Label>
                <Input 
                  type="date" 
                  value={selectedUser.expiresAt} 
                  onChange={(e) => setSelectedUser({...selectedUser, expiresAt: e.target.value})}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={() => selectedUser && handleUpdateSubscription(selectedUser)}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}