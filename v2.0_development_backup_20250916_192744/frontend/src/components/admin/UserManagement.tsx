import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, UserPlus, MoreHorizontal, RefreshCw, Plus } from 'lucide-react';
import { adminApiClient } from '@/lib/admin-api';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';

interface User {
  id: string;
  email: string;
  username: string;
  status: 'active' | 'inactive' | 'banned';
  subscription: string;
  createdAt: string;
  lastLogin: string;
}

function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);
  // New: Credits adjustment dialog state
  const [isAdjustDialogOpen, setIsAdjustDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [adjustAmount, setAdjustAmount] = useState<string>('1000'); // Default 1000, convenient for admin top-up
  const [adjustDescription, setAdjustDescription] = useState<string>('Admin manual adjustment');
  const [adjustSubmitting, setAdjustSubmitting] = useState(false);
  const [adjustResult, setAdjustResult] = useState<{ new_balance: number } | null>(null);
  const [adjustError, setAdjustError] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      // Fix: Use adminApiClient.users.getAll()
      const response = await adminApiClient.users.getAll();
      // Map backend returned fields to frontend User structure
      const mapped: User[] = (response.data || []).map((u: any) => ({
        id: String(u.id),
        email: u.email,
        username: u.username,
        status: u.is_active ? 'active' : 'inactive',
        subscription: u.subscription_tier,
        createdAt: u.created_at,
        lastLogin: u.last_login,
      }));
      setUsers(mapped);
    } catch (err) {
      setError('Failed to fetch user list');
      console.error('Failed to fetch users:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const filteredUsers = users.filter(user => 
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // New: Open credits adjustment dialog method, placed before return
  const openAdjustDialog = (user: User) => {
    setSelectedUser(user);
    setAdjustAmount('1000');
    setAdjustDescription('Admin manual adjustment');
    setAdjustError(null);
    setAdjustResult(null);
    setIsAdjustDialogOpen(true);
  };

  // New: Submit adjustment request method, placed before return
  const handleAdjustCredits = async () => {
    await submitAdjust();
  };

  const submitAdjust = async () => {
    if (!selectedUser) return;
    const amount = parseInt(adjustAmount, 10);
    if (isNaN(amount) || amount === 0) {
      setAdjustError('Please enter a non-zero integer as credit value (positive for top-up, negative for deduction)');
      return;
    }
    setAdjustSubmitting(true);
    setAdjustError(null);
    setAdjustResult(null);
    try {
      const res = await adminApiClient.credits.adjustByUserId(Number(selectedUser.id), {
        amount,
        description: adjustDescription?.trim() || undefined,
      });
      const newBalance = res?.data?.new_balance;
      setAdjustResult({ new_balance: newBalance });
      // Optional: If need to refresh list (if future list displays balance), can call fetchUsers()
      // await fetchUsers();
    } catch (e: any) {
      console.error('Adjust credits failed:', e);
      setAdjustError(e?.response?.data?.detail || 'Failed to adjust credits, please try again later');
    } finally {
      setAdjustSubmitting(false);
    }
  };
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default">Active</Badge>;
      case 'inactive':
        return <Badge variant="secondary">Inactive</Badge>;
      case 'banned':
        return <Badge variant="destructive">Disabled</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-600">Loading...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page title and actions */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage system users and permissions</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={fetchUsers} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add User
          </Button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Search and filter */}
      <Card>
        <CardHeader>
          <CardTitle>User List</CardTitle>
          <CardDescription>Total {users.length} users</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2 mb-4">
            <Search className="h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by email or username..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
          </div>

          {/* User table */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Subscription</TableHead>
                <TableHead>Registration Date</TableHead>
                <TableHead>Last Login</TableHead>
                <TableHead className="w-[50px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-gray-500">
                    {searchTerm ? 'No matching users found' : 'No user data available'}
                  </TableCell>
                </TableRow>
              ) : (
                filteredUsers.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{user.username}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(user.status)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{user.subscription}</Badge>
                      </TableCell>
                      <TableCell className="text-sm text-gray-500">
                        {new Date(user.createdAt).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-sm text-gray-500">
                        {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Never logged in'}
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" onClick={() => openAdjustDialog(user)}>
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
        </CardContent>
      </Card>

      {/* Adjust credits dialog */}
      <Dialog open={isAdjustDialogOpen} onOpenChange={setIsAdjustDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Adjust Credits</DialogTitle>
            <DialogDescription>
              Adjust credits for user {selectedUser.username} ({selectedUser.email}).
              Positive numbers for top-up, negative numbers for deduction.
            </DialogDescription>
          </DialogHeader>
          {!selectedUser ? (
            <p className="text-red-500">Please select a user to adjust</p>
          ) : (
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">Credits</Label>
              <Input
                type="number"
                value={adjustAmount}
                onChange={(e) => setAdjustAmount(e.target.value)}
                className="col-span-3"
                placeholder="e.g.: 1000 (top-up) or -100 (deduction)"
              />
              <Label className="text-right">Note</Label>
              <Input
                value={adjustNote}
                onChange={(e) => setAdjustNote(e.target.value)}
                className="col-span-3"
                placeholder="Note (optional)"
              />
            </div>
          )}
          {adjustResult && (
            <div className="text-green-600 text-sm">
              Adjustment successful, new balance: {adjustResult.new_balance}
            </div>
          )}
          {adjustError && (
            <div className="text-red-500 text-sm">{adjustError}</div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAdjustDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAdjustCredits} disabled={adjustSubmitting}>
              {adjustSubmitting ? 'Submitting...' : 'Confirm Adjustment'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default UserManagement;