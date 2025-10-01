"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Brain, MessageCircle, TrendingUp, Users, Zap, Clock, Star, ArrowRight, Lightbulb, Target, BarChart3, Cog } from 'lucide-react'
import { toast } from "sonner"

interface ExpertRecommendation {
  expert_type: string
  confidence: number
  reasoning: string
  estimated_session_length: number
}

interface ConsultationSession {
  session_id: string
  user_id: string
  idea_summary: string
  expert_type: string
  status: string
  created_at: string
  updated_at: string
  messages: ChatMessage[]
  context_data: any
}

interface ChatMessage {
  role: string
  content: string
  timestamp: string
}

interface ExpertChatResponse {
  session_id: string
  message_id: string
  response: string
  expert_type: string
  confidence_score: number
  sources: any[]
  follow_up_questions: string[]
  timestamp: string
}

const expertTypes = {
  business_strategist: {
    name: "Business Strategy",
    description: "Business model & growth strategy",
    icon: <TrendingUp className="h-5 w-5" />,
    color: "bg-blue-500",
    expertise: ["Business Model", "Growth Strategy", "Market Analysis"]
  },
  technical_advisor: {
    name: "Technical Expert",
    description: "Architecture & development strategy", 
    icon: <Cog className="h-5 w-5" />,
    color: "bg-green-500",
    expertise: ["Architecture", "Development", "Scalability"]
  },
  market_researcher: {
    name: "Market Research",
    description: "Market analysis & validation",
    icon: <BarChart3 className="h-5 w-5" />,
    color: "bg-purple-500",
    expertise: ["Market Analysis", "Validation", "PMF"]
  },
  product_manager: {
    name: "Product Strategy", 
    description: "Product strategy & user experience",
    icon: <Target className="h-5 w-5" />,
    color: "bg-orange-500",
    expertise: ["Product Strategy", "UX", "Roadmap"]
  }
}

