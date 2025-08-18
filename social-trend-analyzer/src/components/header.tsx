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

export function Header() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isSignupOpen, setIsSignupOpen] = useState(false);

  return (
    <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-40">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <a href="#" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-400 rounded-lg flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              IdeaEden
            </span>
          </a>
          
          <nav className="hidden md:flex items-center space-x-8">
            {/* Navigation links removed as per user request */}
          </nav>

          <div className="flex items-center space-x-2">
            <Dialog open={isLoginOpen} onOpenChange={setIsLoginOpen}>
              <DialogTrigger asChild>
                <Button variant="link" className="hidden sm:inline-flex text-gray-600">
                  Log In
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
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
                      <Input type="email" id="email-login" placeholder="you@company.com" className="pl-10" />
                    </div>
                  </div>
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="password-login">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input type="password" id="password-login" placeholder="••••••••" className="pl-10" />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700" onClick={() => setIsLoginOpen(false)}>Log In</Button>
                </DialogFooter>
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
                      <Input type="email" id="email-signup" placeholder="you@company.com" className="pl-10" />
                    </div>
                  </div>
                  <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="password-signup">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input type="password" id="password-signup" placeholder="Create a strong password" className="pl-10" />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700" onClick={() => setIsSignupOpen(false)}>Sign Up & Analyze</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>
    </header>
  );
}
