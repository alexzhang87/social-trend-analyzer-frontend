import { TrendCluster } from "../components/trend-analyzer";

export const mockTrendData: TrendCluster[] = [
  {
    cluster_id: "1",
    title: "AI-Powered Personal Assistants",
    category: "Technology & AI",
    hot_score: 92,
    platforms: ["x", "reddit"],
    keywords: ["AI assistant", "ChatGPT", "productivity", "automation"],
    date: "2025-08-11",
    trend_history: [
      { date: "2025-08-05", score: 75 },
      { date: "2025-08-06", score: 78 },
      { date: "2025-08-07", score: 82 },
      { date: "2025-08-08", score: 80 },
      { date: "2025-08-09", score: 85 },
      { date: "2025-08-10", score: 88 },
      { date: "2025-08-11", score: 92 },
    ],
    pain_points: [
      {
        text: "Users struggle with the complexity of setting up AI assistants.",
        evidence: [
          {
            text: "I spent hours trying to configure the API keys, the documentation is not clear.",
            author: "user123",
            platform: "reddit",
            url: "#"
          }
        ],
        intent: "Ease of use",
        severity: 80,
        confidence: 0.95
      }
    ],
    opportunities: [
      {
        text: "Develop a plug-and-play solution with pre-configured templates.",
        impact: 9,
        effort: 6
      },
      {
        text: "Create an AI-powered onboarding flow that personalizes the setup process.",
        impact: 8,
        effort: 8
      }
    ],
    mvp_1week: {
      goal: "Launch a landing page with a waitlist for the simplified AI assistant.",
      days: ["Day 1-2: Design", "Day 3-5: Development", "Day 6-7: Deploy & Announce"],
      resources: "1 developer, 1 designer",
      budget_usd: 500,
      kpi: "100 signups"
    },
    emotion_analysis: {
      joy: 180,
      sadness: 20,
      anger: 15,
      sarcasm: 35,
      neutral: 50
    }
  },
  {
    cluster_id: "2",
    title: "Sustainable and Eco-Friendly Fashion",
    category: "Sustainability & Green Tech",
    hot_score: 85,
    platforms: ["reddit"],
    keywords: ["sustainable fashion", "eco-friendly", "thrift", "upcycling"],
    date: "2025-07-25",
    trend_history: [
      { date: "2025-07-19", score: 80 },
      { date: "2025-07-20", score: 82 },
      { date: "2025-07-21", score: 85 },
      { date: "2025-07-22", score: 83 },
      { date: "2025-07-23", score: 81 },
      { date: "2025-07-24", score: 84 },
      { date: "2025-07-25", score: 85 },
    ],
    pain_points: [
        {
            text: "Consumers find it difficult to verify the sustainability claims of brands.",
            evidence: [
                {
                    text: "So many brands greenwash, how can I trust them?",
                    author: "eco_warrior",
                    platform: "reddit",
                    url: "#"
                }
            ],
            intent: "Brand transparency",
            severity: 70,
            confidence: 0.90
        }
    ],
    opportunities: [
        {
            text: "Create a browser extension that rates fashion brands' sustainability.",
            impact: 8,
            effort: 7
        }
    ],
    mvp_1week: {
        goal: "Build a prototype of the browser extension for Chrome.",
        days: ["Day 1-3: Data collection", "Day 4-6: Extension development", "Day 7: Internal testing"],
        resources: "2 developers",
        budget_usd: 1000,
        kpi: "Successfully rate 10 major brands"
    },
    emotion_analysis: {
      joy: 250,
      sadness: 10,
      anger: 5,
      sarcasm: 15,
      neutral: 120
    }
  },
  {
    cluster_id: "3",
    title: "Remote Work Burnout Solutions",
    category: "Business & Marketing",
    hot_score: 88,
    platforms: ["x"],
    keywords: ["remote work", "wfh", "burnout", "mental health"],
    date: "2025-06-14",
    trend_history: [
      { date: "2025-06-08", score: 90 },
      { date: "2025-06-09", score: 88 },
      { date: "2025-06-10", score: 85 },
      { date: "2025-06-11", score: 86 },
      { date: "2025-06-12", score: 89 },
      { date: "2025-06-13", score: 87 },
      { date: "2025-06-14", score: 88 },
    ],
    pain_points: [
        {
            text: "Employees feel isolated and disconnected from their teams.",
            evidence: [
                {
                    text: "I miss the random chats by the water cooler. It's just endless Zoom calls now.",
                    author: "dev_dave",
                    platform: "x",
                    url: "#"
                }
            ],
            intent: "Team connection",
            severity: 90,
            confidence: 0.88
        }
    ],
    opportunities: [
        {
            text: "An app for virtual team-building activities and non-work-related chats.",
            impact: 7,
            effort: 5
        }
    ],
    mvp_1week: {
        goal: "Develop a functional prototype for a 'virtual coffee break' feature.",
        days: ["Day 1: Concept", "Day 2-4: Prototyping", "Day 5-7: User testing with a small team"],
        resources: "1 PM, 1 developer",
        budget_usd: 700,
        kpi: "Positive feedback from 80% of testers"
    },
    emotion_analysis: {
      joy: 50,
      sadness: 150,
      anger: 80,
      sarcasm: 90,
      neutral: 30
    }
  }
];