export default function AIExpertConsultation() {
  const [ideaText, setIdeaText] = useState('')
  const [recommendations, setRecommendations] = useState<ExpertRecommendation[]>([])
  const [sessions, setSessions] = useState<ConsultationSession[]>([])
  const [activeSession, setActiveSession] = useState<ConsultationSession | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [currentMessage, setCurrentMessage] = useState('')
  const [isChatting, setIsChatting] = useState(false)

  // Load existing sessions on component mount
  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/ai-expert/sessions', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setSessions(data.sessions || [])
      }
    } catch (error) {
      console.error('Error loading sessions:', error)
    }
  }

  const getExpertRecommendations = async () => {
    if (!ideaText.trim()) {
      toast.error("Please enter your business idea first")
      return
    }

    setIsLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/ai-expert/recommend-expert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          idea_text: ideaText,
          pmf_data: null, // Could be populated from previous analysis
          analysis_data: null,
          consultation_type: 'general'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setRecommendations(data)
        setShowRecommendations(true)
        toast.success("Expert recommendations generated!")
      } else {
        throw new Error('Failed to get recommendations')
      }
    } catch (error) {
      console.error('Error getting recommendations:', error)
      toast.error("Failed to get expert recommendations")
    } finally {
      setIsLoading(false)
    }
  }

  const startConsultation = async (expertType: string) => {
    setIsLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/ai-expert/start-consultation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          idea_text: ideaText,
          pmf_data: null,
          analysis_data: null,
          consultation_type: expertType
        })
      })

      if (response.ok) {
        const session = await response.json()
        setActiveSession(session)
        setSessions(prev => [session, ...prev])
        setShowRecommendations(false)
        toast.success("Consultation session started!")
      } else {
        throw new Error('Failed to start consultation')
      }
    } catch (error) {
      console.error('Error starting consultation:', error)
      toast.error("Failed to start consultation")
    } finally {
      setIsLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!currentMessage.trim() || !activeSession) return

    setIsChatting(true)
    const userMessage = currentMessage
    setCurrentMessage('')

    // Add user message to UI immediately
    const newUserMessage: ChatMessage = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }

    setActiveSession(prev => prev ? {
      ...prev,
      messages: [...prev.messages, newUserMessage]
    } : null)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/ai-expert/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: activeSession.session_id,
          message: userMessage,
          context: null
        })
      })

      if (response.ok) {
        const chatResponse: ExpertChatResponse = await response.json()
        
        // Add assistant message to UI
        const assistantMessage: ChatMessage = {
          role: 'assistant',
          content: chatResponse.response,
          timestamp: chatResponse.timestamp
        }

        setActiveSession(prev => prev ? {
          ...prev,
          messages: [...prev.messages, assistantMessage]
        } : null)

        toast.success("Expert response received!")
      } else {
        throw new Error('Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error("Failed to send message")
    } finally {
      setIsChatting(false)
    }
  }

  const openSession = (session: ConsultationSession) => {
    setActiveSession(session)
  }

  const getExpertInfo = (expertType: string) => {
    return expertTypes[expertType as keyof typeof expertTypes] || expertTypes.business_strategist
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-6">
        {/* Simplified Header */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-3">
            <Brain className="h-8 w-8 text-blue-600 mr-2" />
            <h1 className="text-2xl font-bold text-gray-900">AI Expert Consultation</h1>
          </div>
          <p className="text-gray-600">Get expert advice for your business idea</p>
        </div>

        {!activeSession ? (
          <div className="max-w-3xl mx-auto">
            {/* Simplified Idea Input */}
            <Card className="mb-6">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center">
                  <Lightbulb className="h-4 w-4 mr-2 text-yellow-500" />
                  Describe your business idea
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  placeholder="Tell us about your business idea, target market, or challenges..."
                  value={ideaText}
                  onChange={(e) => setIdeaText(e.target.value)}
                  className="min-h-[100px] mb-4"
                />
                <Button 
                  onClick={getExpertRecommendations}
                  disabled={isLoading || !ideaText.trim()}
                  className="w-full"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Brain className="h-4 w-4 mr-2" />
                      Get Expert Recommendations
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Simplified Expert Recommendations */}
            {showRecommendations && recommendations.length > 0 && (
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg flex items-center">
                    <Star className="h-4 w-4 mr-2 text-yellow-500" />
                    Recommended Experts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3">
                    {recommendations.map((rec, index) => {
                      const expertInfo = getExpertInfo(rec.expert_type)
                      return (
                        <Card key={index} className="border hover:border-blue-300 transition-colors cursor-pointer">
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className={`p-2 rounded-lg ${expertInfo.color} text-white`}>
                                  {expertInfo.icon}
                                </div>
                                <div>
                                  <h3 className="font-semibold text-gray-900">{expertInfo.name}</h3>
                                  <p className="text-sm text-gray-600">{expertInfo.description}</p>
                                  <div className="flex gap-1 mt-1">
                                    {expertInfo.expertise.slice(0, 2).map((skill, i) => (
                                      <Badge key={i} variant="secondary" className="text-xs px-2 py-0">
                                        {skill}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className="flex items-center mb-1">
                                  <span className="text-xs text-gray-500 mr-1">Match</span>
                                  <Progress value={rec.confidence * 100} className="w-16 h-2" />
                                </div>
                                <Button 
                                  size="sm"
                                  onClick={() => startConsultation(rec.expert_type)}
                                  className="h-8"
                                >
                                  Start Chat
                                  <ArrowRight className="h-3 w-3 ml-1" />
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Simplified Previous Sessions */}
            {sessions.length > 0 && (
              <Card className="mt-6">
                <CardHeader className="pb-4">
                  <CardTitle className="text-lg flex items-center">
                    <Clock className="h-4 w-4 mr-2 text-gray-500" />
                    Previous Sessions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {sessions.slice(0, 3).map((session) => {
                      const expertInfo = getExpertInfo(session.expert_type)
                      return (
                        <div 
                          key={session.session_id}
                          className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                          onClick={() => openSession(session)}
                        >
                          <div className="flex items-center space-x-3">
                            <div className={`p-1.5 rounded ${expertInfo.color} text-white`}>
                              {expertInfo.icon}
                            </div>
                            <div>
                              <p className="font-medium text-sm">{expertInfo.name}</p>
                              <p className="text-xs text-gray-500 truncate max-w-[200px]">
                                {session.idea_summary}
                              </p>
                            </div>
                          </div>
                          <ArrowRight className="h-4 w-4 text-gray-400" />
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          /* Simplified Chat Interface */
          <div className="max-w-4xl mx-auto">
            <Card className="h-[600px] flex flex-col">
              {/* Chat Header */}
              <CardHeader className="border-b bg-gray-50 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => setActiveSession(null)}
                      className="p-1"
                    >
                      <ArrowRight className="h-4 w-4 rotate-180" />
                    </Button>
                    <div className={`p-2 rounded-lg ${getExpertInfo(activeSession.expert_type).color} text-white`}>
                      {getExpertInfo(activeSession.expert_type).icon}
                    </div>
                    <div>
                      <h3 className="font-semibold">{getExpertInfo(activeSession.expert_type).name}</h3>
                      <p className="text-xs text-gray-500">AI Expert Assistant</p>
                    </div>
                  </div>
                </div>
              </CardHeader>

              {/* Chat Messages */}
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {activeSession.messages.map((message, index) => (
                    <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[80%] p-3 rounded-lg ${
                        message.role === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>

              {/* Chat Input */}
              <div className="border-t p-4">
                <div className="flex space-x-2">
                  <Textarea
                    placeholder="Ask your question..."
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    className="min-h-[60px] resize-none"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        sendMessage()
                      }
                    }}
                  />
                  <Button 
                    onClick={sendMessage}
                    disabled={isChatting || !currentMessage.trim()}
                    className="self-end"
                  >
                    {isChatting ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      <MessageCircle className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
