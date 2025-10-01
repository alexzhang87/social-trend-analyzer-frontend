'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { 
  Send, 
  Paperclip, 
  Mic, 
  MicOff, 
  Square, 
  Loader2,
  Sparkles,
  FileText,
  Image as ImageIcon
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChatInputProps {
  onSendMessage: (content: string, attachments?: File[]) => void
  isLoading?: boolean
  isTyping?: boolean
  placeholder?: string
  disabled?: boolean
  maxLength?: number
  showAttachments?: boolean
  showVoiceInput?: boolean
  className?: string
}

export function ChatInput({
  onSendMessage,
  isLoading = false,
  isTyping = false,
  placeholder = "Ask me anything about your startup idea...",
  disabled = false,
  maxLength = 4000,
  showAttachments = true,
  showVoiceInput = true,
  className
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [attachments, setAttachments] = useState<File[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const recordingIntervalRef = useRef<NodeJS.Timeout>()

  const canSend = message.trim().length > 0 && !isLoading && !disabled

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  // Recording timer
  useEffect(() => {
    if (isRecording) {
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } else {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }
      setRecordingTime(0)
    }

    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }
    }
  }, [isRecording])

  const handleSend = () => {
    if (!canSend) return
    
    onSendMessage(message.trim(), attachments.length > 0 ? attachments : undefined)
    setMessage('')
    setAttachments([])
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setAttachments(prev => [...prev, ...files])
    
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index))
  }

  const toggleRecording = () => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false)
      // Here you would handle the recorded audio
      console.log('Recording stopped')
    } else {
      // Start recording
      setIsRecording(true)
      console.log('Recording started')
    }
  }

  const formatRecordingTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Attachments Preview */}
      <AnimatePresence>
        {attachments.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex flex-wrap gap-2"
          >
            {attachments.map((file, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="flex items-center gap-2 bg-muted rounded-lg px-3 py-2 text-sm"
              >
                {file.type.startsWith('image/') ? (
                  <ImageIcon className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <FileText className="h-4 w-4 text-muted-foreground" />
                )}
                <span className="truncate max-w-[150px]">{file.name}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeAttachment(index)}
                  className="h-4 w-4 p-0 hover:bg-destructive hover:text-destructive-foreground"
                >
                  ×
                </Button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Recording Indicator */}
      <AnimatePresence>
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex items-center justify-center gap-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg p-3"
          >
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-red-700 dark:text-red-300">
                Recording: {formatRecordingTime(recordingTime)}
              </span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleRecording}
              className="border-red-200 hover:bg-red-100 dark:border-red-800 dark:hover:bg-red-900/20"
            >
              <Square className="h-3 w-3 mr-1" />
              Stop
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Input Area */}
      <Card className="glass-card border-border/50 hover:border-primary/30 transition-all duration-200">
        <div className="flex items-end gap-2 p-3">
          {/* Attachment Button */}
          {showAttachments && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled || isLoading}
              className="shrink-0 hover:bg-muted"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
          )}

          {/* Text Input */}
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isTyping ? "AI is typing..." : placeholder}
              disabled={disabled || isLoading || isTyping}
              maxLength={maxLength}
              className="min-h-[44px] max-h-[200px] resize-none border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 pr-12"
              rows={1}
            />
            
            {/* Character Count */}
            {message.length > maxLength * 0.8 && (
              <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                {message.length}/{maxLength}
              </div>
            )}
          </div>

          {/* Voice Input Button */}
          {showVoiceInput && (
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleRecording}
              disabled={disabled || isLoading}
              className={cn(
                "shrink-0 transition-all duration-200",
                isRecording 
                  ? "bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-950/20 dark:text-red-400" 
                  : "hover:bg-muted"
              )}
            >
              {isRecording ? (
                <MicOff className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </Button>
          )}

          {/* Send Button */}
          <Button
            onClick={handleSend}
            disabled={!canSend}
            size="icon"
            className={cn(
              "shrink-0 transition-all duration-300",
              canSend 
                ? "bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg hover:shadow-xl hover:scale-105" 
                : "bg-muted text-muted-foreground"
            )}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Typing Indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="border-t border-border/50 px-4 py-2"
            >
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Sparkles className="h-3 w-3 animate-pulse" />
                <span>AI is thinking...</span>
                <div className="flex gap-1">
                  <div className="h-1 w-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="h-1 w-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="h-1 w-1 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,.pdf,.doc,.docx,.txt"
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  )
}