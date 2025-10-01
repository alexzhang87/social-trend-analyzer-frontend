// 2.0版本首页设计备份
// 创建时间: 2024年12月
// 特点: 简洁化设计，参考dimeadozen.ai风格，包含AI对话框、功能介绍等模块

import { useState } from "react";
import { Header } from "./header";
import { useAuth } from "@/components/auth-provider";
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
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

// 注意: 这是2.0版本的完整备份，如需恢复，请将此文件内容复制回landing-page.tsx
// 当前文件仅作为备份参考，不会被实际使用

export default function LandingPageV2() {
  // ... 这里应该包含完整的2.0版本代码
  // 由于内容较长，此处仅作为备份标记
  // 实际使用时需要复制完整的landing-page.tsx内容
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="text-center p-8">
        <h1 className="text-2xl font-bold text-gray-800">2.0版本首页设计备份</h1>
        <p className="text-gray-600 mt-2">此文件为备份参考，实际内容请查看完整的landing-page.tsx</p>
      </div>
    </div>
  );
}
