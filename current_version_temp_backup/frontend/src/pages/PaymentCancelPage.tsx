import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { XCircle, ArrowLeft, CreditCard, HelpCircle } from 'lucide-react';

export default function PaymentCancelPage() {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <XCircle className="h-16 w-16 text-orange-500" />
            </div>
            <CardTitle className="text-2xl text-orange-700">
              支付已取消
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center text-gray-600">
              <p className="mb-4">
                您的支付已被取消，没有产生任何费用。
              </p>
              <p>
                如果您遇到了问题或需要帮助，请随时联系我们的客服团队。
              </p>
            </div>

            {/* 可能的原因 */}
            <div className="bg-white rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-4">可能的原因</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  您主动取消了支付流程
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  支付信息验证失败
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  网络连接问题
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  银行卡余额不足或被限制
                </li>
              </ul>
            </div>

            {/* 解决方案 */}
            <div className="bg-white rounded-lg p-6">
              <h3 className="font-semibold text-lg mb-4">解决方案</h3>
              <div className="space-y-3">
                <div className="flex items-start">
                  <CreditCard className="h-5 w-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <p className="font-medium">检查支付信息</p>
                    <p className="text-sm text-gray-600">
                      确保您的银行卡信息正确，余额充足，且未被银行限制在线支付
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <HelpCircle className="h-5 w-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <p className="font-medium">联系客服</p>
                    <p className="text-sm text-gray-600">
                      如果问题持续存在，请联系我们的客服团队获取帮助
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button 
                onClick={() => navigate('/pricing')}
                variant="outline"
                className="flex-1"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                返回定价页面
              </Button>
              <Button 
                onClick={() => navigate('/contact')}
                className="flex-1"
              >
                <HelpCircle className="h-4 w-4 mr-2" />
                联系客服
              </Button>
            </div>

            {/* 其他选择 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium mb-2">其他选择</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 尝试使用不同的支付方式</li>
                <li>• 联系您的银行确认在线支付设置</li>
                <li>• 稍后再试，可能是临时的网络问题</li>
                <li>• 查看我们的帮助文档了解更多支付信息</li>
              </ul>
            </div>

            {/* 联系信息 */}
            <div className="text-center text-sm text-gray-500">
              <p>需要帮助？</p>
              <p>
                邮箱: support@example.com | 电话: 400-123-4567
              </p>
              <p>
                客服时间: 周一至周五 9:00-18:00
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}