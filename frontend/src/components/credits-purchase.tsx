import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Coins, Flame, TrendingUp } from 'lucide-react';
import { useAuth } from './auth-provider';
import { useToast } from '@/hooks/use-toast';

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  originalPrice: number;
  discount: number;
  pricePerCredit: number;
  popular?: boolean;
  description: string;
}

const creditPackages: CreditPackage[] = [
  {
    id: 'small',
    name: 'Small Package',
    credits: 10,
    price: 4.99,
    originalPrice: 9.99,
    discount: 50,
    pricePerCredit: 0.499,
    description: 'STARTER users can perform 5 additional analyses'
  },
  {
    id: 'medium',
    name: 'Medium Package',
    credits: 30,
    price: 11.99,
    originalPrice: 23.99,
    discount: 50,
    pricePerCredit: 0.400,
    popular: true,
    description: 'PRO users can perform 10 additional analyses'
  },
  {
    id: 'large',
    name: 'Large Package',
    credits: 75,
    price: 24.99,
    originalPrice: 49.99,
    discount: 50,
    pricePerCredit: 0.333,
    description: 'For enterprise temporary needs, best value'
  }
];

interface CreditsPurchaseProps {
  currentBalance?: number;
  userTier?: string;
  onPurchase?: (packageId: string) => void;
}

export function CreditsPurchase({ 
  currentBalance = 0, 
  userTier = 'starter',
  onPurchase 
}: CreditsPurchaseProps) {
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const { user } = useAuth();
  const { toast } = useToast();

  const handlePurchase = async (packageId: string) => {
    if (!user) {
      toast({
        title: "Please login first",
        description: "You need to login before purchasing credits",
        variant: "destructive"
      });
      return;
    }

    setSelectedPackage(packageId);
    setIsProcessing(true);
    
    try {
      // Call backend API to create Stripe checkout session
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}/api/v1/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.access_token}`
        },
        body: JSON.stringify({
          product_type: 'credits',
          product_id: packageId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create payment session');
      }

      const data = await response.json();
      
      // Redirect to Stripe checkout page
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        throw new Error('Failed to get payment page URL');
      }
      
      if (onPurchase) {
        onPurchase(packageId);
      }
    } catch (error) {
      toast({
        title: "Purchase failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive"
      });
      console.error('Purchase failed:', error);
    } finally {
      setIsProcessing(false);
      setSelectedPackage(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Current credit status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Coins className="w-5 h-5 text-yellow-500" />
            Current Credit Balance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-3xl font-bold text-primary">{currentBalance}</p>
              <p className="text-sm text-muted-foreground">Available Credits</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Current Plan</p>
              <Badge variant="outline" className="text-xs">
                {userTier.toUpperCase()}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Limited time offer banner - enhanced */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-orange-500 via-red-500 to-pink-500 rounded-lg blur opacity-50 animate-pulse"></div>
        <div className="relative bg-gradient-to-r from-orange-500 to-red-500 text-white p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-white/20 p-2 rounded-full">
                <Flame className="w-8 h-8 animate-bounce" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Limited Time Offer 50% OFF</h3>
                <p className="text-sm opacity-90">All credit packages enjoy 50% discount, valid until December 31, 2025</p>
              </div>
            </div>
            <div className="text-right">
              <div className="bg-white/20 px-4 py-2 rounded-full">
                <p className="text-sm font-semibold">Save up to 50%</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Credit package selection */}
      <div className="grid md:grid-cols-3 gap-6">
        {creditPackages.map((pkg) => (
          <Card 
            key={pkg.id} 
            className={`relative transition-all hover:shadow-lg ${
              pkg.popular ? 'border-2 border-primary shadow-md' : ''
            }`}
          >
            {pkg.popular && (
              <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary">
                Best Value
              </Badge>
            )}
            
            <CardHeader className="text-center">
              <CardTitle className="text-xl">{pkg.name}</CardTitle>
              <CardDescription>{pkg.description}</CardDescription>
            </CardHeader>

            <CardContent className="text-center space-y-4">
              {/* Credit amount */}
              <div>
                <div className="text-3xl font-bold text-primary mb-1">
                  {pkg.credits}
                </div>
                <div className="text-sm text-muted-foreground">Credits</div>
              </div>

              {/* Price display - enhanced */}
              <div>
                <div className="flex items-center justify-center gap-3 mb-3">
                  {/* Discounted price */}
                  <div className="relative">
                    <span className="text-3xl font-black text-green-600 drop-shadow-lg">
                      ${pkg.price}
                    </span>
                    {/* Blinking effect */}
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
                  </div>
                  
                  {/* Original price */}
                  <span className="text-xl text-muted-foreground line-through decoration-2 decoration-red-500">
                    ${pkg.originalPrice}
                  </span>
                  
                  {/* Discount label */}
                  <Badge variant="destructive" className="text-sm font-bold animate-pulse shadow-lg">
                    <Flame className="w-3 h-3 mr-1" />
                    {pkg.discount}% OFF
                  </Badge>
                </div>
                
                {/* Value description */}
                <div className="bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded p-2 mb-2">
                  <p className="text-xs text-green-700 dark:text-green-300 font-medium">
                    ${pkg.pricePerCredit.toFixed(3)} per credit • Great Value
                  </p>
                </div>
                
                {/* Savings amount */}
                <div className="bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800 rounded p-2">
                  <p className="text-xs text-orange-700 dark:text-orange-300 font-medium">
                    🔥 Save ${(pkg.originalPrice - pkg.price).toFixed(2)}!
                  </p>
                </div>
              </div>

              {/* Value comparison */}
              <div className="bg-muted/50 p-3 rounded-lg">
                <div className="flex items-center justify-center gap-1 text-sm">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span>Save ${(pkg.originalPrice - pkg.price).toFixed(2)} compared to individual purchase</span>
                </div>
              </div>
            </CardContent>

            <CardFooter>
              <Button 
                className="w-full" 
                onClick={() => handlePurchase(pkg.id)}
                disabled={isProcessing && selectedPackage === pkg.id}
              >
                {isProcessing && selectedPackage === pkg.id ? (
                  'Processing...'
                ) : (
                  `Buy ${pkg.credits} Credits`
                )}
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      {/* Credit usage instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Credit Usage Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span>FREE Analysis</span>
            <span className="font-medium">1 credit/time</span>
          </div>
          <div className="flex justify-between">
            <span>STARTER Analysis</span>
            <span className="font-medium">2 credits/time</span>
          </div>
          <div className="flex justify-between">
            <span>PRO Analysis</span>
            <span className="font-medium">3 credits/time</span>
          </div>
          <div className="pt-2 border-t">
            <p className="text-muted-foreground">
              • Purchased credits are valid for 6 months<br/>
              • Credit consumption priority: Expiring credits → Purchased credits → Subscription credits
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default CreditsPurchase;
