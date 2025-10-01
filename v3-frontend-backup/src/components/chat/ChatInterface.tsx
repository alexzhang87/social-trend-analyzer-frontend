'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { ExpertSelector } from './ExpertSelector'
import { 
  MessageSquare, 
  Settings, 
  MoreVertical,
  Download,
  Trash2,
  RefreshCw,
  Zap,
  Brain,
  Sparkles
} from 'lucide-react'
import { Message, ExpertPersona, ChatSession } from '@/types'
import { cn } from '@/lib/utils'

interface ChatInterfaceProps {
  className?: string
}

// Mock data for experts
const mockExperts: ExpertPersona[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    title: 'Business Strategy Expert',
    description: 'Specialized in strategic planning, market analysis, and business transformation with 15+ years of consulting experience.',
    avatar: '/avatars/sarah.jpg',
    expertise: ['Business Strategy', 'Market Research', 'Strategic Planning'],
    personality: {
      tone: 'professional',
      style: 'analytical',
      traits: ['detail-oriented', 'strategic', 'data-driven']
    },
    systemPrompt: 'You are Sarah Chen, a senior business strategy consultant...',
    isActive: true
  },
  {
    id: '2',
    name: 'Marcus Rodriguez',
    title: 'Financial Planning Advisor',
    description: 'Expert in financial modeling, investment strategies, and risk management for businesses of all sizes.',
    avatar: '/avatars/marcus.jpg',
    expertise: ['Financial Planning', 'Investment Strategy', 'Risk Management'],
    personality: {
      tone: 'analytical',
      style: 'methodical',
      traits: ['precise', 'conservative', 'thorough']
    },
    systemPrompt: 'You are Marcus Rodriguez, a financial planning expert...',
    isActive: true
  },
  {
    id: '3',
    name: 'Emma Thompson',
    title: 'Marketing & Growth Specialist',
    description: 'Creative marketing strategist with expertise in digital marketing, brand development, and growth hacking.',
    avatar: '/avatars/emma.jpg',
    expertise: ['Marketing', 'Brand Strategy', 'Growth Hacking'],
    personality: {
      tone: 'creative',
      style: 'innovative',
      traits: ['creative', 'energetic', 'trend-aware']
    },
    systemPrompt: 'You are Emma Thompson, a marketing and growth expert...',
    isActive: true
  },
  {
    id: '4',
    name: 'Dr. Alex Kim',
    title: 'Technology & Innovation Consultant',
    description: 'Technology strategist specializing in digital transformation, AI implementation, and innovation management.',
    avatar: '/avatars/alex.jpg',
    expertise: ['Technology', 'AI Strategy', 'Digital Transformation'],
    personality: {
      tone: 'analytical',
      style: 'technical',
      traits: ['innovative', 'logical', 'forward-thinking']
    },
    systemPrompt: 'You are Dr. Alex Kim, a technology and innovation expert...',
    isActive: true
  }
]

