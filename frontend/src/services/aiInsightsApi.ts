import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1';

// AI Insights API interface type definitions
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

// API service class
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

  // Get market intelligence
  async getMarketIntelligence(keyword?: string): Promise<MarketIntelligence> {
    try {
      const params = keyword ? { keyword } : {};
      const response = await axios.get(`${this.baseURL}/market-intelligence`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch market intelligence:', error);
      throw new Error('Failed to fetch market intelligence');
    }
  }

  // Get strategic recommendations
  async getStrategicRecommendations(keyword?: string): Promise<StrategicRecommendations> {
    try {
      const params = keyword ? { keyword } : {};
      const response = await axios.get(`${this.baseURL}/strategic-recommendations`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch strategic recommendations:', error);
      throw new Error('Failed to fetch strategic recommendations');
    }
  }

  // Get growth predictions
  async getGrowthPredictions(keyword?: string, timeRange: string = '3months'): Promise<GrowthPredictions> {
    try {
      const params: any = { time_range: timeRange };
      if (keyword) params.keyword = keyword;
      const response = await axios.get(`${this.baseURL}/growth-predictions`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch growth predictions:', error);
      throw new Error('Failed to fetch growth predictions');
    }
  }

  // Get competitive analysis
  async getCompetitiveAnalysis(keyword?: string): Promise<CompetitiveAnalysis> {
    try {
      const params = keyword ? { keyword } : {};
      const response = await axios.get(`${this.baseURL}/competitive-analysis`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch competitive analysis:', error);
      throw new Error('Failed to fetch competitive analysis');
    }
  }

  // Get dashboard data
  async getDashboardData(): Promise<DashboardData> {
    try {
      const response = await axios.get(`${this.baseURL}/dashboard`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      throw new Error('Failed to fetch dashboard data');
    }
  }

  // Refresh insights data
  async refreshInsights(keyword?: string): Promise<RefreshResult> {
    try {
      const data = keyword ? { keyword } : {};
      const response = await axios.post(`${this.baseURL}/refresh`, data);
      return response.data;
    } catch (error) {
      console.error('Failed to refresh insights data:', error);
      throw new Error('Failed to refresh insights');
    }
  }
}

// Export singleton instance
export const aiInsightsAPI = AIInsightsAPI.getInstance();

// Convenient hook functions
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
