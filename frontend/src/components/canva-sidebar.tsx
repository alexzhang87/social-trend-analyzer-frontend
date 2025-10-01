import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Home,
  Search,
  Target,
  BarChart3,
  Lightbulb,
  FileText,
  Settings,
  HelpCircle,
  User,
  Zap,
  Plus,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Brain,
  Leaf,
  MessageCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

import { cn } from '@/lib/utils';

interface SidebarItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

interface CanvaSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  userStats: {
    creditsRemaining: number;
    totalProjects: number;
    completedAnalyses: number;
  };
}

const sidebarItems: SidebarItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Home,
    description: 'Overview and key metrics',
  },
  {
    id: 'analysis',
    label: 'Keyword Analysis',
    icon: Search,
    description: 'Analyze market trends and opportunities',
  },
  {
    id: 'pmf',
    label: 'PMF Scorecard',
    icon: Target,
    description: 'Product-market fit evaluation',
  },
  {
    id: 'insights',
    label: 'AI Insights',
    icon: Brain,
    description: 'AI-powered business recommendations',
  },
  {
    id: 'history',
    label: 'Chat History',
    icon: MessageCircle,
    description: 'View conversation history',
  },
  {
    id: 'competitors',
    label: 'Competitor Monitor',
    icon: AlertTriangle,
    description: 'Track competitor activities',
  },
  {
    id: 'reports',
    label: 'Data Studio',
    icon: BarChart3,
    description: 'Generate comprehensive reports',
  },
  {
    id: 'templates',
    label: 'Templates',
    icon: FileText,
    description: 'Pre-built analysis templates',
  },
];

const bottomItems: SidebarItem[] = [
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    description: 'Account and app preferences',
  },
  {
    id: 'help',
    label: 'Help & Support',
    icon: HelpCircle,
    description: 'Get help and tutorials',
  },
  {
    id: 'account',
    label: 'Account',
    icon: User,
    description: 'Profile and subscription',
  },
];

export function CanvaSidebar({ 
  activeSection, 
  onSectionChange, 
  userStats 
}: CanvaSidebarProps) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const renderSidebarItem = (item: SidebarItem, index: number) => {
    const isActive = activeSection === item.id;
    const isHovered = hoveredItem === item.id;

    return (
      <motion.div
        key={item.id}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.05 }}
        className="relative"
      >
        <Button
          variant="ghost"
          onClick={() => onSectionChange(item.id)}
          onMouseEnter={() => setHoveredItem(item.id)}
          onMouseLeave={() => setHoveredItem(null)}
          className={cn(
            "w-full justify-start gap-3 h-12 px-3 mb-1 transition-all duration-200",
            "hover:bg-gradient-to-r hover:from-purple-50 hover:to-blue-50",
            "hover:border-l-4 hover:border-l-purple-500",
            isActive && "bg-gradient-to-r from-purple-100 to-blue-100 border-l-4 border-l-purple-500 text-purple-700"
          )}
        >
          <div className={cn(
            "flex items-center justify-center w-6 h-6 rounded-lg transition-all duration-200",
            isActive && "bg-purple-500 text-white",
            !isActive && isHovered && "bg-purple-100 text-purple-600",
            !isActive && !isHovered && "text-gray-600"
          )}>
            <item.icon className="w-4 h-4" />
          </div>
          
          <div className="flex-1 text-left">
            <div className="font-medium text-sm">{item.label}</div>
          </div>
          
          <div className="flex items-center gap-1">
            {item.badge && (
              <Badge variant="secondary" className="text-xs px-2 py-0 bg-orange-100 text-orange-700">
                {item.badge}
              </Badge>
            )}
            {item.isNew && (
              <Badge variant="secondary" className="text-xs px-2 py-0 bg-green-100 text-green-700">
                New
              </Badge>
            )}
            {item.isPro && (
              <Badge variant="secondary" className="text-xs px-2 py-0 bg-purple-100 text-purple-700">
                Pro
              </Badge>
            )}
          </div>
        </Button>
      </motion.div>
    );
  };

  return (
    <motion.div
      initial={{ x: -20, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 shadow-lg z-50"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-400 rounded-lg flex items-center justify-center">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-gray-900 text-xl">IdeaEden</span>
          </div>
        </div>
      </div>



      {/* Quick Search */}
      <div className="p-4 border-b border-gray-100">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search features..."
            className="w-full pl-10 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-50"
          />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {sidebarItems.map((item) => (
          <motion.button
            key={item.id}
            onClick={() => onSectionChange(item.id)}
            className={`w-full flex items-center px-4 py-3 rounded-xl text-left transition-all duration-200 ${
              activeSection === item.id
                ? 'bg-blue-500 text-white shadow-lg'
                : 'text-gray-700 hover:bg-gray-100'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center space-x-3">
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </div>
          </motion.button>
        ))}
        
        {/* Quick Actions */}
        <div className="pt-4 mt-4 border-t border-gray-100">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSectionChange('analysis')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-md hover:from-emerald-600 hover:to-teal-600 transition-all duration-200"
          >
            <Plus className="w-4 h-4" />
            <span className="font-medium text-sm">New Analysis</span>
            <Badge variant="secondary" className="text-xs px-2 py-0 bg-white/20 text-white ml-auto">
              Ctrl+N
            </Badge>
          </motion.button>
        </div>
      </nav>

      {/* Bottom Section */}
      <div className="p-4 border-t border-gray-200 space-y-3">
        {/* Credits Display */}
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-yellow-500" />
            <span className="text-sm font-medium text-gray-700">Credits</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-yellow-600">{userStats.creditsRemaining}</span>
            <span className="text-xs text-gray-500">remaining</span>
          </div>
        </div>

        {/* Upgrade Banner */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-gray-700">Upgrade</span>
          </div>
          <p className="text-xs text-gray-600 mb-2">Get unlimited access to all features</p>
          <Button size="sm" className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600">
            Upgrade Now
          </Button>
        </div>

        {/* Bottom Menu Items */}
        <div className="space-y-1">
          {bottomItems.map((item) => (
            <motion.button
              key={item.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSectionChange(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                activeSection === item.id
                  ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-md'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <item.icon className="w-4 h-4 flex-shrink-0" />
              <span className="font-medium text-sm">{item.label}</span>
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