export function ChatInterface({ className }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [selectedExpert, setSelectedExpert] = useState<ExpertPersona | null>(mockExperts[0])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [showSettings, setShowSettings] = useState(false)

  // Initialize session
  useEffect(() => {
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setSessionId(newSessionId)
    
    // Add welcome message
    if (selectedExpert) {
      const welcomeMessage: Message = {
        id: `msg_${Date.now()}`,
        content: `Hello! I'm ${selectedExpert.name}, your ${selectedExpert.title.toLowerCase()}. I'm here to help you with ${selectedExpert.expertise.join(', ').toLowerCase()}. What would you like to discuss today?`,
        role: 'assistant',
        timestamp: new Date(),
        expertId: selectedExpert.id,
        sessionId: newSessionId
      }
      setMessages([welcomeMessage])
    }
  }, [])

  // Auto scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Handle expert change
  const handleExpertChange = (expert: ExpertPersona) => {
    setSelectedExpert(expert)
    
    // Add transition message
    const transitionMessage: Message = {
      id: `msg_${Date.now()}`,
      content: `Hello! I'm ${expert.name}, your ${expert.title.toLowerCase()}. I've reviewed our previous conversation and I'm ready to help you with ${expert.expertise.join(', ').toLowerCase()}. How can I assist you?`,
      role: 'assistant',
      timestamp: new Date(),
      expertId: expert.id,
      sessionId: sessionId
    }
    
    setMessages(prev => [...prev, transitionMessage])
  }

  // Handle message send
  const handleSendMessage = async (content: string, attachments?: File[]) => {
    if (!content.trim() || !selectedExpert) return

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      content: content.trim(),
      role: 'user',
      timestamp: new Date(),
      sessionId: sessionId,
      attachments: attachments?.map(file => ({
        id: `att_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: file.name,
        type: file.type,
        size: file.size,
        url: URL.createObjectURL(file)
      }))
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Simulate API call to backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          expertId: selectedExpert.id,
          sessionId: sessionId,
          context: messages.slice(-5) // Send last 5 messages for context
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        content: data.response || 'I apologize, but I encountered an issue processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
        expertId: selectedExpert.id,
        sessionId: sessionId,
        metadata: data.metadata
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Add error message
      const errorMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        content: 'I apologize, but I encountered a technical issue. Please check your connection and try again.',
        role: 'assistant',
        timestamp: new Date(),
        expertId: selectedExpert.id,
        sessionId: sessionId,
        metadata: { error: true }
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // Handle message actions
  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    // You could add a toast notification here
  }

  const handleRegenerateMessage = async (messageId: string) => {
    const messageIndex = messages.findIndex(msg => msg.id === messageId)
    if (messageIndex === -1) return

    const previousUserMessage = messages[messageIndex - 1]
    if (!previousUserMessage || previousUserMessage.role !== 'user') return

    // Remove the message to regenerate and all messages after it
    setMessages(prev => prev.slice(0, messageIndex))
    
    // Resend the previous user message
    await handleSendMessage(previousUserMessage.content)
  }

  const handleFeedback = (messageId: string, type: 'like' | 'dislike') => {
    // Update message with feedback
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, feedback: type }
        : msg
    ))
    
    // Send feedback to backend
    fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messageId,
        type,
        sessionId,
        expertId: selectedExpert?.id
      })
    }).catch(console.error)
  }

  // Clear chat
  const handleClearChat = () => {
    setMessages([])
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setSessionId(newSessionId)
    
    if (selectedExpert) {
      const welcomeMessage: Message = {
        id: `msg_${Date.now()}`,
        content: `Hello! I'm ${selectedExpert.name}, your ${selectedExpert.title.toLowerCase()}. How can I help you today?`,
        role: 'assistant',
        timestamp: new Date(),
        expertId: selectedExpert.id,
        sessionId: newSessionId
      }
      setMessages([welcomeMessage])
    }
  }

  // Export chat
  const handleExportChat = () => {
    const chatData = {
      sessionId,
      expert: selectedExpert,
      messages: messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp
      })),
      exportedAt: new Date()
    }
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chat_export_${sessionId}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className={cn("flex flex-col h-full max-h-screen", className)}>
      {/* Header */}
      <Card className="border-b rounded-none border-x-0 border-t-0">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <MessageSquare className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">AI Business Consultant</CardTitle>
                <p className="text-sm text-muted-foreground">
                  {selectedExpert ? `Chatting with ${selectedExpert.name}` : 'Select an expert to start'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSettings(!showSettings)}
              >
                <Settings className="h-4 w-4" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleExportChat}
                disabled={messages.length === 0}
              >
                <Download className="h-4 w-4" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearChat}
                disabled={messages.length === 0}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Expert Selector */}
      <div className="p-4 border-b bg-muted/30">
        <ExpertSelector
          experts={mockExperts}
          selectedExpert={selectedExpert}
          onSelectExpert={handleExpertChange}
        />
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto p-4 space-y-4">
          <AnimatePresence mode="popLayout">
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <ChatMessage
                  message={message}
                  expert={selectedExpert}
                  onCopy={handleCopyMessage}
                  onRegenerate={handleRegenerateMessage}
                  onFeedback={handleFeedback}
                  isLast={index === messages.length - 1}
                />
              </motion.div>
            ))}
          </AnimatePresence>
          
          {/* Loading indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3 p-4"
            >
              <div className="p-2 bg-muted rounded-lg">
                <Brain className="h-4 w-4 animate-pulse" />
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Sparkles className="h-3 w-3 animate-spin" />
                {selectedExpert?.name} is thinking...
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="p-4">
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={isLoading || !selectedExpert}
            placeholder={
              selectedExpert 
                ? `Ask ${selectedExpert.name} anything about ${selectedExpert.expertise.join(', ').toLowerCase()}...`
                : 'Select an expert to start chatting...'
            }
          />
        </div>
      </div>
    </div>
  )
}