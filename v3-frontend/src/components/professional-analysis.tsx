import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Target, 
  Users, 
  TrendingUp, 
  BarChart3,
  PieChart,
  FileText,
  Download,
  Share2,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Info,
  Star,
  DollarSign,
  Calendar,
  Globe,
  Lightbulb,
  Shield,
  Zap,
  Brain,
  Rocket,
  User,
  Clock,
  MessageSquare,
  ArrowRight
} from 'lucide-react';
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend
} from 'recharts';

interface ProfessionalAnalysisData {
  keyword: string;
  overallScore: number;
  marketSize: {
    value: number;
    unit: string;
    growth: number;
  };
  competitorAnalysis: Array<{
    name: string;
    marketShare: number;
    strengths: string[];
    weaknesses: string[];
    pricing: string;
  }>;
  userPersonas: Array<{
    name: string;
    description: string;
    painPoints: string[];
    motivations: string[];
    demographics: {
      age: string;
      income: string;
      location: string;
    };
  }>;
  businessOpportunities: Array<{
    title: string;
    description: string;
    potential: 'high' | 'medium' | 'low';
    timeframe: string;
    investment: string;
  }>;
  marketTrends: Array<{
    trend: string;
    impact: 'positive' | 'negative' | 'neutral';
    description: string;
  }>;
  riskAssessment: {
    overall: 'low' | 'medium' | 'high';
    factors: Array<{
      factor: string;
      level: 'low' | 'medium' | 'high';
      description: string;
    }>;
  };
  recommendations: Array<{
    category: string;
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  financialProjections: {
    revenue: Array<{
      year: number;
      conservative: number;
      optimistic: number;
    }>;
    costs: Array<{
      category: string;
      amount: number;
    }>;
  };
}

interface ProfessionalAnalysisProps {
  keyword: string;
  onNewAnalysis: () => void;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

export function ProfessionalAnalysis({ keyword, onNewAnalysis }: ProfessionalAnalysisProps) {
  const [data, setData] = useState<ProfessionalAnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [aiGenerationStatus, setAiGenerationStatus] = useState<string>('');
  const [generationProgress, setGenerationProgress] = useState(0);

  useEffect(() => {
    fetchProfessionalAnalysis();
  }, [keyword]);

  const fetchProfessionalAnalysis = async () => {
    setIsLoading(true);
    setError(null);
    setGenerationProgress(0);
    
    try {
      // Simulate AI generation process
      const generationSteps = [
        { status: '🧠 AI is analyzing market overview...', progress: 15 },
        { status: '🔍 AI is researching competitors...', progress: 30 },
        { status: '👥 AI is building user personas...', progress: 45 },
        { status: '💡 AI is identifying market opportunities...', progress: 60 },
        { status: '⚠️ AI is evaluating risk factors...', progress: 75 },
        { status: '💰 AI is generating financial forecasts...', progress: 90 },
        { status: '✅ AI analysis complete, organizing report...', progress: 100 }
      ];

      for (const step of generationSteps) {
        setAiGenerationStatus(step.status);
        setGenerationProgress(step.progress);
        await new Promise(resolve => setTimeout(resolve, 800));
      }
      
      // Mock data - replace with actual API response
      const mockData: ProfessionalAnalysisData = {
        keyword,
        overallScore: Math.floor(Math.random() * 30) + 70,
        marketSize: {
          value: Math.floor(Math.random() * 1500) + 500, // Increased range for more realistic data
          unit: 'billion USD',
          growth: Math.floor(Math.random() * 35) + 15 // Higher growth rates
        },
        competitorAnalysis: [
          {
            name: 'OpenAI',
            marketShare: 42,
            market_position: 'Market Leader',
            competitive_positioning: 'Premium AI technology provider',
            founded: 2015,
            headquarters: 'San Francisco, CA',
            funding: '$11.3B',
            employees: '1000+',
            strengths: [
              'Industry-leading AI technology and research capabilities',
              'Strong brand recognition and developer ecosystem',
              'Continuous innovation with GPT models and API platform',
              'Strategic partnerships with Microsoft and enterprise clients',
              'First-mover advantage in conversational AI market'
            ],
            weaknesses: [
              'High operational costs and infrastructure requirements',
              'Regulatory scrutiny and ethical AI concerns',
              'Dependency on cloud infrastructure and scaling challenges',
              'Limited customization options for enterprise clients',
              'Potential for model hallucinations and accuracy issues'
            ],
            pricing: '$0.002-0.12 per 1K tokens',
            pricing_model: 'Usage-based ($0.002-0.12 per 1K tokens)',
            competitive_advantage: 'First-mover advantage in generative AI with superior model performance and developer ecosystem',
            technology_stack: ['Python/PyTorch', 'Kubernetes', 'Cloud Infrastructure', 'GPU Clusters', 'MLOps Pipeline'],
            customer_segments: ['Enterprise Developers', 'SaaS Companies', 'Research Institutions', 'Startups', 'Fortune 500'],
            financial_metrics: {
              annual_revenue: '$2000M',
              growth_rate: '150% YoY',
              valuation: '$80B',
              burn_rate: '$500M/year',
              funding_stage: 'Private'
            },
            recent_developments: [
              'Launched GPT-4 Turbo with improved performance and lower costs',
              'Introduced custom GPTs and GPT Store marketplace',
              'Expanded enterprise partnerships and API capabilities'
            ]
          },
          {
            name: 'Google (Bard/Gemini)',
            marketShare: 28,
            market_position: 'Major Player',
            competitive_positioning: 'Innovation leader with cutting-edge technology',
            founded: 1998,
            headquarters: 'Mountain View, CA',
            funding: 'Public Company',
            employees: '180000+',
            strengths: [
              'Massive data resources and search integration',
              'Advanced multimodal AI capabilities',
              'Strong cloud infrastructure and global reach',
              'Integration with Google Workspace and enterprise tools',
              'Extensive research in AI safety and alignment'
            ],
            weaknesses: [
              'Late entry into conversational AI market',
              'Privacy concerns and data usage policies',
              'Complex pricing structure and enterprise adoption barriers',
              'Limited third-party developer ecosystem compared to OpenAI',
              'Inconsistent performance across different use cases'
            ],
            pricing: 'Free tier + $20/month for advanced features',
            pricing_model: 'Freemium with premium tiers ($20/month)',
            competitive_advantage: 'Unparalleled data access and search integration with massive cloud infrastructure',
            technology_stack: ['TensorFlow', 'Cloud TPU', 'Kubernetes', 'BigQuery', 'Vertex AI'],
            customer_segments: ['Enterprise', 'Developers', 'Consumers', 'Educational Institutions', 'Government'],
            financial_metrics: {
              annual_revenue: '$280000M',
              growth_rate: '25% YoY',
              valuation: '$1700B',
              burn_rate: 'Profitable',
              funding_stage: 'Public'
            },
            recent_developments: [
              'Released Gemini Ultra with state-of-the-art performance',
              'Integrated Bard with Google Workspace suite',
              'Expanded AI capabilities across Google products'
            ]
          },
          {
            name: 'Anthropic (Claude)',
            marketShare: 18,
            market_position: 'Strong Competitor',
            competitive_positioning: 'Niche specialist with deep domain expertise',
            founded: 2021,
            headquarters: 'San Francisco, CA',
            funding: '$7.3B',
            employees: '500+',
            strengths: [
              'Focus on AI safety and constitutional AI approach',
              'Strong performance in reasoning and analysis tasks',
              'Growing enterprise adoption and partnership network',
              'Transparent AI development and ethical guidelines',
              'Superior handling of complex, nuanced conversations'
            ],
            weaknesses: [
              'Smaller market presence and brand recognition',
              'Limited API ecosystem and developer tools',
              'Higher pricing compared to some competitors',
              'Restricted availability in certain regions',
              'Slower feature rollout and product updates'
            ],
            pricing: '$0.008-0.024 per 1K tokens',
            pricing_model: 'Usage-based ($0.008-0.024 per 1K tokens)',
            competitive_advantage: 'Leading focus on AI safety and constitutional AI development with superior reasoning',
            technology_stack: ['Constitutional AI', 'RLHF', 'Cloud Infrastructure', 'Safety Monitoring', 'Alignment Research'],
            customer_segments: ['Enterprise', 'Researchers', 'Content Creators', 'Legal Professionals', 'Consultants'],
            financial_metrics: {
              annual_revenue: '$500M',
              growth_rate: '300% YoY',
              valuation: '$18B',
              burn_rate: '$200M/year',
              funding_stage: 'Series C'
            },
            recent_developments: [
              'Launched Claude 3 with improved multimodal capabilities',
              'Secured major enterprise partnerships',
              'Advanced research in AI safety and alignment'
            ]
          },
          {
            name: 'Microsoft (Copilot)',
            marketShare: 12,
            market_position: 'Strong Competitor',
            competitive_positioning: 'Enterprise-focused productivity AI',
            founded: 1975,
            headquarters: 'Redmond, WA',
            funding: 'Public Company',
            employees: '220000+',
            strengths: [
              'Deep integration with Microsoft Office and enterprise tools',
              'Strong enterprise relationships and sales channels',
              'Comprehensive AI platform with Azure backing',
              'Focus on productivity and business applications',
              'Established trust with enterprise customers'
            ],
            weaknesses: [
              'Dependency on OpenAI technology and partnership',
              'Limited standalone AI product offerings',
              'Complex licensing and enterprise pricing models',
              'Integration complexity for non-Microsoft environments',
              'Slower innovation compared to AI-native companies'
            ],
            pricing: '$30/month per user for enterprise',
            pricing_model: '$30/month per user with volume discounts',
            competitive_advantage: 'Deep enterprise integration and productivity-focused AI solutions',
            technology_stack: ['Azure AI', 'Office 365', 'Power Platform', 'Teams Integration', 'Enterprise Security'],
            customer_segments: ['Enterprise', 'SMB', 'Government', 'Education', 'Healthcare'],
            financial_metrics: {
              annual_revenue: '$211000M',
              growth_rate: '12% YoY',
              valuation: '$2800B',
              burn_rate: 'Profitable',
              funding_stage: 'Public'
            },
            recent_developments: [
              'Integrated Copilot across Microsoft 365 suite',
              'Launched Azure OpenAI Service for enterprises',
              'Expanded AI capabilities in Windows and Edge'
            ]
          }
        ],
        userPersonas: [
          {
            name: 'AI Innovation Leader',
            description: 'C-level executives and innovation directors driving AI transformation in their organizations',
            demographics: {
              age: '40-55',
              income: '$150k-500k+',
              location: 'Major tech hubs and business centers',
              education: 'MBA or Advanced Degree',
              company_size: '500-10,000 employees',
              job_titles: ['Chief Technology Officer', 'VP of Innovation', 'Head of AI Strategy', 'Chief Data Officer']
            },
            psychographics: {
              personality_traits: ['Strategic', 'Visionary', 'Risk-aware', 'Results-driven'],
              values: ['Innovation', 'Competitive advantage', 'Operational excellence', 'Future-proofing'],
              lifestyle: 'Executive-level professional focused on strategic initiatives',
              technology_comfort: 'High'
            },
            painPoints: [
              'Difficulty scaling AI initiatives across organization',
              'Lack of skilled AI talent and expertise',
              'ROI measurement and business case challenges',
              'Integration with legacy systems and workflows',
              'Regulatory compliance and ethical AI considerations'
            ],
            motivations: [
              'Achieve competitive advantage through AI innovation',
              'Drive operational efficiency and cost reduction',
              'Future-proof the organization with AI capabilities',
              'Lead market innovation and digital transformation',
              'Build sustainable AI-driven business models'
            ],
            goals: [
              'Implement enterprise-wide AI strategy',
              'Achieve measurable ROI from AI investments',
              'Build AI-native organizational capabilities',
              'Lead market innovation in AI adoption'
            ],
            decision_process: {
              research_phase: '6-12 months of evaluation',
              influence_level: 'High',
              budget_authority: true
            },
            preferred_channels: [
              'Industry conferences and executive events',
              'Executive networks and peer recommendations',
              'Analyst reports and thought leadership',
              'Strategic consulting and advisory services'
            ],
            content_preferences: [
              'Strategic case studies and business impact',
              'ROI analysis and financial projections',
              'Industry benchmarks and competitive analysis',
              'Executive briefings and whitepapers'
            ]
          },
          {
            name: 'Technical AI Practitioner',
            description: 'Data scientists, ML engineers, and AI researchers implementing cutting-edge AI solutions',
            demographics: {
              age: '28-40',
              income: '$80k-200k',
              location: 'Tech cities worldwide',
              education: 'Computer Science, Statistics, or related field',
              company_size: '50-5,000 employees',
              job_titles: ['Data Scientist', 'ML Engineer', 'AI Researcher', 'Technical Lead']
            },
            psychographics: {
              personality_traits: ['Analytical', 'Detail-oriented', 'Innovation-focused', 'Collaborative'],
              values: ['Technical excellence', 'Open source', 'Continuous learning', 'Problem-solving'],
              lifestyle: 'Tech-focused professional with emphasis on skill development',
              technology_comfort: 'Expert'
            },
            painPoints: [
              'Model deployment and monitoring challenges',
              'Data quality and availability issues',
              'Limited computational resources and infrastructure',
              'Keeping up with rapid AI technology advances',
              'Bridging gap between research and production'
            ],
            motivations: [
              'Build cutting-edge AI solutions that solve real problems',
              'Advance career in rapidly growing AI field',
              'Contribute to open source and AI community',
              'Work with state-of-the-art technologies and models',
              'Solve complex technical and algorithmic challenges'
            ],
            goals: [
              'Deploy production-ready AI models at scale',
              'Improve model performance and accuracy',
              'Streamline ML workflow and operations',
              'Build scalable AI infrastructure and platforms'
            ],
            decision_process: {
              research_phase: '3-6 months of technical evaluation',
              influence_level: 'Medium to High',
              budget_authority: false
            },
            preferred_channels: [
              'Developer communities and forums',
              'Technical conferences and workshops',
              'GitHub and open source platforms',
              'Research publications and papers'
            ],
            content_preferences: [
              'Technical documentation and API references',
              'Code examples and implementation tutorials',
              'Performance benchmarks and comparisons',
              'Research papers and technical deep-dives'
            ]
          },
          {
            name: 'Business Operations Manager',
            description: 'Mid-level managers focused on operational efficiency and process improvement through AI',
            demographics: {
              age: '32-48',
              income: '$60k-130k',
              location: 'Various business centers',
              education: 'Bachelor\'s in Business or related field',
              company_size: '100-2,000 employees',
              job_titles: ['Operations Manager', 'Process Improvement Lead', 'Business Analyst', 'Project Manager']
            },
            psychographics: {
              personality_traits: ['Practical', 'Efficiency-focused', 'Process-oriented', 'Team-oriented'],
              values: ['Operational excellence', 'Cost efficiency', 'Team productivity', 'Measurable results'],
              lifestyle: 'Results-driven professional balancing multiple priorities',
              technology_comfort: 'Intermediate'
            },
            painPoints: [
              'Manual processes consuming excessive time and resources',
              'Difficulty measuring and demonstrating process improvements',
              'Limited budget for new technology implementations',
              'Resistance to change from team members and stakeholders',
              'Lack of technical expertise for AI implementation'
            ],
            motivations: [
              'Improve team productivity and operational efficiency',
              'Reduce operational costs and resource waste',
              'Streamline business processes and workflows',
              'Demonstrate measurable business value and impact',
              'Advance career through successful improvement initiatives'
            ],
            goals: [
              'Automate repetitive manual tasks and processes',
              'Improve process efficiency by 20-30%',
              'Reduce operational costs and improve margins',
              'Enhance team satisfaction and productivity'
            ],
            decision_process: {
              research_phase: '2-4 months of practical evaluation',
              influence_level: 'Medium',
              budget_authority: false
            },
            preferred_channels: [
              'Professional associations and industry groups',
              'Industry publications and trade magazines',
              'Peer recommendations and case studies',
              'Webinars and professional training programs'
            ],
            content_preferences: [
              'Process improvement case studies and success stories',
              'ROI calculators and business impact analysis',
              'Implementation guides and best practices',
              'Training materials and change management resources'
            ]
          }
        ],
        businessOpportunities: [
          {
            title: 'Enterprise AI Transformation Platform',
            description: 'Comprehensive AI adoption platform helping enterprises integrate AI across all business functions with governance, training, and ROI tracking',
            potential: 'high',
            timeframe: '12-18 months',
            investment: '$200-500B market size',
            market_drivers: [
              '87% of enterprises planning AI investments in 2024',
              'Growing demand for AI governance and compliance',
              'Need for unified AI strategy and implementation'
            ],
            competitive_advantages: [
              'End-to-end AI transformation approach',
              'Industry-specific AI templates and frameworks',
              'Built-in compliance and governance tools',
              'Proven ROI measurement and tracking'
            ],
            revenue_streams: [
              'Platform licensing ($50-200K annually per enterprise)',
              'Professional services and consulting ($100-500K per project)',
              'Training and certification programs ($5-15K per user)',
              'Custom AI model development ($50-300K per model)'
            ],
            key_metrics: {
              market_growth_rate: '35% CAGR',
              customer_acquisition_cost: '$25,000',
              lifetime_value: '$500,000',
              gross_margin: '75%'
            },
            strategic_recommendations: [
              'Partner with major cloud providers for distribution',
              'Develop industry-specific AI accelerators',
              'Build strong ecosystem of AI consultants and integrators',
              'Focus on measurable business outcomes and ROI'
            ]
          },
          {
            title: 'Vertical AI Solutions for Healthcare',
            description: 'Specialized AI platform for healthcare providers focusing on diagnostic assistance, patient care optimization, and operational efficiency',
            potential: 'high',
            timeframe: '18-24 months',
            investment: '$150-350B market size',
            market_drivers: [
              'Healthcare AI market growing at 45% CAGR',
              'Physician shortage driving automation needs',
              'Regulatory approval pathways becoming clearer',
              'Proven ROI in diagnostic accuracy and efficiency'
            ],
            competitive_advantages: [
              'HIPAA-compliant AI infrastructure',
              'FDA-approved diagnostic algorithms',
              'Integration with major EHR systems',
              'Clinical evidence and validation'
            ],
            revenue_streams: [
              'SaaS subscriptions ($10-50K per provider monthly)',
              'Per-diagnosis licensing ($5-25 per analysis)',
              'Implementation and training services ($100-500K)',
              'Data analytics and insights ($20-100K monthly)'
            ],
            key_metrics: {
              market_growth_rate: '45% CAGR',
              customer_acquisition_cost: '$50,000',
              lifetime_value: '$800,000',
              gross_margin: '80%'
            },
            strategic_recommendations: [
              'Focus on high-value diagnostic specialties first',
              'Build partnerships with medical device manufacturers',
              'Invest heavily in clinical validation and trials',
              'Develop strong regulatory and compliance expertise'
            ]
          },
          {
            title: 'AI-Powered Financial Services Platform',
            description: 'Comprehensive AI solution for financial institutions covering risk assessment, fraud detection, algorithmic trading, and customer insights',
            potential: 'high',
            timeframe: '15-20 months',
            investment: '$120-280B market size',
            market_drivers: [
              'Financial services AI spending growing 25% annually',
              'Increasing regulatory requirements for risk management',
              'Need for real-time fraud detection and prevention',
              'Demand for personalized financial products'
            ],
            competitive_advantages: [
              'Real-time transaction processing capabilities',
              'Advanced risk modeling and prediction',
              'Regulatory compliance built-in',
              'Multi-asset class trading algorithms'
            ],
            revenue_streams: [
              'Platform licensing ($100-500K annually per institution)',
              'Transaction-based fees ($0.01-0.10 per transaction)',
              'Risk assessment services ($50-200K monthly)',
              'Custom algorithm development ($200-1M per project)'
            ],
            key_metrics: {
              market_growth_rate: '25% CAGR',
              customer_acquisition_cost: '$100,000',
              lifetime_value: '$1,200,000',
              gross_margin: '70%'
            },
            strategic_recommendations: [
              'Start with mid-tier banks and credit unions',
              'Build strong partnerships with fintech companies',
              'Invest in regulatory expertise and compliance',
              'Focus on measurable risk reduction and ROI'
            ]
          },
          {
            title: 'Edge AI and IoT Intelligence Platform',
            description: 'Distributed AI platform for IoT devices enabling real-time processing, predictive maintenance, and autonomous decision-making at the edge',
            potential: 'medium',
            timeframe: '24-36 months',
            investment: '$80-180B market size',
            market_drivers: [
              'IoT device growth reaching 75B devices by 2025',
              'Need for real-time processing and low latency',
              'Bandwidth and cloud cost optimization',
              'Privacy and security requirements for local processing'
            ],
            competitive_advantages: [
              'Ultra-low latency processing capabilities',
              'Optimized for resource-constrained devices',
              'Federated learning and model updates',
              'Industry-specific IoT AI models'
            ],
            revenue_streams: [
              'Device licensing ($5-50 per device annually)',
              'Platform management services ($10-100K monthly)',
              'Custom model development ($50-300K per project)',
              'Data analytics and insights ($20-150K monthly)'
            ],
            key_metrics: {
              market_growth_rate: '30% CAGR',
              customer_acquisition_cost: '$75,000',
              lifetime_value: '$600,000',
              gross_margin: '65%'
            },
            strategic_recommendations: [
              'Partner with major IoT hardware manufacturers',
              'Focus on high-value use cases like predictive maintenance',
              'Develop industry-specific edge AI solutions',
              'Build strong ecosystem of device partners'
            ]
          },
          {
            title: 'AI Ethics and Governance Platform',
            description: 'Comprehensive platform for AI governance, bias detection, explainability, and regulatory compliance management',
            potential: 'medium',
            timeframe: '12-15 months',
            investment: '$30-80B market size',
            market_drivers: [
              'Increasing AI regulation and compliance requirements',
              'Growing awareness of AI bias and fairness issues',
              'Need for AI transparency and explainability',
              'Corporate responsibility and ESG initiatives'
            ],
            competitive_advantages: [
              'Comprehensive AI governance framework',
              'Real-time bias detection and mitigation',
              'Regulatory compliance automation',
              'Industry-leading explainability tools'
            ],
            revenue_streams: [
              'Platform subscriptions ($25-150K annually per organization)',
              'Compliance consulting services ($100-500K per project)',
              'Training and certification programs ($2-10K per user)',
              'Custom governance framework development ($50-250K)'
            ],
            key_metrics: {
              market_growth_rate: '40% CAGR',
              customer_acquisition_cost: '$40,000',
              lifetime_value: '$400,000',
              gross_margin: '85%'
            },
            strategic_recommendations: [
              'Build partnerships with major consulting firms',
              'Develop industry-specific compliance templates',
              'Focus on enterprises with high regulatory requirements',
              'Invest in thought leadership and regulatory expertise'
            ]
          }
        ],
        marketTrends: [
          {
            trend: 'Exponential Growth in AI Adoption',
            impact: 'positive',
            description: 'Enterprise AI adoption accelerating with 67% of companies planning significant AI investments in 2024-2025'
          },
          {
            trend: 'Regulatory Framework Development',
            impact: 'neutral',
            description: 'EU AI Act and similar regulations creating compliance requirements but also market standardization opportunities'
          },
          {
            trend: 'AI Democratization Through APIs',
            impact: 'positive',
            description: 'Lower barriers to entry enabling smaller companies to compete with AI-powered solutions'
          },
          {
            trend: 'Focus on AI Safety and Ethics',
            impact: 'positive',
            description: 'Growing demand for responsible AI solutions creating new market segments for governance and safety tools'
          },
          {
            trend: 'Shift to Multimodal AI',
            impact: 'positive',
            description: 'Integration of text, image, audio, and video processing becoming standard expectation for AI platforms'
          }
        ],
        riskAssessment: {
          overall: 'medium',
          risk_score: 6.2,
          confidence_level: 'high',
          last_updated: '2024-01-15',
          factors: [
            {
              factor: 'Intense Market Competition',
              level: 'high',
              probability: 0.85,
              impact_score: 8.5,
              time_horizon: 'immediate',
              description: 'Major tech giants (Google, Microsoft, OpenAI) with massive resources and established market positions pose significant competitive threats',
              indicators: [
                'Google Bard and ChatGPT rapid feature releases',
                'Microsoft Copilot integration across Office suite',
                'OpenAI GPT-4 enterprise adoption acceleration'
              ],
              mitigation_strategies: [
                'Focus on niche vertical markets with specialized solutions',
                'Build strategic partnerships with industry leaders',
                'Develop unique IP and proprietary datasets',
                'Implement rapid iteration and customer feedback loops'
              ],
              contingency_plans: [
                'Pivot to B2B white-label solutions if direct competition intensifies',
                'Consider acquisition opportunities with larger players',
                'Develop defensive patent portfolio'
              ]
            },
            {
              factor: 'Rapid Technology Evolution',
              level: 'high',
              probability: 0.90,
              impact_score: 7.8,
              time_horizon: 'short-term',
              description: 'Fast-paced AI advancement requires continuous innovation and significant R&D investment to remain competitive',
              indicators: [
                'Monthly major model releases from leading AI companies',
                'Breakthrough in multimodal AI capabilities',
                'Emergence of new AI architectures and paradigms'
              ],
              mitigation_strategies: [
                'Establish continuous learning and adaptation processes',
                'Invest 25-30% of revenue in R&D activities',
                'Build modular architecture for rapid technology integration',
                'Maintain close relationships with research institutions'
              ],
              contingency_plans: [
                'License cutting-edge technology from research labs',
                'Acquire smaller AI startups with breakthrough technologies',
                'Form joint ventures for shared R&D costs'
              ]
            },
            {
              factor: 'Regulatory Uncertainty',
              level: 'medium',
              probability: 0.70,
              impact_score: 6.5,
              time_horizon: 'medium-term',
              description: 'Evolving AI regulations across different jurisdictions may impact product development and market access strategies',
              indicators: [
                'EU AI Act implementation timeline',
                'US federal AI regulation proposals',
                'China AI governance framework updates'
              ],
              mitigation_strategies: [
                'Implement privacy-by-design principles',
                'Establish compliance monitoring systems',
                'Engage with regulatory bodies and industry associations',
                'Build flexible architecture to adapt to regulatory changes'
              ],
              contingency_plans: [
                'Develop region-specific product variants',
                'Establish legal entities in key jurisdictions',
                'Create regulatory compliance consulting services'
              ]
            },
            {
              factor: 'Talent Acquisition Challenges',
              level: 'high',
              probability: 0.80,
              impact_score: 7.2,
              time_horizon: 'immediate',
              description: 'Shortage of qualified AI engineers and researchers driving up costs and creating recruitment difficulties',
              indicators: [
                'Average AI engineer salary increases of 15-20% annually',
                'Extended time-to-hire for technical positions',
                'High turnover rates in AI talent market'
              ],
              mitigation_strategies: [
                'Develop comprehensive remote work policies',
                'Create attractive equity compensation packages',
                'Establish university partnership programs',
                'Invest in internal training and upskilling programs'
              ],
              contingency_plans: [
                'Outsource non-core AI development to specialized firms',
                'Implement AI-assisted development tools to increase productivity',
                'Consider acquisition of teams rather than individual hiring'
              ]
            },
            {
              factor: 'Infrastructure and Scaling Costs',
              level: 'medium',
              probability: 0.75,
              impact_score: 6.8,
              time_horizon: 'short-term',
              description: 'High computational costs for AI model training and inference may impact profitability and pricing strategies',
              indicators: [
                'GPU costs and availability constraints',
                'Cloud computing price increases',
                'Energy costs for data center operations'
              ],
              mitigation_strategies: [
                'Implement efficient model optimization techniques',
                'Negotiate long-term cloud provider contracts',
                'Develop hybrid cloud-edge deployment strategies',
                'Invest in model compression and quantization technologies'
              ],
              contingency_plans: [
                'Partner with cloud providers for preferential pricing',
                'Develop lightweight model variants for cost-sensitive customers',
                'Implement usage-based pricing models'
              ]
            }
          ],
          risk_matrix: {
            high_probability_high_impact: ['Intense Market Competition', 'Rapid Technology Evolution'],
            high_probability_low_impact: [],
            low_probability_high_impact: ['Regulatory Uncertainty'],
            low_probability_low_impact: ['Infrastructure and Scaling Costs']
          },
          monitoring_schedule: {
            daily: ['Market competition activities', 'Technology announcements'],
            weekly: ['Talent market trends', 'Infrastructure costs'],
            monthly: ['Regulatory developments', 'Risk score recalculation'],
            quarterly: ['Comprehensive risk assessment review']
          }
        },
        recommendations: [
          {
            category: 'Product Strategy',
            title: 'Focus on Vertical Specialization',
            description: 'Target specific industries with tailored AI solutions rather than competing directly with general-purpose platforms',
            priority: 'high'
          },
          {
            category: 'Technology',
            title: 'Invest in Edge AI Capabilities',
            description: 'Develop lightweight, on-device AI processing to differentiate from cloud-only competitors and address latency concerns',
            priority: 'high'
          },
          {
            category: 'Go-to-Market',
            title: 'Build Strategic Partnerships',
            description: 'Partner with industry leaders and system integrators to accelerate market entry and credibility',
            priority: 'high'
          },
          {
            category: 'Compliance',
            title: 'Proactive AI Governance Framework',
            description: 'Implement comprehensive AI ethics and compliance framework to address regulatory requirements and build trust',
            priority: 'medium'
          },
          {
            category: 'Talent',
            title: 'Establish AI Research Partnerships',
            description: 'Collaborate with universities and research institutions to access top talent and cutting-edge research',
            priority: 'medium'
          },
          {
            category: 'Business Model',
            title: 'Hybrid Pricing Strategy',
            description: 'Combine subscription, usage-based, and outcome-based pricing models to maximize market penetration and revenue',
            priority: 'medium'
          }
        ],
        financialProjections: {
          revenue: [
            { 
              year: 2024, 
              conservative: 2500000, 
              optimistic: 5000000,
              customers: { conservative: 250, optimistic: 500 },
              arpu: { conservative: 10000, optimistic: 10000 },
              growth_rate: { conservative: 0.15, optimistic: 0.25 }
            },
            { 
              year: 2025, 
              conservative: 8000000, 
              optimistic: 15000000,
              customers: { conservative: 650, optimistic: 1200 },
              arpu: { conservative: 12300, optimistic: 12500 },
              growth_rate: { conservative: 0.22, optimistic: 0.30 }
            },
            { 
              year: 2026, 
              conservative: 20000000, 
              optimistic: 40000000,
              customers: { conservative: 1400, optimistic: 2600 },
              arpu: { conservative: 14300, optimistic: 15400 },
              growth_rate: { conservative: 0.25, optimistic: 0.35 }
            },
            { 
              year: 2027, 
              conservative: 45000000, 
              optimistic: 85000000,
              customers: { conservative: 2700, optimistic: 4800 },
              arpu: { conservative: 16700, optimistic: 17700 },
              growth_rate: { conservative: 0.28, optimistic: 0.38 }
            },
            { 
              year: 2028, 
              conservative: 80000000, 
              optimistic: 150000000,
              customers: { conservative: 4200, optimistic: 7500 },
              arpu: { conservative: 19000, optimistic: 20000 },
              growth_rate: { conservative: 0.30, optimistic: 0.40 }
            }
          ],
          costs: [
            { 
              category: 'R&D and Engineering', 
              amount: 12000000,
              percentage: 40,
              breakdown: {
                'AI Research Team': 4500000,
                'Product Development': 3500000,
                'Infrastructure Engineering': 2500000,
                'Quality Assurance': 1500000
              }
            },
            { 
              category: 'Sales and Marketing', 
              amount: 8000000,
              percentage: 27,
              breakdown: {
                'Digital Marketing': 3000000,
                'Sales Team': 2500000,
                'Content Marketing': 1500000,
                'Events and Partnerships': 1000000
              }
            },
            { 
              category: 'Infrastructure and Operations', 
              amount: 5000000,
              percentage: 17,
              breakdown: {
                'Cloud Computing': 2500000,
                'Data Storage': 1200000,
                'Security and Compliance': 800000,
                'DevOps and Monitoring': 500000
              }
            },
            { 
              category: 'Legal and Compliance', 
              amount: 2000000,
              percentage: 7,
              breakdown: {
                'Legal Counsel': 800000,
                'IP Protection': 600000,
                'Regulatory Compliance': 400000,
                'Insurance': 200000
              }
            },
            { 
              category: 'General and Administrative', 
              amount: 3000000,
              percentage: 10,
              breakdown: {
                'Executive Team': 1200000,
                'Finance and Accounting': 600000,
                'HR and Recruiting': 800000,
                'Office and Facilities': 400000
              }
            }
          ],
          investment_requirements: {
            total_funding_needed: 30000000,
            funding_rounds: [
              {
                round: 'Seed',
                amount: 5000000,
                timeline: 'Q1 2024',
                use_of_funds: {
                  'Product Development': 60,
                  'Team Building': 25,
                  'Market Validation': 15
                }
              },
              {
                round: 'Series A',
                amount: 15000000,
                timeline: 'Q3 2024',
                use_of_funds: {
                  'Product Development': 40,
                  'Sales and Marketing': 35,
                  'Team Expansion': 25
                }
              },
              {
                round: 'Series B',
                amount: 10000000,
                timeline: 'Q2 2025',
                use_of_funds: {
                  'Market Expansion': 50,
                  'Product Enhancement': 30,
                  'Operations Scaling': 20
                }
              }
            ]
          },
          profitability_analysis: {
            break_even_point: {
              conservative: 'Q3 2026',
              optimistic: 'Q1 2026'
            },
            gross_margin: {
              year_1: 0.65,
              year_2: 0.72,
              year_3: 0.78,
              year_4: 0.82,
              year_5: 0.85
            },
            operating_margin: {
              year_1: -0.45,
              year_2: -0.15,
              year_3: 0.12,
              year_4: 0.25,
              year_5: 0.35
            }
          },
          key_metrics: {
            customer_acquisition_cost: {
              year_1: 3200,
              year_2: 2800,
              year_3: 2400,
              year_4: 2000,
              year_5: 1800
            },
            lifetime_value: {
              year_1: 45000,
              year_2: 52000,
              year_3: 58000,
              year_4: 65000,
              year_5: 72000
            },
            churn_rate: {
              year_1: 0.08,
              year_2: 0.06,
              year_3: 0.05,
              year_4: 0.04,
              year_5: 0.03
            },
            monthly_recurring_revenue_growth: {
              year_1: 0.15,
              year_2: 0.12,
              year_3: 0.10,
              year_4: 0.08,
              year_5: 0.06
            }
          },
          roi_analysis: {
            investor_returns: {
              '3_year_roi': 3.2,
              '5_year_roi': 8.5,
              'irr': 0.45
            },
            sensitivity_analysis: {
              best_case: {
                revenue_multiplier: 1.5,
                cost_multiplier: 0.9,
                roi: 12.8
              },
              worst_case: {
                revenue_multiplier: 0.7,
                cost_multiplier: 1.2,
                roi: 1.8
              }
            }
          }
        }
      };
      
      setData(mockData);
    } catch (err) {
      setError('Failed to fetch analysis data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Brain className="w-12 h-12 animate-pulse text-purple-500 mb-4" />
            <h3 className="text-xl font-semibold mb-2">AI Deep Analysis in Progress</h3>
            <p className="text-gray-600 text-center mb-6">
              Using AI to analyze the market potential of "{keyword}"...
            </p>
            
            {/* AI生成状态指示器 */}
            {aiGenerationStatus && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 w-96">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-blue-700 font-medium">{aiGenerationStatus}</span>
                </div>
              </div>
            )}
            
            <div className="space-y-3 w-80">
              <div className="flex justify-between text-sm">
                <span>Market Overview Analysis</span>
                <span className={generationProgress >= 15 ? "text-green-600" : "text-gray-400"}>
                  {generationProgress >= 15 ? "✓" : "⏳"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Competitor Research</span>
                <span className={generationProgress >= 30 ? "text-green-600" : generationProgress >= 15 ? "text-blue-600" : "text-gray-400"}>
                  {generationProgress >= 30 ? "✓" : generationProgress >= 15 ? <RefreshCw className="w-4 h-4 animate-spin" /> : "⏳"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>User Persona Building</span>
                <span className={generationProgress >= 45 ? "text-green-600" : generationProgress >= 30 ? "text-blue-600" : "text-gray-400"}>
                  {generationProgress >= 45 ? "✓" : generationProgress >= 30 ? <RefreshCw className="w-4 h-4 animate-spin" /> : "⏳"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Market Opportunity Identification</span>
                <span className={generationProgress >= 60 ? "text-green-600" : generationProgress >= 45 ? "text-blue-600" : "text-gray-400"}>
                  {generationProgress >= 60 ? "✓" : generationProgress >= 45 ? <RefreshCw className="w-4 h-4 animate-spin" /> : "⏳"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Risk Assessment Analysis</span>
                <span className={generationProgress >= 75 ? "text-green-600" : generationProgress >= 60 ? "text-blue-600" : "text-gray-400"}>
                  {generationProgress >= 75 ? "✓" : generationProgress >= 60 ? <RefreshCw className="w-4 h-4 animate-spin" /> : "⏳"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Financial Forecast Generation</span>
                <span className={generationProgress >= 90 ? "text-green-600" : generationProgress >= 75 ? "text-blue-600" : "text-gray-400"}>
                  {generationProgress >= 90 ? "✓" : generationProgress >= 75 ? <RefreshCw className="w-4 h-4 animate-spin" /> : "⏳"}
                </span>
              </div>
            </div>
            
            <div className="w-80 mt-6 space-y-2">
              <Progress value={generationProgress} className="w-full" />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Progress</span>
                <span>{generationProgress}%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Alert variant="destructive">
          <AlertTriangle className="w-4 h-4" />
          <AlertDescription>
            {error || 'Failed to load analysis data'}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchProfessionalAnalysis}
              className="ml-4"
            >
              Try Again
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          Professional Analysis Report
        </h1>
        <p className="text-xl text-gray-600">
          Comprehensive market analysis for: <span className="font-semibold">"{keyword}"</span>
        </p>
        <div className="flex items-center justify-center gap-4">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="w-4 h-4 mr-2" />
            Share Report
          </Button>
        </div>
      </div>

      {/* Executive Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-6 h-6 text-purple-500" />
            Executive Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className={`text-4xl font-bold ${getScoreColor(data.overallScore)} mb-2`}>
                {data.overallScore}
              </div>
              <p className="text-gray-600">Overall Score</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">
                ${data.marketSize.value}M
              </div>
              <p className="text-gray-600">Market Size</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">
                +{data.marketSize.growth}%
              </div>
              <p className="text-gray-600">Annual Growth</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analysis Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="competitors">Competitors</TabsTrigger>
          <TabsTrigger value="personas">User Personas</TabsTrigger>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="risks">Risk Analysis</TabsTrigger>
          <TabsTrigger value="financials">Financials</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Market Trends */}
          <Card>
            <CardHeader>
              <CardTitle>Market Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.marketTrends.map((trend, index) => (
                  <div key={index} className="flex items-start gap-3 p-4 border rounded-lg">
                    <div className={`w-3 h-3 rounded-full mt-2 ${
                      trend.impact === 'positive' ? 'bg-green-500' :
                      trend.impact === 'negative' ? 'bg-red-500' : 'bg-gray-500'
                    }`} />
                    <div>
                      <h4 className="font-semibold">{trend.trend}</h4>
                      <p className="text-gray-600 text-sm">{trend.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Key Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Key Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.recommendations.slice(0, 3).map((rec, index) => (
                  <div key={index} className="flex items-start gap-3 p-4 border rounded-lg">
                    <Badge className={getPriorityColor(rec.priority)}>
                      {rec.priority.toUpperCase()}
                    </Badge>
                    <div>
                      <h4 className="font-semibold">{rec.title}</h4>
                      <p className="text-gray-600 text-sm">{rec.description}</p>
                      <Badge variant="outline" className="mt-2">{rec.category}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="competitors" className="space-y-6">
          <div className="grid gap-6">
            {data.competitorAnalysis.map((competitor, index) => (
              <Card key={index} className="overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-xl">{competitor.name}</CardTitle>
                      <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                        {competitor.market_position || competitor.marketPosition || 'Market Player'}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="text-lg font-semibold">
                        {competitor.marketShare || competitor.market_share}% market share
                      </Badge>
                      <p className="text-sm text-gray-600 mt-1">
                        {competitor.competitive_positioning || competitor.competitivePositioning}
                      </p>
                    </div>
                  </div>
                  
                  {/* Company Info */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
                    <div>
                      <span className="text-gray-600">Founded:</span>
                      <p className="font-medium">{competitor.founded || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Employees:</span>
                      <p className="font-medium">{competitor.employees || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Funding:</span>
                      <p className="font-medium">{competitor.funding || 'N/A'}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">HQ:</span>
                      <p className="font-medium">{competitor.headquarters || 'N/A'}</p>
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="p-6">
                  {/* Pricing and Competitive Advantage */}
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-green-800 mb-2">Pricing Model</h4>
                      <p className="text-sm text-green-700">
                        {competitor.pricing_model || competitor.pricing}
                      </p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-purple-800 mb-2">Competitive Advantage</h4>
                      <p className="text-sm text-purple-700">
                        {competitor.competitive_advantage || competitor.competitiveAdvantage || 'Strong market position'}
                      </p>
                    </div>
                  </div>

                  {/* Strengths and Weaknesses */}
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div>
                      <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
                        <CheckCircle className="w-5 h-5" />
                        Key Strengths
                      </h4>
                      <ul className="space-y-2">
                        {competitor.strengths.map((strength, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span>{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5" />
                        Key Weaknesses
                      </h4>
                      <ul className="space-y-2">
                        {competitor.weaknesses.map((weakness, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                            <span>{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Additional Details */}
                  {(competitor.technology_stack || competitor.customer_segments || competitor.financial_metrics) && (
                    <div className="border-t pt-6">
                      <div className="grid md:grid-cols-3 gap-6">
                        {competitor.technology_stack && (
                          <div>
                            <h4 className="font-semibold text-blue-700 mb-2">Technology Stack</h4>
                            <div className="flex flex-wrap gap-1">
                              {competitor.technology_stack.map((tech, i) => (
                                <Badge key={i} variant="outline" className="text-xs">
                                  {tech}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {competitor.customer_segments && (
                          <div>
                            <h4 className="font-semibold text-orange-700 mb-2">Customer Segments</h4>
                            <div className="flex flex-wrap gap-1">
                              {competitor.customer_segments.map((segment, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  {segment}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {competitor.financial_metrics && (
                          <div>
                            <h4 className="font-semibold text-purple-700 mb-2">Financial Metrics</h4>
                            <div className="text-xs space-y-1">
                              <div>Revenue: {competitor.financial_metrics.annual_revenue}</div>
                              <div>Growth: {competitor.financial_metrics.growth_rate}</div>
                              <div>Valuation: {competitor.financial_metrics.valuation}</div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Recent Developments */}
                  {competitor.recent_developments && (
                    <div className="border-t pt-4 mt-4">
                      <h4 className="font-semibold text-gray-700 mb-2">Recent Developments</h4>
                      <ul className="text-sm space-y-1">
                        {competitor.recent_developments.map((development, i) => (
                          <li key={i} className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            {development}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="personas" className="space-y-6">
          <div className="grid gap-6">
            {data.userPersonas.map((persona, index) => (
              <Card key={index} className="overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                        <Users className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <CardTitle className="text-xl">{persona.name}</CardTitle>
                        <CardDescription className="text-sm">{persona.description}</CardDescription>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-indigo-100 text-indigo-800">
                      {persona.psychographics?.technology_comfort || 'Tech User'}
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent className="p-6">
                  {/* Demographics & Psychographics */}
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
                        <User className="w-4 h-4" />
                        Demographics
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Age:</span>
                          <span className="font-medium">{persona.demographics.age}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Income:</span>
                          <span className="font-medium">{persona.demographics.income}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Education:</span>
                          <span className="font-medium">{persona.demographics.education || 'College+'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Location:</span>
                          <span className="font-medium">{persona.demographics.location}</span>
                        </div>
                      </div>
                      
                      {/* Job Titles */}
                      {persona.demographics.job_titles && (
                        <div className="mt-3">
                          <span className="text-gray-600 text-sm">Typical Roles:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {persona.demographics.job_titles.slice(0, 3).map((title, i) => (
                              <Badge key={i} variant="outline" className="text-xs">
                                {title}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-purple-800 mb-3 flex items-center gap-2">
                        <Brain className="w-4 h-4" />
                        Psychographics
                      </h4>
                      
                      {/* Personality Traits */}
                      {persona.psychographics?.personality_traits && (
                        <div className="mb-3">
                          <span className="text-gray-600 text-sm">Personality:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {persona.psychographics.personality_traits.map((trait, i) => (
                              <Badge key={i} variant="secondary" className="text-xs bg-purple-100 text-purple-700">
                                {trait}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* Values */}
                      {persona.psychographics?.values && (
                        <div className="mb-3">
                          <span className="text-gray-600 text-sm">Core Values:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {persona.psychographics.values.slice(0, 4).map((value, i) => (
                              <Badge key={i} variant="outline" className="text-xs">
                                {value}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="text-sm">
                        <span className="text-gray-600">Tech Comfort:</span>
                        <span className="font-medium ml-2">{persona.psychographics?.technology_comfort || 'Intermediate'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Pain Points & Motivations */}
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div>
                      <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5" />
                        Key Pain Points
                      </h4>
                      <ul className="space-y-2">
                        {(persona.painPoints || persona.pain_points || []).map((pain, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                            <span>{pain}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-green-700 mb-3 flex items-center gap-2">
                        <Target className="w-5 h-5" />
                        Core Motivations
                      </h4>
                      <ul className="space-y-2">
                        {persona.motivations.map((motivation, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <Target className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span>{motivation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Goals & Decision Process */}
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-green-800 mb-3 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" />
                        Primary Goals
                      </h4>
                      <ul className="space-y-1 text-sm">
                        {(persona.goals || []).map((goal, i) => (
                          <li key={i} className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            {goal}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="bg-orange-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-orange-800 mb-3 flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        Decision Process
                      </h4>
                      {persona.decision_process ? (
                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="text-gray-600">Research Phase:</span>
                            <p className="font-medium">{persona.decision_process.research_phase}</p>
                          </div>
                          <div>
                            <span className="text-gray-600">Influence Level:</span>
                            <Badge variant="outline" className="ml-2 text-xs">
                              {persona.decision_process.influence_level}
                            </Badge>
                          </div>
                          <div>
                            <span className="text-gray-600">Budget Authority:</span>
                            <Badge variant={persona.decision_process.budget_authority ? "default" : "secondary"} className="ml-2 text-xs">
                              {persona.decision_process.budget_authority ? "Yes" : "No"}
                            </Badge>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-gray-600">Methodical evaluation process with focus on ROI and reliability</p>
                      )}
                    </div>
                  </div>

                  {/* Preferred Channels & Content */}
                  <div className="border-t pt-6">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold text-blue-700 mb-3 flex items-center gap-2">
                          <MessageSquare className="w-4 h-4" />
                          Preferred Channels
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {(persona.preferred_channels || [
                            "Professional networks",
                            "Industry publications", 
                            "Online communities",
                            "Conferences"
                          ]).map((channel, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {channel}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-purple-700 mb-3 flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Content Preferences
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {(persona.content_preferences || [
                            "Case studies",
                            "Product demos",
                            "Technical docs",
                            "ROI analysis"
                          ]).map((content, i) => (
                            <Badge key={i} variant="secondary" className="text-xs bg-purple-100 text-purple-700">
                              {content}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="opportunities" className="space-y-6">
          <div className="grid gap-6">
            {data.businessOpportunities.map((opportunity, index) => (
              <Card key={index} className="overflow-hidden">
                <CardContent className="p-0">
                  {/* Header Section */}
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border-b">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">{opportunity.title}</h3>
                          <Badge className={getPriorityColor(opportunity.potential)}>
                            {opportunity.potential.toUpperCase()} POTENTIAL
                          </Badge>
                        </div>
                        <p className="text-gray-700 mb-4 leading-relaxed">{opportunity.description}</p>
                        <div className="flex items-center gap-6 text-sm">
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4 text-blue-600" />
                            <span className="font-medium">Timeline: {opportunity.timeframe}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-green-600" />
                            <span className="font-medium">Market Size: {opportunity.investment}</span>
                          </div>
                        </div>
                      </div>
                      <Lightbulb className="w-10 h-10 text-yellow-500 ml-4" />
                    </div>
                  </div>

                  {/* Detailed Content */}
                  <div className="p-6 space-y-6">
                    {/* Market Drivers */}
                    {opportunity.market_drivers && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <TrendingUp className="w-5 h-5 text-green-600" />
                          Market Drivers
                        </h4>
                        <ul className="space-y-2">
                          {opportunity.market_drivers.map((driver, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <ArrowRight className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span>{driver}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Competitive Advantages */}
                    {opportunity.competitive_advantages && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <Shield className="w-5 h-5 text-blue-600" />
                          Competitive Advantages
                        </h4>
                        <ul className="space-y-2">
                          {opportunity.competitive_advantages.map((advantage, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <CheckCircle className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                              <span>{advantage}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Revenue Streams */}
                    {opportunity.revenue_streams && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <DollarSign className="w-5 h-5 text-green-600" />
                          Revenue Streams
                        </h4>
                        <ul className="space-y-2">
                          {opportunity.revenue_streams.map((stream, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <ArrowRight className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                              <span>{stream}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Key Metrics */}
                    {opportunity.key_metrics && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <BarChart3 className="w-5 h-5 text-purple-600" />
                          Key Metrics
                        </h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="bg-gray-50 p-3 rounded-lg">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Growth Rate</div>
                            <div className="text-lg font-bold text-green-600">{opportunity.key_metrics.market_growth_rate}</div>
                          </div>
                          <div className="bg-gray-50 p-3 rounded-lg">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">CAC</div>
                            <div className="text-lg font-bold text-blue-600">{opportunity.key_metrics.customer_acquisition_cost}</div>
                          </div>
                          <div className="bg-gray-50 p-3 rounded-lg">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">LTV</div>
                            <div className="text-lg font-bold text-purple-600">{opportunity.key_metrics.lifetime_value}</div>
                          </div>
                          <div className="bg-gray-50 p-3 rounded-lg">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Gross Margin</div>
                            <div className="text-lg font-bold text-orange-600">{opportunity.key_metrics.gross_margin}</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Strategic Recommendations */}
                    {opportunity.strategic_recommendations && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                          <Target className="w-5 h-5 text-red-600" />
                          Strategic Recommendations
                        </h4>
                        <ul className="space-y-2">
                          {opportunity.strategic_recommendations.map((recommendation, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              <Target className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                              <span>{recommendation}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="risks" className="space-y-6">
          {/* Risk Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Overall Risk Level</p>
                    <Badge className={`mt-1 ${getRiskColor(data.riskAssessment.overall)}`}>
                      {data.riskAssessment.overall.toUpperCase()}
                    </Badge>
                  </div>
                  <Shield className="w-8 h-8 text-red-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Risk Score</p>
                    <p className="text-2xl font-bold text-red-600">{data.riskAssessment.risk_score}/10</p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-red-500" />
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Confidence Level</p>
                    <p className="text-lg font-semibold text-green-600 capitalize">{data.riskAssessment.confidence_level}</p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Risk Matrix */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                Risk Matrix
              </CardTitle>
              <CardDescription>
                Risk categorization based on probability and impact
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <h4 className="font-semibold text-red-800 mb-2">High Probability, High Impact</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.risk_matrix.high_probability_high_impact.map((risk, i) => (
                      <li key={i} className="text-sm text-red-700">• {risk}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h4 className="font-semibold text-yellow-800 mb-2">Low Probability, High Impact</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.risk_matrix.low_probability_high_impact.map((risk, i) => (
                      <li key={i} className="text-sm text-yellow-700">• {risk}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
                  <h4 className="font-semibold text-orange-800 mb-2">High Probability, Low Impact</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.risk_matrix.high_probability_low_impact.length > 0 ? 
                      data.riskAssessment.risk_matrix.high_probability_low_impact.map((risk, i) => (
                        <li key={i} className="text-sm text-orange-700">• {risk}</li>
                      )) : 
                      <li className="text-sm text-gray-500">No risks in this category</li>
                    }
                  </ul>
                </div>
                
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">Low Probability, Low Impact</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.risk_matrix.low_probability_low_impact.map((risk, i) => (
                      <li key={i} className="text-sm text-green-700">• {risk}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Detailed Risk Factors */}
          <div className="space-y-6">
            {data.riskAssessment.factors.map((factor, index) => (
              <Card key={index} className="overflow-hidden">
                <CardContent className="p-0">
                  {/* Risk Header */}
                  <div className={`p-6 border-b ${factor.level === 'high' ? 'bg-red-50' : factor.level === 'medium' ? 'bg-yellow-50' : 'bg-green-50'}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">{factor.factor}</h3>
                          <Badge className={getRiskColor(factor.level)}>
                            {factor.level.toUpperCase()}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {factor.time_horizon}
                          </Badge>
                        </div>
                        <p className="text-gray-700 mb-4 leading-relaxed">{factor.description}</p>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                          <div className="flex items-center gap-2">
                            <BarChart3 className="w-4 h-4 text-blue-600" />
                            <span className="font-medium">Probability: {(factor.probability * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 text-red-600" />
                            <span className="font-medium">Impact: {factor.impact_score}/10</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-purple-600" />
                            <span className="font-medium">Timeline: {factor.time_horizon}</span>
                          </div>
                        </div>
                      </div>
                      <AlertTriangle className={`w-10 h-10 ml-4 ${factor.level === 'high' ? 'text-red-500' : factor.level === 'medium' ? 'text-yellow-500' : 'text-green-500'}`} />
                    </div>
                  </div>

                  {/* Risk Details */}
                  <div className="p-6 space-y-6">
                    {/* Risk Indicators */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-orange-600" />
                        Risk Indicators
                      </h4>
                      <ul className="space-y-2">
                        {factor.indicators.map((indicator, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <ArrowRight className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                            <span>{indicator}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Mitigation Strategies */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-blue-600" />
                        Mitigation Strategies
                      </h4>
                      <ul className="space-y-2">
                        {factor.mitigation_strategies.map((strategy, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <CheckCircle className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                            <span>{strategy}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Contingency Plans */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <Zap className="w-5 h-5 text-purple-600" />
                        Contingency Plans
                      </h4>
                      <ul className="space-y-2">
                        {factor.contingency_plans.map((plan, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm">
                            <Zap className="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
                            <span>{plan}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Monitoring Schedule */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Risk Monitoring Schedule
              </CardTitle>
              <CardDescription>
                Regular monitoring activities to track risk evolution
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">Daily</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.monitoring_schedule.daily.map((item, i) => (
                      <li key={i} className="text-sm text-blue-700">• {item}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-semibold text-green-800 mb-2">Weekly</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.monitoring_schedule.weekly.map((item, i) => (
                      <li key={i} className="text-sm text-green-700">• {item}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <h4 className="font-semibold text-yellow-800 mb-2">Monthly</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.monitoring_schedule.monthly.map((item, i) => (
                      <li key={i} className="text-sm text-yellow-700">• {item}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <h4 className="font-semibold text-purple-800 mb-2">Quarterly</h4>
                  <ul className="space-y-1">
                    {data.riskAssessment.monitoring_schedule.quarterly.map((item, i) => (
                      <li key={i} className="text-sm text-purple-700">• {item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="financials" className="space-y-6">
          {/* Revenue Projections and Key Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Revenue Projections
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.financialProjections.revenue}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`} />
                    <Tooltip formatter={(value) => [`$${(value / 1000000).toFixed(1)}M`, '']} />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="conservative" 
                      stroke="#3B82F6" 
                      strokeWidth={2}
                      name="Conservative"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="optimistic" 
                      stroke="#10B981" 
                      strokeWidth={2}
                      name="Optimistic"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Customer Growth Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {data.financialProjections.revenue[4].customers.conservative.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">Conservative Customers (2028)</div>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {data.financialProjections.revenue[4].customers.optimistic.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">Optimistic Customers (2028)</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        ${data.financialProjections.key_metrics.lifetime_value.year_5.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">Customer LTV (Year 5)</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">
                        ${data.financialProjections.key_metrics.customer_acquisition_cost.year_5.toLocaleString()}
                      </div>
                      <div className="text-sm text-gray-600">CAC (Year 5)</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Investment Requirements and Cost Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Investment Requirements
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                    <div className="text-3xl font-bold text-blue-600">
                      ${(data.financialProjections.investment_requirements.total_funding_needed / 1000000).toFixed(0)}M
                    </div>
                    <div className="text-sm text-gray-600">Total Funding Required</div>
                  </div>
                  <div className="space-y-3">
                    {data.financialProjections.investment_requirements.funding_rounds.map((round, index) => (
                      <div key={index} className="flex justify-between items-center p-3 border rounded-lg">
                        <div>
                          <div className="font-semibold">{round.round}</div>
                          <div className="text-sm text-gray-600">{round.timeline}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-green-600">
                            ${(round.amount / 1000000).toFixed(0)}M
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Cost Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsPieChart>
                    <Pie
                      data={data.financialProjections.costs}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ category, percentage }) => `${category}: ${percentage}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="amount"
                    >
                      {data.financialProjections.costs.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`$${(value / 1000000).toFixed(1)}M`, 'Amount']} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Profitability Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Profitability Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-700">Break-even Point</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Conservative:</span>
                      <span className="font-semibold">{data.financialProjections.profitability_analysis.break_even_point.conservative}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Optimistic:</span>
                      <span className="font-semibold">{data.financialProjections.profitability_analysis.break_even_point.optimistic}</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-700">Gross Margin Evolution</h4>
                  <div className="space-y-2">
                    {Object.entries(data.financialProjections.profitability_analysis.gross_margin).map(([year, margin]) => (
                      <div key={year} className="flex justify-between">
                        <span className="text-sm text-gray-600">{year.replace('_', ' ')}:</span>
                        <span className="font-semibold">{(margin * 100).toFixed(0)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-700">Operating Margin</h4>
                  <div className="space-y-2">
                    {Object.entries(data.financialProjections.profitability_analysis.operating_margin).map(([year, margin]) => (
                      <div key={year} className="flex justify-between">
                        <span className="text-sm text-gray-600">{year.replace('_', ' ')}:</span>
                        <span className={`font-semibold ${margin >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {(margin * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* ROI Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                ROI Analysis & Sensitivity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-700">Investor Returns</h4>
                  <div className="space-y-3">
                    <div className="p-3 bg-green-50 rounded-lg">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">3-Year ROI:</span>
                        <span className="font-bold text-green-600">
                          {data.financialProjections.roi_analysis.investor_returns['3_year_roi']}x
                        </span>
                      </div>
                    </div>
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">5-Year ROI:</span>
                        <span className="font-bold text-blue-600">
                          {data.financialProjections.roi_analysis.investor_returns['5_year_roi']}x
                        </span>
                      </div>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-lg">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">IRR:</span>
                        <span className="font-bold text-purple-600">
                          {(data.financialProjections.roi_analysis.investor_returns.irr * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-700">Sensitivity Analysis</h4>
                  <div className="space-y-3">
                    <div className="p-3 border border-green-200 rounded-lg">
                      <div className="font-semibold text-green-700 mb-2">Best Case Scenario</div>
                      <div className="text-sm space-y-1">
                        <div>Revenue: +{((data.financialProjections.roi_analysis.sensitivity_analysis.best_case.revenue_multiplier - 1) * 100).toFixed(0)}%</div>
                        <div>Costs: {((1 - data.financialProjections.roi_analysis.sensitivity_analysis.best_case.cost_multiplier) * 100).toFixed(0)}%</div>
                        <div className="font-bold">ROI: {data.financialProjections.roi_analysis.sensitivity_analysis.best_case.roi}x</div>
                      </div>
                    </div>
                    <div className="p-3 border border-red-200 rounded-lg">
                      <div className="font-semibold text-red-700 mb-2">Worst Case Scenario</div>
                      <div className="text-sm space-y-1">
                        <div>Revenue: {((data.financialProjections.roi_analysis.sensitivity_analysis.worst_case.revenue_multiplier - 1) * 100).toFixed(0)}%</div>
                        <div>Costs: +{((data.financialProjections.roi_analysis.sensitivity_analysis.worst_case.cost_multiplier - 1) * 100).toFixed(0)}%</div>
                        <div className="font-bold">ROI: {data.financialProjections.roi_analysis.sensitivity_analysis.worst_case.roi}x</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
        <Button onClick={onNewAnalysis} size="lg">
          <RefreshCw className="w-4 h-4 mr-2" />
          Analyze Another Keyword
        </Button>
        
        <Button variant="outline" size="lg">
          <FileText className="w-4 h-4 mr-2" />
          Save to Dashboard
        </Button>
      </div>
    </div>
  );
}