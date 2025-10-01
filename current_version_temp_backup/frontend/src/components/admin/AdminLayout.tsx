import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';

interface AdminLayoutProps {
  children?: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const location = useLocation();
  
  const menuItems = [
    { path: '/admin/dashboard', label: '仪表板', icon: '📊' },
    { path: '/admin/users', label: '用户管理', icon: '👥' },
    { path: '/admin/subscriptions', label: '订阅管理', icon: '💳' },
    { path: '/admin/analytics', label: '数据分析', icon: '📈' },
    { path: '/admin/settings', label: '系统设置', icon: '⚙️' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        {/* 侧边栏 */}
        <div className="w-64 bg-white shadow-sm border-r">
          <div className="p-6">
            <h1 className="text-xl font-bold text-gray-900">管理后台</h1>
            <Badge variant="secondary" className="mt-2">Admin Panel</Badge>
          </div>
          
          <nav className="mt-6">
            <div className="px-3">
              {menuItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 transition-colors ${
                    location.pathname === item.path
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <span className="mr-3">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </div>
          </nav>
          
          <div className="absolute bottom-0 w-64 p-4 border-t">
            <Link to="/dashboard">
              <Button variant="outline" className="w-full">
                返回用户界面
              </Button>
            </Link>
          </div>
        </div>

        {/* 主内容区域 */}
        <div className="flex-1">
          <header className="bg-white shadow-sm border-b">
            <div className="px-6 py-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">
                  {menuItems.find(item => item.path === location.pathname)?.label || '管理后台'}
                </h2>
                <div className="flex items-center space-x-4">
                  <Badge variant="outline">在线</Badge>
                  <span className="text-sm text-gray-500">
                    {new Date().toLocaleString('zh-CN')}
                  </span>
                </div>
              </div>
            </div>
          </header>

          <main className="p-6">
            {children || <Outlet />}
          </main>
        </div>
      </div>
    </div>
  );
}