import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Search, UserPlus, MoreHorizontal, RefreshCw } from 'lucide-react';
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

export function UserManagement() {
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
  const submitAdjust = async () => {
    if (!selectedUser) return;
    const amount = parseInt(adjustAmount, 10);
    if (isNaN(amount) || amount === 0) {
      setAdjustError('请输入非零整数作为积分值（正数为充值，负数为扣减）');
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
      setAdjustError(e?.response?.data?.detail || '调整积分失败，请稍后再试');
    } finally {
      setAdjustSubmitting(false);
    }
  };
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default">活跃</Badge>;
      case 'inactive':
        return <Badge variant="secondary">非活跃</Badge>;
      case 'banned':
        return <Badge variant="destructive">已禁用</Badge>;
      default:
        return <Badge variant="outline">未知</Badge>;
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
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">用户管理</h1>
          <p className="text-gray-600">管理系统用户和权限</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={fetchUsers} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            刷新
          </Button>
          <Button size="sm">
            <UserPlus className="h-4 w-4 mr-2" />
            添加用户
          </Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* 搜索和筛选 */}
      <Card>
        <CardHeader>
          <CardTitle>用户列表</CardTitle>
          <CardDescription>共 {users.length} 个用户</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="按邮箱或用户名搜索..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* 用户表格 */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>用户</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>订阅</TableHead>
                  <TableHead>注册时间</TableHead>
                  <TableHead>最后登录</TableHead>
                  <TableHead className="w-[50px]">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                      {searchTerm ? '未找到匹配的用户' : '暂无用户数据'}
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
                        {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : '从未登录'}
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
          </div>
        </CardContent>
      </Card>

      {/* 调整积分弹窗 */}
      <Dialog open={isAdjustDialogOpen} onOpenChange={setIsAdjustDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>调整积分</DialogTitle>
            <DialogDescription>
              {selectedUser ? (
                <>
                  为用户 {selectedUser.username}（{selectedUser.email}）调整积分。
                  正数为充值，负数为扣减。
                </>
              ) : (
                '请选择要调整的用户'
              )}
            </DialogDescription>
          </DialogHeader>
      
          <div className="space-y-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">积分</Label>
              <Input
                className="col-span-3"
                type="number"
                value={adjustAmount}
                onChange={(e) => setAdjustAmount(e.target.value)}
                placeholder="例如：1000（充值）或 -100（扣减）"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">备注</Label>
              <Input
                className="col-span-3"
                value={adjustDescription}
                onChange={(e) => setAdjustDescription(e.target.value)}
                placeholder="备注（可选）"
              />
            </div>
      
            {adjustError && (
              <div className="text-red-600 text-sm">{adjustError}</div>
            )}
            {adjustResult && (
              <div className="text-green-600 text-sm">
                调整成功，新的余额为：{adjustResult.new_balance}
              </div>
            )}
          </div>
      
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAdjustDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={submitAdjust} disabled={adjustSubmitting || !selectedUser}>
              {adjustSubmitting ? '提交中...' : '确认调整'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}