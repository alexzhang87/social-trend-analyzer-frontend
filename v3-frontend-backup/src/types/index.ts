// User and Authentication Types
export interface User {
  id: string
  email: string
  name: string
  avatar?: string
  role: 'user' | 'admin'
  createdAt: string
  updatedAt: string
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

// Expert Persona Types
export interface ExpertPersona {
  id: string
  name: string
  title: string
  description: string
  expertise: string[]
  avatar: string
  personality: {
    tone: 'professional' | 'friendly' | 'analytical' | 'creative'
    style: 'formal' | 'casual' | 'technical' | 'conversational'
    approach: 'strategic' | 'tactical' | 'innovative' | 'practical'
  }
  specializations: string[]
  experience: string
  isActive: boolean
}

// Chat and Conversation Types
export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: string
  expertPersona?: ExpertPersona
  metadata?: {
    sources?: string[]
    confidence?: number
    processingTime?: number
    tokens?: number
  }
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  expertPersona: ExpertPersona
  createdAt: string
  updatedAt: string
  status: 'active' | 'archived' | 'deleted'
  tags: string[]
  summary?: string
}

export interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  isLoading: boolean
  isTyping: boolean
  error: string | null
}

// Business Analysis Types
export interface BusinessIdea {
  id: string
  title: string
  description: string
  industry: string
  targetMarket: string
  problemStatement: string
  solution: string
  uniqueValueProposition: string
  revenueModel: string
  competitiveAdvantage: string
  createdAt: string
  updatedAt: string
}

export interface MarketAnalysis {
  id: string
  businessIdeaId: string
  marketSize: {
    tam: number // Total Addressable Market
    sam: number // Serviceable Addressable Market
    som: number // Serviceable Obtainable Market
  }
  targetAudience: {
    demographics: string[]
    psychographics: string[]
    painPoints: string[]
    behaviors: string[]
  }
  competitors: Competitor[]
  marketTrends: string[]
  opportunities: string[]
  threats: string[]
  recommendations: string[]
  confidence: number
  createdAt: string
}

export interface Competitor {
  id: string
  name: string
  description: string
  strengths: string[]
  weaknesses: string[]
  marketShare: number
  pricing: string
  website?: string
  fundingStage?: string
}

export interface FinancialProjection {
  id: string
  businessIdeaId: string
  timeframe: '1year' | '3years' | '5years'
  revenue: MonthlyProjection[]
  expenses: MonthlyProjection[]
  profitability: MonthlyProjection[]
  cashFlow: MonthlyProjection[]
  keyMetrics: {
    breakEvenMonth: number
    totalInvestmentNeeded: number
    projectedROI: number
    customerAcquisitionCost: number
    lifetimeValue: number
  }
  assumptions: string[]
  risks: string[]
  createdAt: string
}

export interface MonthlyProjection {
  month: number
  value: number
  growth: number
}

// AI Orchestration Types
export interface AIRequest {
  id: string
  type: 'chat' | 'analysis' | 'projection' | 'research'
  input: any
  expertPersona?: ExpertPersona
  context?: {
    conversationId?: string
    businessIdeaId?: string
    previousAnalysis?: string[]
  }
  priority: 'low' | 'medium' | 'high'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  createdAt: string
  completedAt?: string
}

export interface AIResponse {
  id: string
  requestId: string
  content: any
  metadata: {
    model: string
    tokens: number
    processingTime: number
    confidence: number
    sources?: string[]
  }
  status: 'success' | 'error'
  error?: string
  createdAt: string
}

// UI Component Types
export interface SelectOption {
  value: string
  label: string
  description?: string
  icon?: string
}

export interface TabItem {
  id: string
  label: string
  content: React.ReactNode
  icon?: string
  disabled?: boolean
}

export interface ChartData {
  name: string
  value: number
  color?: string
  [key: string]: any
}

export interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  render?: (value: any, row: any) => React.ReactNode
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
  pagination?: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

export interface PaginationParams {
  page?: number
  limit?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  search?: string
  filters?: Record<string, any>
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'chat' | 'notification' | 'status' | 'error'
  payload: any
  timestamp: string
  id?: string
}

export interface WebSocketState {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  lastMessage: WebSocketMessage | null
}

// Form Types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'file'
  placeholder?: string
  required?: boolean
  validation?: {
    min?: number
    max?: number
    pattern?: string
    custom?: (value: any) => string | null
  }
  options?: SelectOption[]
  description?: string
}

export interface FormState {
  values: Record<string, any>
  errors: Record<string, string>
  touched: Record<string, boolean>
  isSubmitting: boolean
  isValid: boolean
}

// Notification Types
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
  createdAt: string
}

// Theme Types
export interface Theme {
  name: string
  colors: {
    primary: string
    secondary: string
    accent: string
    background: string
    foreground: string
    muted: string
    border: string
  }
  fonts: {
    sans: string
    mono: string
    display: string
  }
  spacing: Record<string, string>
  borderRadius: Record<string, string>
}