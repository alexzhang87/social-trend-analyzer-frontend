import { useState } from "react";
import { Leaf, ArrowRight, Mail, Lock, Eye, EyeOff } from "lucide-react";
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
import { useAuth } from "@/components/auth-provider";
import { toast } from "@/hooks/use-toast";
import { Link } from "react-router-dom";

export function Header() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSignupOpen, setIsSignupOpen] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: "", password: "" });
  const [signupForm, setSignupForm] = useState({ email: "", password: "", verificationCode: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isCodeSent, setIsCodeSent] = useState(false);
  const [isSendingCode, setIsSendingCode] = useState(false);
  
  const { login, register, isAuthenticated, user, logout } = useAuth();

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

    setIsSendingCode(true);
    try {
      // TODO: Should call backend API to send verification code
      // Temporarily simulate successful sending
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setIsCodeSent(true);
      toast({
        title: "Verification Code Sent",
        description: "Please check your email for the verification code",
      });
    } catch (error) {
      toast({
        title: "Failed to Send Code",
        description: "Please try again later",
        variant: "destructive",
      });
    } finally {
      setIsSendingCode(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isCodeSent) {
      toast({
        title: "Verification Required",
        description: "Please send and enter verification code first",
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
      // TODO: Should verify verification code here
      // Temporarily simulate successful verification
      
      // Extract username from email (part before @)
      const username = signupForm.email.split('@')[0];
      await register(signupForm.email, username, signupForm.password);
      setIsSignupOpen(false);
      setSignupForm({ email: "", password: "", verificationCode: "" });
      setIsCodeSent(false);
      toast({
        title: "Registration Successful",
        description: "Welcome to IdeaEden!",
      });
    } catch (error) {
      toast({
        title: "Registration Failed",
        description: "Please check your information or try again later",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast({
      title: "Logged Out",
      description: "Thank you for using our service!",
    });
  };

  return (
    <header className="border-b border-border/20 bg-background/80 backdrop-blur-sm sticky top-0 z-40">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <a href="#" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-400 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              IdeaEden
            </span>
          </a>
          
          <nav className="hidden md:flex items-center space-x-8">
            {/* Navigation links removed as per user request */}
          </nav>

          <div className="flex items-center space-x-2">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-muted-foreground">Welcome, {user?.email}</span>
                <Link to="/workspace" className="text-sm px-3 py-2 rounded border border-border/30 hover:bg-accent/10 transition-colors">
                  Workspace
                </Link>
                <Button variant="outline" onClick={handleLogout} className="border-border/30 hover:bg-accent/10">
                  Logout
                </Button>
              </div>
            ) : (
              <>
                <Link to="/workspace" className="text-sm px-3 py-2 rounded border border-border/30 hover:bg-accent/10 transition-colors text-muted-foreground hover:text-foreground">
                  Workspace
                </Link>
                <Link to="/pricing" className="text-sm px-3 py-2 rounded border border-border/30 hover:bg-accent/10 transition-colors text-muted-foreground hover:text-foreground">
                  Pricing
                </Link>
                <Dialog open={isLoginOpen} onOpenChange={setIsLoginOpen}>
                  <DialogTrigger asChild>
                    <Button variant="link" className="hidden sm:inline-flex text-muted-foreground hover:text-foreground">
                      Log In
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <form onSubmit={handleLogin}>
                      <DialogHeader>
                        <DialogTitle>Welcome Back</DialogTitle>
                        <DialogDescription>
                          Log in to access your dashboard and saved analyses.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid w-full items-center gap-1.5">
                          <Label htmlFor="email-login">Email</Label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input 
                              type="email" 
                              id="email-login" 
                              placeholder="you@company.com" 
                              className="pl-10"
                              value={loginForm.email}
                              onChange={(e) => setLoginForm(prev => ({ ...prev, email: e.target.value }))}
                              required
                            />
                          </div>
                        </div>
                        <div className="grid w-full items-center gap-1.5">
                          <Label htmlFor="password-login">Password</Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input 
                              type={showPassword ? "text" : "password"} 
                              id="password-login" 
                              placeholder="••••••••" 
                              className="pl-10 pr-10"
                              value={loginForm.password}
                              onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
                              required
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                            >
                              {showPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </button>
                          </div>
                          <div className="text-right mt-1">
                            <button
                              type="button"
                              onClick={() => {
                                toast({
                                  title: "Forgot Password",
                                  description: "Please contact support to reset your password.",
                                });
                              }}
                              className="text-sm text-teal-600 hover:text-teal-700 underline"
                            >
                              Forgot your password?
                            </button>
                          </div>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button 
                          type="submit" 
                          className="w-full bg-teal-600 hover:bg-teal-700" 
                          disabled={isLoading}
                        >
                          {isLoading ? "Logging in..." : "Log In"}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>

                <Dialog open={isSignupOpen} onOpenChange={setIsSignupOpen}>
                  <DialogTrigger asChild>
                    <Button className="bg-teal-600 hover:bg-teal-700 text-white group">
                      Sign Up
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <form onSubmit={handleSignup}>
                      <DialogHeader>
                        <DialogTitle>Create an Account</DialogTitle>
                        <DialogDescription>
                          Welcome to IdeaEden. Let's find your next great business idea.
                        </DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid w-full items-center gap-1.5">
                          <Label htmlFor="email-signup">Email</Label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input 
                              type="email" 
                              id="email-signup" 
                              placeholder="you@company.com" 
                              className="pl-10"
                              value={signupForm.email}
                              onChange={(e) => setSignupForm(prev => ({ ...prev, email: e.target.value }))}
                              required
                            />
                          </div>
                        </div>
                        <div className="grid w-full items-center gap-1.5">
                          <Label htmlFor="password-signup">Password</Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input 
                              type="password" 
                              id="password-signup" 
                              placeholder="Create a strong password" 
                              className="pl-10"
                              value={signupForm.password}
                              onChange={(e) => setSignupForm(prev => ({ ...prev, password: e.target.value }))}
                              required
                            />
                          </div>
                        </div>
                        <div className="grid w-full items-center gap-1.5">
                          <Label htmlFor="verification-code">Verification Code</Label>
                          <div className="flex gap-2">
                            <Input 
                              type="text" 
                              id="verification-code" 
                              placeholder="Enter verification code" 
                              value={signupForm.verificationCode}
                              onChange={(e) => setSignupForm(prev => ({ ...prev, verificationCode: e.target.value }))}
                              required
                              disabled={!isCodeSent}
                            />
                            <Button
                              type="button"
                              variant="outline"
                              onClick={handleSendVerificationCode}
                              disabled={isSendingCode || !signupForm.email}
                              className="whitespace-nowrap"
                            >
                              {isSendingCode ? "Sending..." : isCodeSent ? "Resend" : "Send Code"}
                            </Button>
                          </div>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button 
                          type="submit" 
                          className="w-full bg-teal-600 hover:bg-teal-700" 
                          disabled={isLoading}
                        >
                          {isLoading ? "Signing up..." : "Sign Up & Analyze"}
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
