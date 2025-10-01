import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { CheckCircle, Home, CreditCard } from 'lucide-react';
import { useAuth } from './auth-provider';

export function PaymentSuccess() {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user, refreshUser } = useAuth();
  const [paymentDetails, setPaymentDetails] = useState<any>(null);

  // Get session ID from URL parameters
  const sessionId = new URLSearchParams(location.search).get('session_id');

  useEffect(() => {
    const fetchPaymentDetails = async () => {
      if (!sessionId || !user) return;

      try {
        // Should call backend API to get payment details
    // Using mock data for now
        setPaymentDetails({
          id: sessionId,
          amount: 0,
          currency: 'usd',
          status: 'paid'
        });

        // Refresh user info to get latest credits and subscription info
        await refreshUser();

        toast({
          title: "Payment Successful",
        description: "Your payment has been completed and services have been activated"
        });
      } catch (error) {
        toast({
          title: "Failed to Get Payment Info",
        description: "Unable to get payment details, please check your account",
          variant: "destructive"
        });
      }
    };

    fetchPaymentDetails();
  }, [sessionId, user, refreshUser, toast]);

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Card className="glass-card">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          <CardTitle className="text-2xl">Payment Successful!</CardTitle>
          <CardDescription>
            Thank you for your purchase, your subscription has been activated
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-green-600" />
              <span className="font-medium">Transaction Completed</span>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Your payment has been successfully processed and services are now active
            </p>
          </div>

          {paymentDetails && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Transaction ID</p>
                  <p className="font-mono text-sm">{paymentDetails.id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                <p className="text-green-600 font-medium">Completed</p>
                </div>
              </div>
            </div>
          )}

          <div className="pt-4 border-t">
            <h3 className="font-medium mb-2">What you can do next:</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Start using new features for trend analysis immediately</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Check user center for credit balance and subscription details</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1">•</span>
                <span>Explore new features to enhance analysis effectiveness</span>
              </li>
            </ul>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button 
              onClick={() => navigate('/')} 
              className="flex-1"
            >
              <Home className="w-4 h-4 mr-2" />
              Back to Home
            </Button>
            <Button 
              variant="outline" 
              onClick={() => navigate('/user-center')}
              className="flex-1"
            >
              User Center
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
