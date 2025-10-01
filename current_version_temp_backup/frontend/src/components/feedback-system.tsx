import React, { useState, useEffect } from 'react';
import { MessageSquare, Star, ThumbsUp, ThumbsDown, Bug, Lightbulb, AlertCircle, Send, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { useAuth } from '@/components/auth-provider';

interface FeedbackData {
  type: 'bug' | 'feature' | 'improvement' | 'compliment' | 'complaint' | 'question';
  title: string;
  description: string;
  rating?: number;
  category?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  attachments?: File[];
  userAgent: string;
  url: string;
  timestamp: string;
}

interface FeedbackSystemProps {
  trigger?: React.ReactNode;
  autoShow?: boolean;
  context?: string;
}

const feedbackTypes = [
  {
    id: 'bug' as const,
    label: '错误报告',
    description: '报告应用中的问题或错误',
    icon: Bug,
    color: 'text-red-600 bg-red-100',
  },
  {
    id: 'feature' as const,
    label: '功能建议',
    description: '建议新功能或改进',
    icon: Lightbulb,
    color: 'text-blue-600 bg-blue-100',
  },
  {
    id: 'improvement' as const,
    label: '体验改进',
    description: '建议改进现有功能',
    icon: ThumbsUp,
    color: 'text-green-600 bg-green-100',
  },
  {
    id: 'compliment' as const,
    label: '表扬反馈',
    description: '分享您的积极体验',
    icon: Star,
    color: 'text-yellow-600 bg-yellow-100',
  },
  {
    id: 'complaint' as const,
    label: '投诉建议',
    description: '反映不满意的地方',
    icon: ThumbsDown,
    color: 'text-orange-600 bg-orange-100',
  },
  {
    id: 'question' as const,
    label: '使用咨询',
    description: '询问使用方法或疑问',
    icon: MessageSquare,
    color: 'text-purple-600 bg-purple-100',
  },
];

const categories = [
  '用户界面',
  '功能性能',
  '数据分析',
  '账户管理',
  '支付相关',
  '移动端体验',
  '其他',
];

export function FeedbackSystem({ trigger, autoShow = false, context }: FeedbackSystemProps) {
  const [isOpen, setIsOpen] = useState(autoShow);
  const [currentStep, setCurrentStep] = useState<'type' | 'details' | 'success'>('type');
  const [feedbackData, setFeedbackData] = useState<Partial<FeedbackData>>({
    userAgent: navigator.userAgent,
    url: window.location.href,
    timestamp: new Date().toISOString(),
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [rating, setRating] = useState(0);
  const { user } = useAuth();

  useEffect(() => {
    if (context) {
      setFeedbackData(prev => ({ ...prev, category: context }));
    }
  }, [context]);

  const handleTypeSelect = (type: FeedbackData['type']) => {
    setFeedbackData(prev => ({ ...prev, type }));
    setCurrentStep('details');
  };

  const handleSubmit = async () => {
    if (!feedbackData.type || !feedbackData.title || !feedbackData.description) {
      toast.error('请填写完整的反馈信息');
      return;
    }

    setIsSubmitting(true);
    try {
      const submitData = {
        ...feedbackData,
        rating: rating > 0 ? rating : undefined,
        userId: user?.id,
        userEmail: user?.email,
      };

      const response = await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });

      if (response.ok) {
        setCurrentStep('success');
        toast.success('感谢您的反馈！我们会认真处理您的建议。');
        
        // 3秒后自动关闭
        setTimeout(() => {
          setIsOpen(false);
          resetForm();
        }, 3000);
      } else {
        throw new Error('提交失败');
      }
    } catch (error) {
      toast.error('提交反馈时出现错误，请稍后重试');
      console.error('Feedback submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setCurrentStep('type');
    setFeedbackData({
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
    });
    setRating(0);
  };

  const handleClose = () => {
    setIsOpen(false);
    resetForm();
  };

  const renderStarRating = () => {
    return (
      <div className="flex items-center space-x-1">
        <span className="text-sm text-gray-600 mr-2">评分:</span>
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => setRating(star)}
            className={`p-1 rounded transition-colors ${
              star <= rating
                ? 'text-yellow-400 hover:text-yellow-500'
                : 'text-gray-300 hover:text-gray-400'
            }`}
          >
            <Star className="w-5 h-5 fill-current" />
          </button>
        ))}
        {rating > 0 && (
          <span className="text-sm text-gray-600 ml-2">
            {rating === 1 && '很不满意'}
            {rating === 2 && '不满意'}
            {rating === 3 && '一般'}
            {rating === 4 && '满意'}
            {rating === 5 && '非常满意'}
          </span>
        )}
      </div>
    );
  };

  const renderTypeSelection = () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-2">选择反馈类型</h3>
        <p className="text-sm text-gray-600 mb-4">
          请选择最符合您反馈内容的类型，这将帮助我们更好地处理您的建议。
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {feedbackTypes.map((type) => {
          const Icon = type.icon;
          return (
            <button
              key={type.id}
              onClick={() => handleTypeSelect(type.id)}
              className="p-4 border rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left group"
            >
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${type.color} group-hover:scale-110 transition-transform`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{type.label}</h4>
                  <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );

  const renderDetailsForm = () => {
    const selectedType = feedbackTypes.find(t => t.id === feedbackData.type);
    const Icon = selectedType?.icon || MessageSquare;

    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${selectedType?.color}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">{selectedType?.label}</h3>
            <p className="text-sm text-gray-600">{selectedType?.description}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="title">标题 *</Label>
            <Input
              id="title"
              placeholder="简要描述您的反馈"
              value={feedbackData.title || ''}
              onChange={(e) => setFeedbackData(prev => ({ ...prev, title: e.target.value }))}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="description">详细描述 *</Label>
            <Textarea
              id="description"
              placeholder="请详细描述您的反馈内容，包括具体的问题、建议或想法..."
              value={feedbackData.description || ''}
              onChange={(e) => setFeedbackData(prev => ({ ...prev, description: e.target.value }))}
              className="mt-1 min-h-[120px]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="category">相关分类</Label>
              <Select
                value={feedbackData.category || ''}
                onValueChange={(value) => setFeedbackData(prev => ({ ...prev, category: value }))}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="选择相关分类" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="priority">优先级</Label>
              <Select
                value={feedbackData.priority || ''}
                onValueChange={(value: any) => setFeedbackData(prev => ({ ...prev, priority: value }))}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="选择优先级" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">低</SelectItem>
                  <SelectItem value="medium">中</SelectItem>
                  <SelectItem value="high">高</SelectItem>
                  <SelectItem value="urgent">紧急</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 评分组件 */}
          <div className="p-4 bg-gray-50 rounded-lg">
            {renderStarRating()}
          </div>

          {/* 系统信息 */}
          <div className="text-xs text-gray-500 space-y-1">
            <p><strong>系统信息:</strong></p>
            <p>页面: {feedbackData.url}</p>
            <p>时间: {new Date(feedbackData.timestamp!).toLocaleString()}</p>
            {user && <p>用户: {user.email}</p>}
          </div>
        </div>

        <div className="flex justify-between pt-4">
          <Button
            variant="outline"
            onClick={() => setCurrentStep('type')}
          >
            返回
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !feedbackData.title || !feedbackData.description}
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                提交中...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                提交反馈
              </>
            )}
          </Button>
        </div>
      </div>
    );
  };

  const renderSuccess = () => (
    <div className="text-center space-y-4 py-8">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
        <ThumbsUp className="w-8 h-8 text-green-600" />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-green-600 mb-2">
          反馈提交成功！
        </h3>
        <p className="text-gray-600">
          感谢您的宝贵反馈，我们会认真处理并尽快回复您。
        </p>
      </div>
      <div className="text-sm text-gray-500">
        <p>反馈ID: FB_{Date.now()}</p>
        <p>我们通常会在24小时内回复</p>
      </div>
    </div>
  );

  const defaultTrigger = (
    <Button variant="outline" size="sm">
      <MessageSquare className="w-4 h-4 mr-2" />
      反馈
    </Button>
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle>
                {currentStep === 'type' && '用户反馈'}
                {currentStep === 'details' && '反馈详情'}
                {currentStep === 'success' && '提交成功'}
              </DialogTitle>
              <DialogDescription>
                {currentStep === 'type' && '您的反馈对我们非常重要，帮助我们不断改进产品'}
                {currentStep === 'details' && '请提供详细信息，以便我们更好地处理您的反馈'}
                {currentStep === 'success' && '我们已收到您的反馈，感谢您的支持'}
              </DialogDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClose}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>
        
        <div className="mt-4">
          {currentStep === 'type' && renderTypeSelection()}
          {currentStep === 'details' && renderDetailsForm()}
          {currentStep === 'success' && renderSuccess()}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// 浮动反馈按钮组件
export function FloatingFeedbackButton() {
  return (
    <div className="fixed bottom-6 right-6 z-40">
      <FeedbackSystem
        trigger={
          <Button
            size="lg"
            className="rounded-full shadow-lg hover:shadow-xl transition-shadow"
          >
            <MessageSquare className="w-5 h-5 mr-2" />
            反馈
          </Button>
        }
      />
    </div>
  );
}

// 快速反馈组件（用于特定页面或功能）
export function QuickFeedback({ context, className }: { context?: string; className?: string }) {
  return (
    <div className={className}>
      <FeedbackSystem
        context={context}
        trigger={
          <Button variant="ghost" size="sm" className="text-gray-500 hover:text-gray-700">
            <MessageSquare className="w-4 h-4 mr-1" />
            反馈
          </Button>
        }
      />
    </div>
  );
}