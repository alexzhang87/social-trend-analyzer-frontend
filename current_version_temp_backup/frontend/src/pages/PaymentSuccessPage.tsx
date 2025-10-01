import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, Download, ArrowRight } from 'lucide-react';
import { useAuth } from '../components/auth-provider';
import { useLoading } from '../components/loading-provider';
import { toast } from 'sonner';

interface PaymentDetails {
  session_id: string;
  amount: number;
  currency: string;
  product_type: 'subscription' | 'credits';
  product_name: string;
  credits_added?: number;
  subscription_tier?: string;
}

export default function PaymentSuccessPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const { setLoading } = useLoading();
  const [paymentDetails, setPaymentDetails] = useState<PaymentDetails | null>(null);
  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    
    if (!sessionId) {
      toast.error('无效的支付会话');
      navigate('/pricing');
      return;
    }

    verifyPayment(sessionId);
  }, [searchParams, navigate]);

  const verifyPayment = async (sessionId: string) => {
    try {
      setLoading(true, '验证支付状态...');
      
      const response = await fetch(`/api/v1/payments/verify-payment?session_id=${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('支付验证失败');
      }

      const data = await response.json();
      setPaymentDetails(data);
      setIsVerified(true);
      
      // 刷新用户信息以获取最新的积分和订阅状态
      await refreshUser();
      
      toast.success('支付成功！');
      
    } catch (error) {
      console.error('支付验证失败:', error);
      toast.error('支付验证失败，请联系客服');
      navigate('/pricing');
    } finally {
      setLoading(false);
    }
  };

  const downloadReceipt = async () => {
    if (!paymentDetails) return;
    
    try {
      const response = await fetch(`/api/v1/payments/receipt/${paymentDetails.session_id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('下载收据失败');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `receipt-${paymentDetails.session_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('收据下载成功');
    } catch (error) {
      console.error('下载收据失败:', error);
      toast.error('下载收据失败');
    }
  };

  if (!isVerified || !paymentDetails) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p>正在验证支付状态...</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <Card className="border-green-200 bg-green-50">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <CheckCircle className="h-16 w-16 text-green-500" />
            </div>
            <CardTitle className="text-2xl text-green-700">
              支付成功！
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* 支付详情 */}
            <div className="bg-white rounded-lg p-6 space-y-4">
              <h3 className="font-semibold text-lg mb-4">支付详情</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">产品</p>
                  <p className="font-medium">{paymentDetails.product_name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">金额</p>
                  <p className="font-medium">
                    ${paymentDetails.amount} {paymentDetails.currency.toUpperCase()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">类型</p>
                  <p className="font-medium">
                    {paymentDetails.product_type === 'subscription' ? '订阅' : '积分包'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">订单号</p>
                  <p className="font-medium text-xs">{paymentDetails.session_id}</p>
                </div>
              </div>

              {paymentDetails.product_type === 'credits' && paymentDetails.credits_added && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-blue-700 font-medium">
                    🎉 您的账户已成功添加 {paymentDetails.credits_added} 积分！
                  </p>
                </div>
              )}

              {paymentDetails.product_type === 'subscription' && paymentDetails.subscription_tier && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-blue-700 font-medium">
                    🎉 您已成功订阅 {paymentDetails.subscription_tier} 方案！
                  </p>
                </div>
              )}
            </div>

            {/* 当前账户状态 */}
            {user && (
              <div className="bg-white rounded-lg p-6">
                <h3 className="font-semibold text-lg mb-4">当前账户状态</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">可用积分</p>
                    <p className="font-medium text-xl text-blue-600">{user.credits || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">订阅方案</p>
                    <p className="font-medium">
                      {user.subscription_tier || '无订阅'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button 
                onClick={downloadReceipt}
                variant="outline"
                className="flex-1"
              >
                <Download className="h-4 w-4 mr-2" />
                下载收据
              </Button>
              <Button 
                onClick={() => navigate('/dashboard')}
                className="flex-1"
              >
                前往控制台
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>

            {/* 下一步提示 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">接下来您可以：</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 在控制台查看您的积分和订阅状态</li>
                <li>• 开始使用我们的分析工具</li>
                <li>• 查看使用教程和帮助文档</li>
                {paymentDetails.product_type === 'subscription' && (
                  <li>• 在账户设置中管理您的订阅</li>
                )}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}