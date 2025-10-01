"use client"

import { useState } from "react";
import { Header } from "./header";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/hooks/use-toast";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, TrendingUp, Target, Zap, BarChart3, Users, Lightbulb, Search, ArrowRight, CheckCircle, DollarSign, Star, Shield, Globe, Brain, Rocket, Award, ChevronRight, Clock, Database, Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter
} from 'recharts';

export default function LandingPage() {
  const { user, isAuthenticated, login, register } = useAuth();
  const { toast } = useToast();
  const router = useRouter();
  const [keyword, setKeyword] = useState("");
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSignupOpen, setIsSignupOpen] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [signupForm, setSignupForm] = useState({ email: "", password: "", verificationCode: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isCodeSent, setIsCodeSent] = useState(false);
  const [isSendingCode, setIsSendingCode] = useState(false);

  const handleModeSelect = (mode: 'quick' | 'professional', keyword: string) => {
    if (!keyword.trim()) {
      toast({
        title: "Please enter a keyword",
        description: "Enter a business idea or keyword to analyze",
        variant: "destructive",
      });
      return;
    }
    
    router.push(`/analysis?mode=${mode}&keyword=${encodeURIComponent(keyword)}`);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await login(loginForm.email, loginForm.password);
      setIsLoginOpen(false);
      setLoginForm({ email: "", password: "" });
      toast({
        title: "Login Successful",
        description: "Welcome back!",
      });
    } catch (error) {
      toast({
        title: "Login Failed",
        description: "Please check your email and password",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendVerificationCode = async () => {
    if (!signupForm.email) {
      toast({
        title: "Email Required",
        description: "Please enter your email address first",
        variant: "destructive",
      });
      return;
    }

    if (!/\S+@\S+\.\S+/.test(signupForm.email)) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address",
        variant: "destructive",
      });
      return;
    }

    setIsSendingCode(true);
    
    // Simulate sending verification code
    setTimeout(() => {
      setIsSendingCode(false);
      setIsCodeSent(true);
      toast({
        title: "Verification Code Sent",
        description: "Please check your email for the verification code",
      });
    }, 2000);
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isCodeSent) {
      toast({
        title: "Verification Required",
        description: "Please send and enter the verification code first",
        variant: "destructive",
      });
      return;
    }

    if (!signupForm.verificationCode) {
      toast({
        title: "Verification Code Required",
        description: "Please enter the verification code",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    try {
      // Simulate verification code validation
      if (signupForm.verificationCode !== "123456") {
        throw new Error("Invalid verification code");
      }

      await register(signupForm.email, signupForm.password);
      setIsSignupOpen(false);
      setSignupForm({ email: "", password: "", verificationCode: "" });
      setIsCodeSent(false);
      toast({
        title: "Registration Successful",
        description: "Welcome! Your account has been created.",
      });
    } catch (error) {
      toast({
        title: "Registration Failed",
        description: "Please check your information and try again",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAnalysis = () => {
    if (isAuthenticated) {
      if (keyword.trim()) {
        handleModeSelect('quick', keyword);
      } else {
        toast({
          title: "Please enter a keyword",
          description: "Enter a business idea or keyword to analyze",
          variant: "destructive",
        });
      }
    } else {
      setIsSignupOpen(true);
    }
  };

  const handleProfessionalAnalysis = () => {
    if (isAuthenticated) {
      if (keyword.trim()) {
        handleModeSelect('professional', keyword);
      } else {
        toast({
          title: "Please enter a keyword",
          description: "Enter a business idea or keyword to analyze",
          variant: "destructive",
        });
      }
    } else {
      setIsSignupOpen(true);
    }
  };

  const handleSearchClick = () => {
    if (!keyword.trim()) {
      toast({
        title: "Please enter a keyword",
        description: "Enter a business idea or keyword to analyze",
        variant: "destructive",
      });
      return;
    }

    if (isAuthenticated) {
      handleModeSelect('quick', keyword);
    } else {
      setIsSignupOpen(true);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <div className="text-center">
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-8"
            >
              <Sparkles className="w-4 h-4" />
              AI-Powered Startup Idea Validation Platform
            </motion.div>

            {/* Main heading */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground mb-6 leading-tight"
            >
              Validate Startup Ideas with Data
              <span className="block bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                Not Guesswork
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg md:text-xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              2-minute quick validation vs traditional 6-month research, save $50,000+ consulting fees.
              AI-driven multi-source data analysis, providing 80% of Brandwatch functionality at 20% of the price.
            </motion.p>

            {/* Search Input */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="max-w-2xl mx-auto mb-16"
            >
              <div className="relative">
                <input
                  type="text"
                  placeholder="Enter your product or service keyword..."
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  onClick={handleSearchClick}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearchClick()}
                  className="w-full px-6 py-4 text-lg rounded-2xl border border-border bg-card/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-200 cursor-pointer"
                />
                <button
                  type="button"
                  onClick={handleSearchClick}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-primary/10 rounded-full transition-colors"
                >
                  <Zap className="w-5 h-5 text-primary" />
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Choose Your Analysis Mode */}
      <section className="py-20 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              Choose Your Analysis Mode
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground max-w-2xl mx-auto"
            >
              Select the right analysis depth for your needs
            </motion.p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Quick Analysis Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="group relative h-full"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary rounded-2xl opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
              <div className="relative bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300 h-full flex flex-col">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Zap className="w-8 h-8 text-primary" />
                </div>
                
                <h3 className="text-2xl font-bold text-foreground mb-4">
                  Quick Validation
                </h3>
                
                <p className="text-muted-foreground mb-6 text-sm leading-relaxed">
                  Lightning-fast market validation for rapid idea screening. Get essential insights in 2 minutes vs traditional 6-month research cycles.
                </p>
                
                <div className="bg-primary/5 border border-primary/20 rounded-lg p-3 mb-6">
                  <div className="flex items-center mb-1">
                    <Zap className="w-4 h-4 text-primary mr-2" />
                    <span className="text-sm font-medium text-primary">Perfect for: Initial Screening</span>
                  </div>
                  <p className="text-xs text-primary/80">Save $10,000+ in market research costs</p>
                </div>
                
                <div className="flex-grow">
                  <ul className="text-muted-foreground mb-8 space-y-3 text-left">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Instant market size estimation</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Basic competitor landscape scan</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>AI-powered viability score</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Critical risk alerts</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Social sentiment snapshot</span>
                    </li>
                  </ul>
                </div>

                <button
                  onClick={handleQuickAnalysis}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-6 rounded-xl transition-colors duration-200 mt-auto flex items-center justify-center gap-2"
                >
                  <Zap className="w-4 h-4" />
                  Start Quick Analysis
                </button>
              </div>
            </motion.div>

            {/* Professional Analysis Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="group relative h-full"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-secondary to-accent rounded-2xl opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
              <div className="relative bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300 h-full flex flex-col">
                <div className="w-16 h-16 bg-secondary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Target className="w-8 h-8 text-secondary" />
                </div>
                
                <h3 className="text-2xl font-bold text-foreground mb-4">
                  Professional Analysis
                </h3>
                
                <p className="text-muted-foreground mb-6 text-sm leading-relaxed">
                  Enterprise-grade analysis with multi-source data integration. Get Brandwatch-level insights at 20% of the cost for serious entrepreneurs.
                </p>
                
                <div className="bg-secondary/5 border border-secondary/20 rounded-lg p-3 mb-6">
                  <div className="flex items-center mb-1">
                    <Target className="w-4 h-4 text-secondary mr-2" />
                    <span className="text-sm font-medium text-secondary">Perfect for: Investment Readiness</span>
                  </div>
                  <p className="text-xs text-secondary/80">Replace $50,000+ consulting fees</p>
                </div>
                
                <div className="flex-grow">
                  <ul className="text-muted-foreground mb-8 space-y-3 text-left">
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Multi-platform data aggregation (Reddit, Twitter, News)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Advanced competitor intelligence & positioning</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>PMF probability scoring with confidence intervals</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Strategic go-to-market recommendations</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full mt-2 flex-shrink-0"></div>
                      <span>Investment pitch-ready data package</span>
                    </li>
                  </ul>
                </div>

                <button
                  onClick={handleProfessionalAnalysis}
                  className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground font-semibold py-3 px-6 rounded-xl transition-colors duration-200 mt-auto flex items-center justify-center gap-2"
                >
                  <Target className="w-4 h-4" />
                  Start Professional Analysis
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* See Your Idea's Potential */}
      <section className="py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              See Your Idea's Potential
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground max-w-2xl mx-auto"
            >
              Real-time data-driven market insights with advanced visualization
            </motion.p>
          </div>

          {/* Mock Dashboard */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="bg-card border border-border rounded-3xl p-8 shadow-lg"
          >
            <div className="flex items-center gap-3 mb-8">
              <BarChart3 className="w-6 h-6 text-primary" />
              <h3 className="text-xl font-bold text-foreground">Market Analysis Dashboard</h3>
            </div>

            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="bg-primary/5 border border-primary/20 rounded-2xl p-6 text-center">
                <div className="text-3xl font-bold text-primary mb-2">85%</div>
                <div className="text-sm text-muted-foreground">Market Potential</div>
              </div>
              
              <div className="bg-secondary/5 border border-secondary/20 rounded-2xl p-6 text-center">
                <div className="text-3xl font-bold text-secondary mb-2">$2.5M</div>
                <div className="text-sm text-muted-foreground">Estimated Market Size</div>
              </div>
              
              <div className="bg-accent/5 border border-accent/20 rounded-2xl p-6 text-center">
                <div className="text-3xl font-bold text-accent mb-2">72%</div>
                <div className="text-sm text-muted-foreground">Success Probability</div>
              </div>
            </div>

            {/* Charts Grid */}
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              {/* Market Trend Chart */}
              <div className="bg-muted/30 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-primary" />
                  <h4 className="font-semibold text-foreground">Market Growth Trend</h4>
                </div>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={[
                      { month: 'Jan', value: 45 },
                      { month: 'Feb', value: 58 },
                      { month: 'Mar', value: 75 },
                      { month: 'Apr', value: 68 },
                      { month: 'May', value: 85 },
                      { month: 'Jun', value: 92 },
                      { month: 'Jul', value: 88 },
                      { month: 'Aug', value: 95 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
                      <YAxis stroke="hsl(var(--muted-foreground))" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }} 
                      />
                      <Line 
                        type="cardinal" 
                        dataKey="value" 
                        stroke="hsl(var(--primary))" 
                        strokeWidth={3}
                        dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
                        tension={0.4}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Competition Analysis */}
              <div className="bg-muted/30 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Users className="w-5 h-5 text-secondary" />
                  <h4 className="font-semibold text-foreground">Competitive Landscape</h4>
                </div>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart data={[
                      { x: 20, y: 30, name: 'Competitor A', size: 400 },
                      { x: 40, y: 60, name: 'Competitor B', size: 300 },
                      { x: 70, y: 80, name: 'Your Opportunity', size: 200 },
                      { x: 85, y: 45, name: 'Market Leader', size: 600 },
                      { x: 60, y: 25, name: 'Competitor C', size: 250 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="x" name="Market Share" stroke="hsl(var(--muted-foreground))" />
                      <YAxis dataKey="y" name="Innovation" stroke="hsl(var(--muted-foreground))" />
                      <Tooltip 
                        cursor={{ strokeDasharray: '3 3' }}
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }}
                      />
                      <Scatter dataKey="size" fill="hsl(var(--secondary))" />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Revenue Projection */}
              <div className="bg-muted/30 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <BarChart3 className="w-5 h-5 text-accent" />
                  <h4 className="font-semibold text-foreground">Revenue Forecast</h4>
                </div>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[
                      { year: 'Year 1', conservative: 50000, optimistic: 120000 },
                      { year: 'Year 2', conservative: 150000, optimistic: 350000 },
                      { year: 'Year 3', conservative: 400000, optimistic: 800000 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="year" stroke="hsl(var(--muted-foreground))" />
                      <YAxis stroke="hsl(var(--muted-foreground))" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }}
                        formatter={(value) => [`$${value.toLocaleString()}`, '']}
                      />
                      <Bar dataKey="conservative" fill="hsl(var(--accent))" name="Conservative" />
                      <Bar dataKey="optimistic" fill="hsl(var(--primary))" name="Optimistic" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* PMF Metrics */}
              <div className="bg-muted/30 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="w-5 h-5 text-primary" />
                  <h4 className="font-semibold text-foreground">PMF Score Breakdown</h4>
                </div>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={[
                          { name: 'Market Need', value: 85, fill: 'hsl(var(--primary))' },
                          { name: 'Solution Fit', value: 78, fill: 'hsl(var(--secondary))' },
                          { name: 'Monetization', value: 72, fill: 'hsl(var(--accent))' },
                          { name: 'Competition', value: 68, fill: 'hsl(var(--muted))' }
                        ]}
                        cx="50%"
                        cy="50%"
                        outerRadius={60}
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}%`}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--card))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }}
                      />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="bg-muted/30 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-5 h-5 text-accent" />
                <h4 className="font-semibold text-foreground">AI-Generated Key Insights</h4>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-muted-foreground">Strong target market demand with 35% growth rate</p>
                    <p className="text-xs text-muted-foreground/70 mt-1">Based on search volume and social sentiment analysis</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-secondary rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-muted-foreground">Competitive analysis reveals market gap opportunities</p>
                    <p className="text-xs text-muted-foreground/70 mt-1">3 key differentiators identified for positioning</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-accent rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-muted-foreground">Clear user pain points with high solution fit</p>
                    <p className="text-xs text-muted-foreground/70 mt-1">92% problem-solution match score</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2"></div>
                  <div>
                    <p className="text-sm text-muted-foreground">Monetization potential: $89 average monthly willingness to pay</p>
                    <p className="text-xs text-muted-foreground/70 mt-1">Survey data from 1,200+ target users</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              AI-Powered Market Intelligence Platform
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground max-w-3xl mx-auto"
            >
              Advanced AI models analyze real-time data from multiple channels to deliver unparalleled market insights and PMF evaluation
            </motion.p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300"
            >
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Brain className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-4 leading-tight">
                AI-Powered Market Analysis
              </h3>
              <p className="text-muted-foreground mb-4 leading-relaxed text-sm">
                Intelligent analysis engine that processes market data, consumer feedback, and startup trends. 
                Helps identify patterns and opportunities that might be missed in manual analysis.
              </p>
              <div className="text-sm text-primary font-semibold">
                Smart Analysis + Data Insights
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300"
            >
              <div className="w-16 h-16 bg-secondary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Database className="w-8 h-8 text-secondary" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-4 leading-tight">
                Multi-Platform Data Collection
              </h3>
              <p className="text-muted-foreground mb-4 leading-relaxed text-sm">
                Gather insights from X (Twitter), Reddit, Product Hunt, and Google Trends to understand 
                user discussions, feedback, and trending topics across different communities.
              </p>
              
              {/* Platform Logos */}
              <div className="flex justify-center gap-4 mb-4">
                {/* X (Twitter) Logo */}
                <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                  </svg>
                </div>
                
                {/* Reddit Logo */}
                <div className="w-10 h-10 bg-[#FF4500] rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
                  </svg>
                </div>
                
                {/* Product Hunt Logo */}
                <div className="w-10 h-10 bg-[#DA552F] rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M13.604 8.4h-3.405V12h3.405a1.8 1.8 0 0 0 0-3.6zM12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zm1.604 14.4h-3.405V18H7.801V6h5.803a4.2 4.2 0 1 1 0 8.4z"/>
                  </svg>
                </div>
                
                {/* Google Trends Logo */}
                <div className="w-10 h-10 bg-[#4285F4] rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M7.5 7.5L12 3l4.5 4.5v9L12 21l-4.5-4.5v-9zM12 5.5L9 8.5v7l3 3 3-3v-7l-3-3z"/>
                    <path d="M10.5 10.5h3v3h-3z"/>
                  </svg>
                </div>
              </div>
              
              <div className="text-sm text-secondary font-semibold">
                4+ Platforms · Regular Updates
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300"
            >
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <Target className="w-8 h-8 text-accent" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-4 leading-tight">
                PMF Assessment Framework
              </h3>
              <p className="text-muted-foreground mb-4 leading-relaxed text-sm">
                Comprehensive evaluation system analyzing key PMF indicators including market demand, competition landscape, 
                user sentiment, and business potential to guide your product decisions.
              </p>
              <div className="text-sm text-accent font-semibold">
                Data-Driven Insights
              </div>
            </motion.div>
          </div>

          {/* Competitive Advantages */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="bg-gradient-to-r from-primary/5 via-secondary/5 to-accent/5 rounded-3xl p-8 border border-border"
          >
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-foreground mb-4">
                Trusted by Innovators & Business Builders
              </h3>
              <p className="text-muted-foreground">
                Join creators, founders, and business owners who use our insights to validate and improve their ideas
              </p>
            </div>

            <div className="grid md:grid-cols-4 gap-6 text-center">
              <div className="bg-card/50 rounded-xl p-4 border border-border/50">
                <div className="text-2xl font-bold text-primary mb-2">300%</div>
                <div className="text-sm text-muted-foreground">Higher Success Rate</div>
              </div>
              <div className="bg-card/50 rounded-xl p-4 border border-border/50">
                <div className="text-2xl font-bold text-secondary mb-2">6 Months</div>
                <div className="text-sm text-muted-foreground">Time Saved</div>
              </div>
              <div className="bg-card/50 rounded-xl p-4 border border-border/50">
                <div className="text-2xl font-bold text-accent mb-2">$50K+</div>
                <div className="text-sm text-muted-foreground">Cost Savings</div>
              </div>
              <div className="bg-card/50 rounded-xl p-4 border border-border/50">
                <div className="text-2xl font-bold text-primary mb-2">24/7</div>
                <div className="text-sm text-muted-foreground">AI Analysis</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary/10 via-secondary/10 to-accent/10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="bg-card/80 backdrop-blur-sm border border-border rounded-3xl p-12 shadow-xl"
          >
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-6"
            >
              Ready to Validate Your Idea?
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto"
            >
              Join thousands of successful entrepreneurs who've turned their ideas into thriving businesses
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="flex justify-center"
            >
              <button
                onClick={() => isAuthenticated ? router.push('/pricing') : setIsSignupOpen(true)}
                className="group bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-4 px-8 rounded-xl transition-all duration-200 flex items-center justify-center gap-2"
              >
                Get Started Now
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="mt-8 flex items-center justify-center gap-6 text-sm text-muted-foreground"
            >
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-secondary" />
                <span>5-minute setup</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Login Dialog */}
      <Dialog open={isLoginOpen} onOpenChange={setIsLoginOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-center">Welcome Back</DialogTitle>
            <DialogDescription className="text-center text-muted-foreground">
              Sign in to your account to continue
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="login-email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  id="login-email"
                  type="email"
                  placeholder="Enter your email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                  className="pl-10"
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="login-password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  className="pl-10 pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="text-right">
              <button
                type="button"
                className="text-sm text-primary hover:underline"
                onClick={() => {
                  setIsLoginOpen(false);
                  // Add forgot password logic here
                }}
              >
                Forgot password?
              </button>
            </div>
            <DialogFooter className="flex-col space-y-2">
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Signing in..." : "Sign In"}
              </Button>
              <p className="text-sm text-center text-muted-foreground">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsLoginOpen(false);
                    setIsSignupOpen(true);
                  }}
                  className="text-primary hover:underline font-medium"
                >
                  Sign up
                </button>
              </p>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Signup Dialog */}
      <Dialog open={isSignupOpen} onOpenChange={setIsSignupOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-center">Create Account</DialogTitle>
            <DialogDescription className="text-center text-muted-foreground">
              Join us to start validating your startup ideas
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSignup} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="signup-email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  id="signup-email"
                  type="email"
                  placeholder="Enter your email"
                  value={signupForm.email}
                  onChange={(e) => setSignupForm({ ...signupForm, email: e.target.value })}
                  className="pl-10"
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="signup-password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  id="signup-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a password"
                  value={signupForm.password}
                  onChange={(e) => setSignupForm({ ...signupForm, password: e.target.value })}
                  className="pl-10 pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="verification-code">Verification Code</Label>
              <div className="flex gap-2">
                <Input
                  id="verification-code"
                  type="text"
                  placeholder="Enter verification code"
                  value={signupForm.verificationCode}
                  onChange={(e) => setSignupForm({ ...signupForm, verificationCode: e.target.value })}
                  disabled={!isCodeSent}
                  required
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleSendVerificationCode}
                  disabled={isSendingCode || isCodeSent}
                  className="whitespace-nowrap"
                >
                  {isSendingCode ? "Sending..." : isCodeSent ? "Sent" : "Send Code"}
                </Button>
              </div>
            </div>
            <DialogFooter className="flex-col space-y-2">
              <p className="text-sm text-center text-muted-foreground">
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignupOpen(false);
                    setIsLoginOpen(true);
                  }}
                  className="text-primary hover:underline font-medium"
                >
                  Sign in
                </button>
              </p>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Creating account..." : "Create Account"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}