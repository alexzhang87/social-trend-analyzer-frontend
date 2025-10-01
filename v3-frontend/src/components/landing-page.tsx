/**
 * IMPORTANT UI LANGUAGE REQUIREMENT:
 * ALL user-facing text in this component MUST be in English.
 * This includes: titles, descriptions, placeholders, button text, error messages, etc.
 * 重要提醒：此组件中所有面向用户的文本必须使用英文！
 */

import { useState } from "react";
import { Header } from "./header";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, TrendingUp, Target, Zap, BarChart3, Users, Lightbulb, Search, ArrowRight, CheckCircle, DollarSign, Star, Shield, Globe, Brain, Rocket, Award, ChevronRight, Clock, Database, Mail, Lock, Eye, EyeOff, MessageCircle, Send, Activity, Leaf } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
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
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState("");
  const [chatMessage, setChatMessage] = useState("");
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
    
    navigate(`/analysis?mode=${mode}&keyword=${encodeURIComponent(keyword)}`);
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

  const handleChatSubmit = () => {
    if (!chatMessage.trim()) {
      toast({
        title: "Please enter a message",
        description: "Please enter your question or business idea",
        variant: "destructive",
      });
      return;
    }

    if (isAuthenticated) {
      // 导航到AI专家咨询页面
      navigate('/ai-expert-consultation');
    } else {
      setIsSignupOpen(true);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Enhanced Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-secondary/8 to-accent/10" />
        <div className="absolute inset-0 bg-gradient-to-t from-background/50 to-transparent" />
        
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

            {/* Main heading with gradient text */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl md:text-6xl lg:text-7xl font-bold mb-10 leading-loose py-2 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent"
            >
              Multi-Agent Market Research
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-lg md:text-xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              AI analyzes social signals, competitors, and trends to deliver instant market validation reports.
            </motion.p>

            {/* AI Chat Input - Chat Page Style */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="max-w-4xl mx-auto mb-16"
            >


              {/* Chat Input Box */}
              <div className="w-full max-w-3xl mx-auto">
                <div className="relative bg-white rounded-2xl shadow-xl border border-gray-200 p-6">
                  <textarea
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleChatSubmit())}
                    placeholder="Message IdeaEden..."
                    className="w-full px-6 py-3 pr-14 border-0 bg-transparent resize-none focus:outline-none text-gray-900 placeholder-gray-500 text-lg"
                    rows={1}
                    style={{ 
                      minHeight: '48px', 
                      maxHeight: '96px',
                      fontSize: '18px',
                      lineHeight: '1.4'
                    }}
                  />
                  <button
                    onClick={handleChatSubmit}
                    disabled={!chatMessage.trim()}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-400 text-white rounded-full flex items-center justify-center hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed w-10 h-10"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Feature Buttons */}
              <div className="w-full max-w-3xl mx-auto mt-4">
                <div className="flex gap-2 justify-center">
                  <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                    <span>🔍</span>
                    <span>Keyword Analysis</span>
                  </button>
                  <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                    <span>🎯</span>
                    <span>PMF Evaluation</span>
                  </button>
                  <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                    <span>📊</span>
                    <span>Market Dashboard</span>
                  </button>
                  <button className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-colors">
                    <span>📈</span>
                    <span>Analysis Reports</span>
                  </button>
                </div>
              </div>
            </motion.div>


          </div>
        </div>
      </section>

      {/* Core Features */}
      <section className="py-20 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              How It Works
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground max-w-2xl mx-auto"
            >
              Three simple steps to validate your business idea
            </motion.p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="group relative h-full"
            >
              <div className="relative bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300 h-full flex flex-col">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Search className="w-8 h-8 text-primary" />
                </div>
                
                <h3 className="text-xl font-bold text-foreground mb-4">
                  Enter Your Idea
                </h3>
                
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Simply describe your business idea or enter keywords. Our AI understands context and intent.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="group relative h-full"
            >
              <div className="relative bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300 h-full flex flex-col">
                <div className="w-16 h-16 bg-secondary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Brain className="w-8 h-8 text-secondary" />
                </div>
                
                <h3 className="text-xl font-bold text-foreground mb-4">
                  AI Analysis
                </h3>
                
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Multi-agent AI analyzes social signals, competitors, and market trends across platforms in real-time.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="group relative h-full"
            >
              <div className="relative bg-card border border-border rounded-2xl p-8 text-center hover:shadow-lg transition-all duration-300 h-full flex flex-col">
                <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <BarChart3 className="w-8 h-8 text-accent" />
                </div>
                
                <h3 className="text-xl font-bold text-foreground mb-4">
                  Get Report
                </h3>
                
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Receive instant market validation report with actionable insights and recommendations.
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Data Sources */}
      <section className="py-20 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              Multi-Platform Data Sources
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground max-w-2xl mx-auto"
            >
              Access <span className="text-primary font-semibold">real-time data</span> and <span className="text-secondary font-semibold">authentic user reviews</span> from leading platforms for comprehensive market validation
            </motion.p>
          </div>

          {/* Platform Cards Grid */}
          <div className="relative">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-secondary/5 rounded-3xl"></div>
            
            {/* Cards Container */}
            <div className="relative bg-card/50 backdrop-blur-sm border border-border/50 rounded-3xl p-8">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-7xl mx-auto">
                {/* X (Twitter) */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/50 dark:to-blue-900/50 border border-blue-200 dark:border-blue-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">X (Twitter)</h3>
                    <p className="text-muted-foreground text-sm">Real-time conversations</p>
                  </div>
                </motion.div>

                {/* Facebook */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950/50 dark:to-indigo-900/50 border border-blue-200 dark:border-blue-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">Facebook</h3>
                    <p className="text-muted-foreground text-sm">Social engagement data</p>
                  </div>
                </motion.div>

                {/* Instagram */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-pink-50 to-purple-100 dark:from-pink-950/50 dark:to-purple-900/50 border border-pink-200 dark:border-pink-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-gradient-to-br from-pink-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">Instagram</h3>
                    <p className="text-muted-foreground text-sm">Visual content trends</p>
                  </div>
                </motion.div>

                {/* LinkedIn */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.4 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-blue-50 to-cyan-100 dark:from-blue-950/50 dark:to-cyan-900/50 border border-blue-200 dark:border-blue-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">LinkedIn</h3>
                    <p className="text-muted-foreground text-sm">Professional insights</p>
                  </div>
                </motion.div>

                {/* TikTok */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.5 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950/50 dark:to-gray-900/50 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-gray-900 dark:bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white dark:text-gray-900" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">TikTok</h3>
                    <p className="text-muted-foreground text-sm">Viral content patterns</p>
                  </div>
                </motion.div>

                {/* Reddit */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.6 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-orange-50 to-red-100 dark:from-orange-950/50 dark:to-red-900/50 border border-orange-200 dark:border-orange-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">Reddit</h3>
                    <p className="text-muted-foreground text-sm">Community discussions</p>
                  </div>
                </motion.div>

                {/* Product Hunt */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.7 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-orange-50 to-yellow-100 dark:from-orange-950/50 dark:to-yellow-900/50 border border-orange-200 dark:border-orange-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300">
                      <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M13.604 8.4h-3.405V12h3.405c.995 0 1.801-.806 1.801-1.801 0-.993-.805-1.799-1.801-1.799zM12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zm1.604 14.4h-3.405V18H7.801V6h5.803c2.319 0 4.199 1.881 4.199 4.199s-1.88 4.201-4.199 4.201z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">Product Hunt</h3>
                    <p className="text-muted-foreground text-sm">Product launches</p>
                  </div>
                </motion.div>

                {/* Google Trends */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.8 }}
                  className="group relative"
                >
                  <div className="bg-gradient-to-br from-blue-50 to-green-100 dark:from-blue-950/50 dark:to-green-900/50 border border-blue-200 dark:border-blue-800 rounded-2xl p-6 text-center hover:shadow-xl hover:scale-105 transition-all duration-300">
                    <div className="w-14 h-14 bg-white dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-6 transition-transform duration-300 shadow-lg border border-gray-200 dark:border-gray-700">
                      <svg className="w-8 h-8" viewBox="0 0 48 48">
                        <title>Google Logo</title>
                        <clipPath id="g">
                          <path d="M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z"/>
                        </clipPath>
                        <g className="colors" clipPath="url(#g)">
                          <path fill="#FBBC05" d="M0 37V11l17 13z"/>
                          <path fill="#EA4335" d="M0 11l17 13 7-6.1L48 14V0H0z"/>
                          <path fill="#34A853" d="M0 37l30-23 7.9 1L48 0v48H0z"/>
                          <path fill="#4285F4" d="M48 48L17 24l-4-3 35-10z"/>
                        </g>
                      </svg>
                    </div>
                    <h3 className="text-lg font-bold text-foreground mb-2">Google Trends</h3>
                    <p className="text-muted-foreground text-sm">Search patterns</p>
                  </div>
                </motion.div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-16 bg-muted/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              Trusted by Innovators Globally
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground"
            >
              Join thousands of entrepreneurs who've validated their ideas with our AI
            </motion.p>
          </div>

          <div className="grid md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl lg:text-6xl font-bold text-primary mb-2">10K+</div>
              <div className="text-base text-muted-foreground">Ideas Validated</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl lg:text-6xl font-bold text-secondary mb-2">5K+</div>
              <div className="text-base text-muted-foreground">Active Users</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl lg:text-6xl font-bold text-accent mb-2">85%</div>
              <div className="text-base text-muted-foreground">Success Rate</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-center"
            >
              <div className="text-4xl md:text-5xl lg:text-6xl font-bold text-primary mb-2">2min</div>
              <div className="text-base text-muted-foreground">Average Analysis</div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-background">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl md:text-4xl font-bold text-foreground mb-4"
            >
              Frequently Asked Questions
            </motion.h2>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-lg text-muted-foreground"
            >
              Everything you need to know about our AI-powered market validation
            </motion.p>
          </div>

          <div className="space-y-4">
            {[
              {
                question: "How accurate is the AI market analysis?",
                answer: "Our multi-agent AI system analyzes real-time data from multiple platforms with 85%+ accuracy rate, validated against actual market outcomes from thousands of startups."
              },
              {
                question: "What data sources do you use?",
                answer: "We analyze data from X (Twitter), Reddit, Product Hunt, Google Trends, and other leading platforms to provide comprehensive market insights and competitor analysis."
              },
              {
                question: "How long does the analysis take?",
                answer: "Most analyses are completed within 2-5 minutes. Complex market research that traditionally takes weeks can now be done in minutes with our AI agents."
              },
              {
                question: "Can I validate any type of business idea?",
                answer: "Yes! Our AI works across all industries and business models - from SaaS and e-commerce to physical products and services. The more specific your idea, the better insights you'll get."
              }
            ].map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 + index * 0.1 }}
                className="bg-card border border-border rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => {
                    const content = document.getElementById(`faq-content-${index}`);
                    const icon = document.getElementById(`faq-icon-${index}`);
                    if (content && icon) {
                      const isOpen = content.style.maxHeight && content.style.maxHeight !== '0px';
                      if (isOpen) {
                        content.style.maxHeight = '0px';
                        content.style.opacity = '0';
                        icon.style.transform = 'rotate(0deg)';
                      } else {
                        content.style.maxHeight = content.scrollHeight + 'px';
                        content.style.opacity = '1';
                        icon.style.transform = 'rotate(45deg)';
                      }
                    }
                  }}
                  className="w-full p-6 text-left flex items-center justify-between hover:bg-muted/50 transition-colors"
                >
                  <h3 className="text-lg font-semibold text-foreground">
                    {faq.question}
                  </h3>
                  <div
                    id={`faq-icon-${index}`}
                    className="w-6 h-6 flex items-center justify-center text-2xl font-light text-muted-foreground transition-transform duration-300"
                    style={{ transform: 'rotate(0deg)' }}
                  >
                    +
                  </div>
                </button>
                <div
                  id={`faq-content-${index}`}
                  className="overflow-hidden transition-all duration-300 ease-in-out"
                  style={{ maxHeight: '0px', opacity: '0' }}
                >
                  <div className="px-6 pb-6">
                    <p className="text-muted-foreground">
                      {faq.answer}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* See Your Idea's Potential - DISABLED */}
      {/*
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

            <div className="grid md:grid-cols-2 gap-8 mb-8">
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
      */}



      {/* CTA Section - Disabled */}
      {/*
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
                onClick={() => isAuthenticated ? navigate('/pricing') : setIsSignupOpen(true)}
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
      */}

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

      {/* Footer */}
      <footer className="bg-muted/30 border-t border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="col-span-1">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-lg flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-foreground">IdeaEden</span>
              </div>
              <p className="text-muted-foreground text-sm">
                AI-powered startup idea validation platform helping entrepreneurs make data-driven decisions.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-foreground mb-4">Product</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Market Analysis</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Competitor Research</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">PMF Evaluation</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Pricing</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-foreground mb-4">Resources</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">Documentation</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">API Reference</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Case Studies</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Blog</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-foreground mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#" className="hover:text-foreground transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-foreground transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-border mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-muted-foreground">
              © 2024 IdeaEden. All rights reserved.
            </p>
            <div className="flex items-center gap-4 mt-4 md:mt-0">
              <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </a>
              <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"/>
                </svg>
              </a>
              <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}