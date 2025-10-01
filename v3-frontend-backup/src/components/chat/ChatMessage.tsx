'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Copy, ThumbsUp, ThumbsDown, RotateCcw } from 'lucide-react'
import { Message, ExpertPersona } from '@/types'
import { cn, formatTime, copyToClipboard } from '@/lib/utils'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface ChatMessageProps {
  message: Message
  isLast?: boolean
  onRegenerate?: () => void
  onFeedback?: (messageId: string, type: 'positive' | 'negative') => void
}

export function ChatMessage({ 
  message, 
  isLast = false, 
  onRegenerate, 
  onFeedback 
}: ChatMessageProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  
  const handleCopy = async () => {
    try {
      await copyToClipboard(message.content)
      // You can add a toast notification here
    } catch (error) {
      console.error('Failed to copy message:', error)
    }
  }

  const handleFeedback = (type: 'positive' | 'negative') => {
    if (onFeedback) {
      onFeedback(message.id, type)
    }
  }

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex justify-center my-4"
      >
        <div className="bg-muted/50 text-muted-foreground text-xs px-3 py-1 rounded-full">
          {message.content}
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={cn(
        "flex gap-4 mb-6",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        <Avatar className={cn(
          "h-10 w-10 border-2 transition-all duration-200",
          isUser 
            ? "border-primary/20 bg-primary/10" 
            : "border-secondary/20 bg-secondary/10"
        )}>
          {isUser ? (
            <>
              <AvatarImage src="/user-avatar.png" alt="User" />
              <AvatarFallback className="bg-primary/20 text-primary font-semibold">
                U
              </AvatarFallback>
            </>
          ) : (
            <>
              <AvatarImage 
                src={message.expertPersona?.avatar} 
                alt={message.expertPersona?.name || "AI Assistant"} 
              />
              <AvatarFallback className="bg-secondary/20 text-secondary font-semibold">
                {message.expertPersona?.name?.charAt(0) || "AI"}
              </AvatarFallback>
            </>
          )}
        </Avatar>
      </div>

      {/* Message Content */}
      <div className={cn(
        "flex-1 max-w-[80%]",
        isUser ? "flex flex-col items-end" : "flex flex-col items-start"
      )}>
        {/* Expert Info (for AI messages) */}
        {!isUser && message.expertPersona && (
          <div className="mb-2 flex items-center gap-2">
            <span className="text-sm font-medium text-secondary">
              {message.expertPersona.name}
            </span>
            <span className="text-xs text-muted-foreground">
              {message.expertPersona.title}
            </span>
          </div>
        )}

        {/* Message Bubble */}
        <Card className={cn(
          "relative transition-all duration-200 hover:shadow-md",
          isUser 
            ? "bg-primary text-primary-foreground border-primary/20" 
            : "bg-card border-border glass-card"
        )}>
          <CardContent className="p-4">
            <div className={cn(
              "prose prose-sm max-w-none",
              isUser 
                ? "prose-invert" 
                : "prose-gray dark:prose-invert"
            )}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '')
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        className="rounded-md !mt-2 !mb-2"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={cn(
                        "relative rounded bg-muted px-[0.3rem] py-[0.2rem] font-mono text-sm",
                        className
                      )} {...props}>
                        {children}
                      </code>
                    )
                  },
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  ul: ({ children }) => <ul className="mb-2 last:mb-0 pl-4">{children}</ul>,
                  ol: ({ children }) => <ol className="mb-2 last:mb-0 pl-4">{children}</ol>,
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>

        {/* Message Actions */}
        <div className={cn(
          "flex items-center gap-1 mt-2 opacity-0 group-hover:opacity-100 transition-opacity",
          isUser ? "flex-row-reverse" : "flex-row"
        )}>
          <span className="text-xs text-muted-foreground">
            {formatTime(message.timestamp)}
          </span>
          
          {!isUser && (
            <div className="flex items-center gap-1 ml-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                className="h-6 w-6 p-0 hover:bg-muted"
              >
                <Copy className="h-3 w-3" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleFeedback('positive')}
                className="h-6 w-6 p-0 hover:bg-muted hover:text-green-600"
              >
                <ThumbsUp className="h-3 w-3" />
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleFeedback('negative')}
                className="h-6 w-6 p-0 hover:bg-muted hover:text-red-600"
              >
                <ThumbsDown className="h-3 w-3" />
              </Button>
              
              {isLast && onRegenerate && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onRegenerate}
                  className="h-6 w-6 p-0 hover:bg-muted hover:text-primary"
                >
                  <RotateCcw className="h-3 w-3" />
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Metadata (for AI messages) */}
        {!isUser && message.metadata && (
          <div className="mt-2 text-xs text-muted-foreground space-y-1">
            {message.metadata.confidence && (
              <div>Confidence: {Math.round(message.metadata.confidence * 100)}%</div>
            )}
            {message.metadata.processingTime && (
              <div>Response time: {message.metadata.processingTime}ms</div>
            )}
            {message.metadata.sources && message.metadata.sources.length > 0 && (
              <div>
                Sources: {message.metadata.sources.slice(0, 3).join(', ')}
                {message.metadata.sources.length > 3 && ` +${message.metadata.sources.length - 3} more`}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
}