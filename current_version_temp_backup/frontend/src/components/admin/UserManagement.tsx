import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  subscription_tier: string;
  subscription_status: string;
  credits: number;
  created_at: string;
  last_login: string;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState('all');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/v1/admin/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      const response = await fetch(`/api/v1/admin/users/${userId}/toggle-status`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        setUsers(users.map(user => 
          user.id === userId ? { ...user, is_active: !currentStatus } : user
        ));
      }
    } catch (error) {
      console.error('Failed to toggle user status:', error);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (selectedTab === 'active') return matchesSearch && user.is_active;
    if (selectedTab === 'inactive') return matchesSearch && !user.is_active;
    if (selectedTab === 'premium') return matchesSearch && user.subscription_tier !== 'free';
    
    return matchesSearch;
  });

  const getStatusBadge = (user: User) => {
    if (!user.is_active) return <Badge variant="destructive">已禁用</Badge>;
    if (user.subscription_tier === 'premium') return <Badge variant="default">高级用户</Badge>;
    if (user.subscription_tier === 'pro') return <Badge variant="secondary">专业用户</Badge>;
    return <Badge variant="outline">免费用户</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-500">加载用户数据...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>用户管理</CardTitle>
          <CardDescription>
            管理系统中的所有用户账户
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-6">
            <Input
              placeholder="搜索用户名或邮箱..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-sm"
            />
            <Button variant="outline">
              导出用户数据
            </Button>
          </div>

          <Tabs value={selectedTab} onValueChange={setSelectedTab}>
            <TabsList>
              <TabsTrigger value="all">全部用户 ({users.length})</TabsTrigger>
              <TabsTrigger value="active">活跃用户 ({users.filter(u => u.is_active).length})</TabsTrigger>
              <TabsTrigger value="inactive">已禁用 ({users.filter(u => !u.is_active).length})</TabsTrigger>
              <TabsTrigger value="premium">付费用户 ({users.filter(u => u.subscription_tier !== 'free').length})</TabsTrigger>
            </TabsList>

            <TabsContent value={selectedTab} className="mt-6">
              <div className="space-y-4">
                {filteredUsers.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <div>
                          <h3 className="font-medium">{user.username}</h3>
                          <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                        {getStatusBadge(user)}
                      </div>
                      <div className="mt-2 text-xs text-gray-400">
                        <span>积分: {user.credits}</span>
                        <span className="mx-2">•</span>
                        <span>注册: {new Date(user.created_at).toLocaleDateString('zh-CN')}</span>
                        {user.last_login && (
                          <>
                            <span className="mx-2">•</span>
                            <span>最后登录: {new Date(user.last_login).toLocaleDateString('zh-CN')}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant={user.is_active ? "destructive" : "default"}
                        size="sm"
                        onClick={() => toggleUserStatus(user.id, user.is_active)}
                      >
                        {user.is_active ? '禁用' : '启用'}
                      </Button>
                      <Button variant="outline" size="sm">
                        详情
                      </Button>
                    </div>
                  </div>
                ))}
                
                {filteredUsers.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    没有找到匹配的用户
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}