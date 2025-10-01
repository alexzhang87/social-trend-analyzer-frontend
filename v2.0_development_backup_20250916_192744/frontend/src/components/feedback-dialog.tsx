import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Star, MessageSquare } from 'lucide-react';
import { toast } from 'sonner';
import { authApiClient } from '@/lib/auth-api';

interface FeedbackDialogProps {
  analysisId?: string;
  trigger?: React.ReactNode;
}

interface FeedbackData {
  title: string;
  content: string;
  feedback_type: string;
  rating?: number;
  analysis_id?: string;
}

const FEEDBACK_TYPES = [
  { value: 'analysis_quality', label: 'Analysis Quality' },
  { value: 'feature_request', label: 'Feature Request' },
  { value: 'bug_report', label: 'Bug Report' },
  { value: 'general', label: 'General Feedback' },
];

export function FeedbackDialog({ analysisId, trigger }: FeedbackDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<FeedbackData>({
    title: '',
    content: '',
    feedback_type: 'general',
    rating: undefined,
    analysis_id: analysisId,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.content.trim()) {
      toast.error('Please fill in title and content');
      return;
    }

    setLoading(true);
    try {
      await authApiClient.post('/api/v1/feedback/', formData);
      toast.success('Feedback submitted successfully! Thank you for your valuable input.');
      setOpen(false);
      setFormData({
        title: '',
        content: '',
        feedback_type: 'general',
        rating: undefined,
        analysis_id: analysisId,
      });
    } catch (error: any) {
      console.error('Failed to submit feedback:', error);
      toast.error(error.response?.data?.detail || 'Submission failed, please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleRatingClick = (rating: number) => {
    setFormData(prev => ({ ...prev, rating }));
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm">
            <MessageSquare className="w-4 h-4 mr-2" />
            Feedback
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Feedback & Suggestions</DialogTitle>
          <DialogDescription>
            We value your opinion. Please tell us about your experience or suggestions for improvement.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Feedback type */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Feedback Type</label>
            <Select
              value={formData.feedback_type}
              onValueChange={(value) => setFormData(prev => ({ ...prev, feedback_type: value }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="analysis_quality">Analysis Quality</SelectItem>
                <SelectItem value="feature_request">Feature Request</SelectItem>
                <SelectItem value="bug_report">Bug Report</SelectItem>
                <SelectItem value="general">General Feedback</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Rating */}
          {formData.feedback_type === 'analysis_quality' && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Rating</label>
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => handleRatingClick(star)}
                    className={`p-1 rounded transition-colors ${
                      formData.rating && star <= formData.rating
                        ? 'text-yellow-500'
                        : 'text-gray-300 hover:text-yellow-400'
                    }`}
                  >
                    <Star className="w-6 h-6 fill-current" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Title */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Title</label>
            <Input
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Please enter feedback title..."
              maxLength={200}
            />
          </div>

          {/* Content */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Detailed Description</label>
            <Textarea
              value={formData.content}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              placeholder="Please describe your issue or suggestion in detail..."
              rows={4}
              maxLength={1000}
            />
            <div className="text-xs text-gray-500 text-right">
              {formData.content.length}/1000
            </div>
          </div>

          {/* Submit button */}
          <div className="flex justify-end space-x-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}