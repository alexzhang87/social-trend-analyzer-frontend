'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { 
  ChevronDown, 
  ChevronUp, 
  Sparkles, 
  Brain, 
  TrendingUp, 
  DollarSign,
  Users,
  Lightbulb,
  BarChart3,
  Target
} from 'lucide-react'
import { ExpertPersona } from '@/types'
import { cn } from '@/lib/utils'

interface ExpertSelectorProps {
  experts: ExpertPersona[]
  selectedExpert: ExpertPersona | null
  onSelectExpert: (expert: ExpertPersona) => void
  className?: string
}

// Mock expert data with icons
const expertIcons = {
  'Business Strategy': TrendingUp,
  'Financial Planning': DollarSign,
  'Market Research': BarChart3,
  'Product Development': Lightbulb,
  'Marketing': Target,
  'Operations': Users,
  'Technology': Brain,
  'General': Sparkles
}

export function ExpertSelector({ 
  experts, 
  selectedExpert, 
  onSelectExpert, 
  className 
}: ExpertSelectorProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getExpertIcon = (expertise: string[]) => {
    const primaryExpertise = expertise[0] || 'General'
    const IconComponent = expertIcons[primaryExpertise as keyof typeof expertIcons] || Sparkles
    return IconComponent
  }

  const getPersonalityColor = (tone: string) => {
    switch (tone) {
      case 'professional': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
      case 'friendly': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
      case 'analytical': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300'
      case 'creative': return 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300'
    }
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Current Expert Display */}
      {selectedExpert && (
        <Card className="glass-card border-primary/20 bg-primary/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Avatar className="h-10 w-10 border-2 border-primary/20">
                <AvatarImage src={selectedExpert.avatar} alt={selectedExpert.name} />
                <AvatarFallback className="bg-primary/20 text-primary font-semibold">
                  {selectedExpert.name.charAt(0)}
                </AvatarFallback>
              </Avatar>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-sm truncate">{selectedExpert.name}</h3>
                  <Badge 
                    variant="secondary" 
                    className={getPersonalityColor(selectedExpert.personality.tone)}
                  >
                    {selectedExpert.personality.tone}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground truncate">
                  {selectedExpert.title}
                </p>
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="shrink-0"
              >
                {isExpanded ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Expert Selection Grid */}
      <AnimatePresence>
        {(isExpanded || !selectedExpert) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {experts.map((expert) => {
                const IconComponent = getExpertIcon(expert.expertise)
                const isSelected = selectedExpert?.id === expert.id
                
                return (
                  <motion.div
                    key={expert.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Card 
                      className={cn(
                        "cursor-pointer transition-all duration-200 hover:shadow-md hover:scale-[1.02]",
                        isSelected 
                          ? "border-primary bg-primary/5 shadow-md" 
                          : "border-border hover:border-primary/50"
                      )}
                      onClick={() => {
                        onSelectExpert(expert)
                        setIsExpanded(false)
                      }}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-start gap-3">
                          <div className={cn(
                            "p-2 rounded-lg transition-colors",
                            isSelected 
                              ? "bg-primary text-primary-foreground" 
                              : "bg-muted"
                          )}>
                            <IconComponent className="h-4 w-4" />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <CardTitle className="text-sm font-semibold truncate">
                              {expert.name}
                            </CardTitle>
                            <CardDescription className="text-xs truncate">
                              {expert.title}
                            </CardDescription>
                          </div>

                          <Avatar className="h-8 w-8 border">
                            <AvatarImage src={expert.avatar} alt={expert.name} />
                            <AvatarFallback className="text-xs">
                              {expert.name.charAt(0)}
                            </AvatarFallback>
                          </Avatar>
                        </div>
                      </CardHeader>

                      <CardContent className="pt-0 pb-3">
                        <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
                          {expert.description}
                        </p>

                        {/* Expertise Tags */}
                        <div className="flex flex-wrap gap-1 mb-3">
                          {expert.expertise.slice(0, 3).map((skill, index) => (
                            <Badge 
                              key={index} 
                              variant="outline" 
                              className="text-xs px-2 py-0"
                            >
                              {skill}
                            </Badge>
                          ))}
                          {expert.expertise.length > 3 && (
                            <Badge variant="outline" className="text-xs px-2 py-0">
                              +{expert.expertise.length - 3}
                            </Badge>
                          )}
                        </div>

                        {/* Personality Indicators */}
                        <div className="flex gap-1">
                          <Badge 
                            variant="secondary" 
                            className={cn(
                              "text-xs px-2 py-0",
                              getPersonalityColor(expert.personality.tone)
                            )}
                          >
                            {expert.personality.tone}
                          </Badge>
                          <Badge 
                            variant="outline" 
                            className="text-xs px-2 py-0"
                          >
                            {expert.personality.style}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Actions */}
      {selectedExpert && !isExpanded && (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsExpanded(true)}
            className="flex-1"
          >
            <Sparkles className="h-3 w-3 mr-1" />
            Switch Expert
          </Button>
        </div>
      )}
    </div>
  )
}