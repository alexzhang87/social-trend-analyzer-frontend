declare module 'react-d3-cloud';

// This file defines the TypeScript interfaces that match the new backend API response.

// Sub-interfaces for the new structured response
export interface HypeIndex {
  score: number;
  reasoning: string;
}

export interface SentimentSpectrum {
  positive: number;
  neutral: number;
  negative: number;
  questioning: number;
  total: number;
}

export interface KeyTheme {
  theme: string;
  summary: string;
  isEmerging: boolean;
}

export interface UserPersonaSnapshot {
  personas: string[];
  coreNeeds: string[];
}

export interface ActionableOpportunity {
  opportunity: string;
  description: string;
  targetPersona: string;
}

export interface TopMention {
  platform: 'X' | 'Reddit';
  author: string;
  text: string;
  url: string;
  likes: number;
  sentiment: 'Positive' | 'Negative' | 'Neutral'; // This can be refined later
}

// The main data structure for a single trend analysis result, matching the new API.
export interface TrendAnalysis {
  id: string; // A unique identifier for the trend
  title: string;
  summary: string;
  hypeIndex: HypeIndex;
  sentimentSpectrum: SentimentSpectrum;
  keyThemes: KeyTheme[];
  userPersonaSnapshot: UserPersonaSnapshot;
  actionableOpportunities: ActionableOpportunity[];
  top_mentions: TopMention[];
  keywords: string[];
  user_tier?: 'free' | 'starter' | 'pro'; // User subscription tier
}