import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// AI Insights API 接口类型定义
export interface TrendingOpportunity {
  title: string;
  description: string;
  growth_rate: string;
  market_size?: string;
  search_volume?: string;
  priority: 'high' | 'medium' | 'low';
  action?: string;
}

export interface GrowthPrediction {
  metric: string;
  current_value?: number;
  predicted_value?: number;
  growth_rate: string;
  confidence: string;
  timeframe: string;
}

export interface MarketIntelligence {
  trending_opportunities: TrendingOpportunity[];
  growth_predictions: GrowthPrediction[];
  market_score: number;
  last_updated: string;
  data_sources: string[];
}

export interface GrowthOpportunity {
  opportunity: string;
  description: string;
  target_persona: string;
  ltv_increase?: string;
  satisfaction_impact?: string;
  confidence: string;
  priority: 'high' | 'medium' | 'low';
}

export interface CompetitiveRisk {
  risk: string;
  description: string;
  competitor?: string;
  launched?: string;
  impact_level: 'high' | 'medium' | 'low';
  action_required?: string;
}

export interface StrategicAction {
  action: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  timeline: string;
  resources_needed?: string;
}

export interface StrategicRecommendations {
  growth_opportunities: GrowthOpportunity[];
  competitive_risks: CompetitiveRisk[];
  strategic_actions: StrategicAction[];
  relevance_score: number;
  confidence_level: number;
  last_updated: string;
}

export interface ForecastData {
  date: string;
  value: number;
}

export interface GrowthPredictions {
  forecast_data: ForecastData[];
  growth_rate: string;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  key_drivers: string[];
  risk_factors: string[];
  time_range: string;
  last_updated: string;
}

export interface CompetitiveThreat {
  competitor: string;
  threat_level: 'high' | 'medium' | 'low';
  description: string;
  action: string;
}

export interface MarketPositioning {
  current_position: string;
  competitive_advantage: string;
  differentiation: string;
}

export interface DifferentiationOpportunity {
  opportunity: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

export interface MonitoringAlert {
  alert: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
}

export interface CompetitiveAnalysis {
  competitive_threats: CompetitiveThreat[];
  market_positioning: MarketPositioning;
  differentiation_opportunities: DifferentiationOpportunity[];
  threat_level: 'high' | 'medium' | 'low';
  monitoring_alerts: MonitoringAlert[];
  last_updated: string;
}

export interface SummaryMetrics {
  total_insights: number;
  high_priority_alerts: number;
  market_score: number;
  confidence_level: number;
}

export interface DashboardData {
  market_intelligence: MarketIntelligence;
  strategic_recommendations: StrategicRecommendations;
  growth_predictions: GrowthPredictions;
  competitive_analysis: CompetitiveAnalysis;
  summary_metrics: SummaryMetrics;
  last_updated: string;
}

export interface RefreshResult {
  refreshed_at: string;
  keyword: string;
  status: 'success' | 'error';
  updated_insights?: number;
  new_opportunities?: number;
  alerts_generated?: number;
  error?: string;
}

// API 服务类
export class AIInsightsAPI {
  private static instance: AIInsightsAPI;
  private baseURL: string;

  private constructor() {
    this.baseURL = `${API_BASE_URL}/ai-insights`;
  }

  public static getInstance(): AIInsightsAPI {
    if (!AIInsightsAPI.instance) {
      AIInsightsAPI.instance = new AIInsightsAPI();
    }
    return AIInsightsAPI.instance;
  }

  // 获取市场情报
  async getMarketIntelligence(keyword?: string): Promise<MarketIntelligence> {
    try {
      const params = keyword ? { keyword } : {};
      const response = await axios.get(`${this.baseURL}/market-intelligence`, { params });
      return response.data;
    } catch (error) {
      console.error('获取市场情报失败:', error);
      throw new Error('Failed to fetch market intelligence');
    }
  }

  // 获取战略建议
  async getStrategicRecommendations(keyword?: string): Promise<StrategicRecommendations> {
    try {
      const params = keyword ? { keyword } : {};
      const response = await axios.get(`${this.baseURL}/strategic-recommendations`, { params });
      return response.data;
    } catch (error) {
      console.error('获取战略建议失败:', error);
      throw new Error('Failed to fetch strategic recommendations');
    }
  }

  // 获取增长预测
  async getGrowthPredictions(keyword?: string, timeRange: string = '3months'): Promise<GrowthPredictions> {
    try {
      const params: any = { time_range: timeRange };
      if (keyword) params.keyword = keyword;
      const response = await axios.get(`${this.baseURL}/growth-predictions`, { params });
      return response.data;
    } catch (error) {
      console.error('获取增长预测失败:', error);
      throw new Error('Failed to fetch growth predictions');
    }
  }

  // 获取竞争分析
  async getCompetitiveAnalysis(keyword?: string): Promise<CompetitiveAnalysis> {
    try {
      const params = keyword ? { keyword } : {};
      const response = await axios.get(`${this.baseURL}/competitive-analysis`, { params });
      return response.data;
    } catch (error) {
      console.error('获取竞争分析失败:', error);
      throw new Error('Failed to fetch competitive analysis');
    }
  }

  // 获取仪表板数据
  async getDashboardData(): Promise<DashboardData> {
    try {
      const response = await axios.get(`${this.baseURL}/dashboard`);
      return response.data;
    } catch (error) {
      console.error('获取仪表板数据失败:', error);
      throw new Error('Failed to fetch dashboard data');
    }
  }

  // 刷新洞察数据
  async refreshInsights(keyword?: string): Promise<RefreshResult> {
    try {
      const data = keyword ? { keyword } : {};
      const response = await axios.post(`${this.baseURL}/refresh`, data);
      return response.data;
    } catch (error) {
      console.error('刷新洞察数据失败:', error);
      throw new Error('Failed to refresh insights');
    }
  }
}

// 导出单例实例
export const aiInsightsAPI = AIInsightsAPI.getInstance();

// 便捷的钩子函数
export const useAIInsights = () => {
  return {
    getMarketIntelligence: aiInsightsAPI.getMarketIntelligence.bind(aiInsightsAPI),
    getStrategicRecommendations: aiInsightsAPI.getStrategicRecommendations.bind(aiInsightsAPI),
    getGrowthPredictions: aiInsightsAPI.getGrowthPredictions.bind(aiInsightsAPI),
    getCompetitiveAnalysis: aiInsightsAPI.getCompetitiveAnalysis.bind(aiInsightsAPI),
    getDashboardData: aiInsightsAPI.getDashboardData.bind(aiInsightsAPI),
    refreshInsights: aiInsightsAPI.refreshInsights.bind(aiInsightsAPI),
  };
};