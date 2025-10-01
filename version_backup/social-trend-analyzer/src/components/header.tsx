import { useState } from "react";
import { Leaf, ArrowRight, Mail, Lock } from "lucide-react";
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
  const [signupForm, setSignupForm] = useState({ email: "", password: "" });
  const [isLoading, setIsLoading] = useState(false);
  
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

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Extract username from email (part before @)
      const username = signupForm.email.split('@')[0];
      await register(signupForm.email, username, signupForm.password);
      setIsSignupOpen(false);
      setSignupForm({ email: "", password: "" });
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
            <span className="text-xl font-bold text-white">
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
                              type="password" 
                              id="password-login" 
                              placeholder="••••••••" 
                              className="pl-10"
                              value={loginForm.password}
                              onChange={(e) => setLoginForm(prev => ({ ...prev, password: e.target.value }))}
                              required
                            />
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
                      Get Started Free
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
