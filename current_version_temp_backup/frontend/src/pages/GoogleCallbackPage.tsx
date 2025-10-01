import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../components/auth-provider';
import { useLoading } from '../components/loading-provider';
import { toast } from 'sonner';

export default function GoogleCallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { refreshUser } = useAuth();
  const { setLoading } = useLoading();

  useEffect(() => {
    const handleCallback = async () => {
      setLoading(true, '正在处理Google登录...');
      
      try {
        const token = searchParams.get('token');
        const error = searchParams.get('error');
        
        if (error) {
          toast.error('Google登录失败: ' + error);
          navigate('/login');
          return;
        }
        
        if (token) {
          // 保存token并获取用户信息
          localStorage.setItem('access_token', token);
          await refreshUser();
          toast.success('Google登录成功');
          navigate('/dashboard');
        } else {
          toast.error('未收到有效的认证信息');
          navigate('/login');
        }
      } catch (error) {
        console.error('Google callback error:', error);
        toast.error('处理Google登录时出错');
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    handleCallback();
  }, [searchParams, navigate, refreshUser, setLoading]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">正在处理Google登录...</p>
      </div>
    </div>
  );
}