import React from 'react';
import { Outlet, Link } from 'react-router-dom';

const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 简单的导航栏 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">IdeaEden</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/dashboard" className="text-gray-700 hover:text-gray-900">仪表板</Link>
              <Link to="/workspace" className="text-gray-700 hover:text-gray-900">工作区</Link>
              <Link to="/analyze" className="text-gray-700 hover:text-gray-900">分析</Link>
              <Link to="/profile" className="text-gray-700 hover:text-gray-900">个人资料</Link>
              <Link to="/settings" className="text-gray-700 hover:text-gray-900">设置</Link>
            </div>
          </div>
        </div>
      </nav>
      
      {/* 主要内容区域 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;