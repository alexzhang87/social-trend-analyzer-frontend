import React from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { FaGithub } from 'react-icons/fa';
import { FcGoogle } from 'react-icons/fc';
import { useAuth } from '../components/auth-provider';
import './Auth.css';

const LoginPage: React.FC = () => {
  const { googleAuth } = useAuth();

  const handleGoogleLogin = () => {
    googleAuth();
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Log in</h2>
        <Button variant="outline" className="social-btn">
          <FaGithub className="mr-2" /> GitHub
        </Button>
        <Button variant="outline" className="social-btn" onClick={handleGoogleLogin}>
          <FcGoogle className="mr-2" /> Google
        </Button>
        <div className="divider">
          <span>or with Email</span>
        </div>
        <Input type="email" placeholder="Email" />
        <Input type="password" placeholder="Password" />
        <a href="#" className="forgot-password">
          Forgot password?
        </a>
        <Button className="auth-btn">Log in</Button>
        <p className="switch-auth">
          Don't have an account? <a href="/register">Sign up</a>
        </p>
        <p className="terms">
          By continuing, you are agreeing to Trae's Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;